#!./venv/bin/python
# coding: utf-8

import argparse
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import textwrap
import zipfile
from collections import defaultdict, namedtuple
from contextlib import closing
from functools import total_ordering

import boto3
import jinja2
import requests

IOS_REPO = 'ssh://git@github.com/megacool/megacool-ios-sdk'
VERSION_RE = re.compile(r'^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([a-z0-9-]+))?$')


@total_ordering
class Version(namedtuple('Version', 'major minor patch label')):

    def __str__(self):
        label = '-%s' % self.label if self.label else ''
        return '%d.%d.%d%s' % (self[:3] + (label,))


    @property
    def release_branch(self):
        return '%d.%d.x' % (self.major, self.minor)


    @classmethod
    def from_string(cls, version_str):
        version_match = VERSION_RE.match(version_str)
        if not version_match:
            raise ValueError('Invalid version, must be formatted like 2.0.1 or 3.2.1-rc1')
        groups = [int(part) for part in version_match.groups()[:3]]
        label = version_match.group(4) or ''
        groups.append(label)
        return cls(*groups)


    def __lt__(self, other):
        # Intended ordering:
        # 1.0.0
        # 2.0.0-rc1
        # 2.0.0-rc2
        # 2.0.0
        self_versions = self[0:3]
        other_versions = other[0:3]
        if self_versions == other_versions:
            # All versions with labels are lesser than those without
            if self.label and other.label:
                return self.label < other.label
            elif self.label and not other.label:
                return True
            else:
                return False
        else:
            return self_versions < other_versions


    def __gt__(self, other):
        # We need to override this since namedtuple has some defaults that'll
        # mess up @total_ordering
        return self != other and not self < other


def main():
    args = get_args()
    release_spec = get_release_spec(args.version)
    ios_release = build_release_archive(args.version, release_spec)
    release_url = upload_release(args.version, ios_release)

    os.remove(ios_release)
    podspec = build_podspec(args.version, release_url)
    submit_pod(podspec)

    tag_source_commit(release_spec['commit'], args.version)
    git_push(tags=True)

    truncate_unreleased(args.version)
    git_push()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    args.version = Version.from_string(args.version)
    return args


def build_release_archive(version, release_spec):
    # First writes the intended archive contents to a directory, then packages that
    # directory as zip. Could easily be extended or modified to different formats if desired
    # (like tarballs), but keeping only zip for now since it works cross-platform and is
    # "easy" to build in a reproducible manner.
    # Note that while shutil.make_archive seems like it should be able to assist here, it
    # does not handle symlinks correctly, and does not create reproducible tarballs.
    print('Building template release')

    # Add meta files
    archive_dir = tempfile.mkdtemp()
    shutil.copy2('CHANGELOG.md', os.path.join(archive_dir, 'CHANGELOG.md'))
    for dist_file in os.listdir('dist-files'):
        file_path = os.path.join('dist-files', dist_file)
        shutil.copy2(file_path, os.path.join(archive_dir, dist_file))

    # Download and extract Megacool.framework
    framework = download_file(release_spec['iOS'])
    with tarfile.open(framework, mode='r:gz') as framework:
        framework.extractall(path=archive_dir)
    os.remove(framework.name)

    # Set a predictable mtime for all files in the source.
    release_timestamp = get_release_timestamp(version)
    for dirname, directories, filenames in os.walk(archive_dir):
        for item in directories + filenames:
            filepath = os.path.join(dirname, item)
            os.utime(filepath, (release_timestamp, release_timestamp), follow_symlinks=False)

    release_archive = create_zip_archive(archive_dir, release_timestamp)

    shutil.rmtree(archive_dir)

    return release_archive


def get_release_spec(version):
    repo_path = checkout_repository(version.release_branch)

    commitish = get_commitish(repo_path)

    cmd = [
        'git',
        '-C', repo_path,
        'notes',
        '--ref', 'artifacts',
        'show', commitish,
    ]
    artifact_notes = subprocess.check_output(cmd).decode('utf-8').strip()
    artifact_re = re.compile(r'^(?P<artifact>\w+)/(?P<detail>\w+):\s*(?P<content>.+)$')
    artifacts = defaultdict(dict)
    artifacts['commit'] = commitish
    for line in artifact_notes.split('\n'):
        line = line.strip()
        match = artifact_re.match(line)
        artifact, detail, content = match.groups()
        artifacts[artifact][detail] = content
    return artifacts


def get_commitish(repo_path):
    return subprocess.check_output([
        'git',
        '-C', repo_path,
        'rev-parse', 'HEAD',
    ]).decode('utf-8').strip()


def checkout_repository(branch):
    cached_repo_path = get_cached_repo_path()
    _checkout_repository(IOS_REPO, cached_repo_path, branch)
    return cached_repo_path


def get_cached_repo_path():
    return os.path.join(os.path.expanduser('~'), '.cache', 'megacool-sdk', 'ios')


def _checkout_repository(url, directory, branch):
    '''Idempotentially ensures the repo at the given url is checked out in the given directory at
    the given branch.
    '''
    if not os.path.exists(directory):
        clone_cmd = [
            'git',
            'clone', url,
            '--config', 'remote.origin.fetch=+refs/notes/*:refs/notes/*',
            directory,
        ]
        subprocess.check_call(clone_cmd)

    # TODO: When the bug that prevents the --config refspec from being used
    # on the initial clone[1] is fixed, the fetch can be put in an `else`
    # block to prevent an extra network hop.
    # [1]: http://public-inbox.org/git/robbat2-20170225T185056-448272755Z@orbis-terrarum.net/

    subprocess.check_call([
        'git',
        '-C', directory,
        'fetch',
        '--quiet',
    ])

    checkout_cmd = [
        'git',
        '-C', directory,
        'checkout', branch,
        '--quiet',
    ]
    subprocess.check_call(checkout_cmd)

    subprocess.check_call([
        'git',
        '-C', directory,
        'rebase', 'origin/%s' % branch,
        '--quiet',
    ])


def create_zip_archive(source_directory, release_timestamp):
    print('Building zip release')

    # Expand any symlinks in the source
    source_directory = os.path.realpath(source_directory)

    archive = tempfile.NamedTemporaryFile(delete=False)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as fh:
        for dirname, directories, filenames in os.walk(source_directory):
            directories.sort()
            for filename in sorted(filenames) + directories:
                # symlink detection and handling
                filepath = os.path.join(source_directory, dirname, filename)
                arcname = os.path.relpath(filepath, source_directory)
                mtime = datetime.datetime.fromtimestamp(release_timestamp).timetuple()[:6]
                info = zipfile.ZipInfo(arcname, mtime)
                info.external_attr = 0o644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                if os.path.isdir(filepath):
                    # make executable
                    info.external_attr |= 0o111 << 16
                if os.path.islink(filepath):
                    info.external_attr |= 0o120000 << 16 # make symlink

                    # strip common prefix from links to keep us within the archive
                    target = os.path.realpath(filepath)
                    prefix = os.path.commonprefix([filepath, target])
                    link_target = target[len(prefix):]

                    fh.writestr(info, link_target)
                elif os.path.isdir(filepath):
                    pass
                    info.filename += '/'
                    fh.writestr(info, b'')
                else:
                    # normal file
                    with open(filepath, 'rb') as source_fh:
                        # We assume we're never going to write any single file that'll
                        # have trouble fitting in memory
                        fh.writestr(info, source_fh.read())

    return archive.name


def upload_release(version, path):
    print('Uploading archive')
    s3 = boto3.resource('s3')
    s3_args = {
        'ContentType': 'application/zip',
        'ACL': 'public-read',
    }
    key = 'megacool-sdk-ios-v{version}.zip'.format(version=version)
    bucket = 'megacool-files'
    with open(path, 'rb') as fh:
        s3.Bucket(bucket).upload_fileobj(fh, key, ExtraArgs=s3_args)

    return 'https://{bucket}.s3-accelerate.amazonaws.com/{path}'.format(
        bucket=bucket, path=key)


def get_release_timestamp(version):
    version_re = re.compile(r'%s - (\d{4})-(\d{2})-(\d{2})$' % str(version))
    with open('CHANGELOG.md') as fh:
        for line in fh:
            match = version_re.match(line.strip())
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                # Since we release as zip we'll not use UTC since zip uses local times.
                return datetime.datetime(year, month, day).timestamp()
    raise ValueError('Version %s not found in changelog' % str(version))


def download_file(spec):
    hash_state = hashlib.sha256()
    destination = tempfile.NamedTemporaryFile(delete=False)
    with closing(requests.get(spec['url'], stream=True)) as response:
        response.raise_for_status()
        for chunk in iter(response.iter_content(64*2**10, b'')):
            destination.write(chunk)
            hash_state.update(chunk)
    destination.close()
    digest = hash_state.hexdigest()
    assert digest == spec['sha256']
    return destination.name


def build_podspec(version, release_url):
    return jinja2.Template(textwrap.dedent('''\
        Pod::Spec.new do |s|
            s.name = "Megacool"
            s.version = "{{ version }}"
            s.summary = "Viral growth solution with GIFs!"
            s.description = <<-DESCRIPTION
        Megacool is a viral growth solution that helps you spread
        user-generated GIFs and link them back to your app.

        Head over to [the documentation](https://docs.megacool.co/quickstart) to get started!
        DESCRIPTION

            s.homepage = "https://megacool.co"
            s.license = {
                :type => "Commercial",
                :file => "LICENSE.md"
            }
            s.authors = {
                "Nicolaj Broby Petersen" => "nicolaj@megacool.co",
                "Tarjei Husøy" => "tarjei@megacool.co"
            }
            s.social_media_url = "https://twitter.com/megacool_co"

            s.source = {
                :http => "{{ release_url }}"
            }
            s.documentation_url = "https://docs.megacool.co"
            s.platforms = {
                :ios => "7.0"
            }
            s.xcconfig = {
                "OTHER_LDFLAGS" => "$(inherited) -ObjC"
            }
            s.preserve_paths = [
                "LICENSE.md",
                "CHANGELOG.md",
                "Megacool.framework"
            ]
            s.libraries = "z"
            s.vendored_frameworks = "Megacool.framework"
            s.frameworks = [
                "Accounts",
                "CoreGraphics",
                "CoreMedia",
                "Foundation",
                "Security",
                "UIKit",
                "SafariServices",
                "Social",
            ]

        end
    ''')).render(
        version=str(version),
        release_url=release_url,
    ).encode('utf-8')


def submit_pod(podspec):
    build_dir = tempfile.mkdtemp()

    with open(os.path.join(build_dir, '.swift-version'), 'w') as fh:
        fh.write('2.3\n')

    with open(os.path.join(build_dir, 'Megacool.podspec'), 'wb') as fh:
        fh.write(podspec)

    try:
        subprocess.check_call(['pod', 'trunk', 'push', 'Megacool.podspec'], cwd=build_dir)
    finally:
        shutil.rmtree(build_dir)


def truncate_unreleased(version):
    repo_path = get_cached_repo_path()
    unreleased_path = os.path.join(repo_path, 'UNRELEASED.md')

    if os.stat(unreleased_path).st_size == 0:
        # No changes, ignore
        return

    with open(unreleased_path, 'w') as fh:
        fh.truncate()
    subprocess.check_call([
        'git',
        '-C', repo_path,
        'add', 'UNRELEASED.md',
    ])
    subprocess.check_call([
        'git',
        '-C', repo_path,
        'commit', '-m', 'Truncate UNRELEASED\n\nThese changes were released in %s' % str(version),
    ])


def tag_source_commit(commitish, version):
    repo_path = get_cached_repo_path()
    subprocess.check_call([
        'git',
        '-C', repo_path,
        'tag',
        '--message', 'Release v%s' % str(version),
        'v%s' % str(version),
        commitish,
    ])


def git_push(tags=False):
    repo_path = get_cached_repo_path()
    cmd = [
        'git',
        '-C', repo_path,
        'push',
    ]
    if tags:
        cmd.append('--tags')
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
