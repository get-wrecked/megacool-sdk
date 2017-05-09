#!./venv/bin/python
# coding: utf-8

import argparse
import datetime
import hashlib
import io
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from functools import total_ordering
from collections import defaultdict, namedtuple

import boto3

VERSION_RE = re.compile(r'^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([a-z0-9-]+))?$')
HEADER_RE = re.compile(r'^(' + VERSION_RE.pattern[1:-1] + r') - (\d+-\d+-\d+)$')
SKIP_LINE_RE = re.compile(r'^[=-]+$')
ANDROID_REPO = 'ssh://git@github.com/megacool/megacool-android-sdk'
MAVEN_BUCKET = 'megacool-maven-repo'
MANIFEST_KEY = 'releases/co/megacool/megacool/maven-metadata.xml'

s3 = boto3.resource('s3')


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


def main():
    args = get_args()
    print('Fetching release spec')
    release_spec = get_release_spec(args.version)
    print('Got spec, downloading artifact')
    downloaded = download_artifact(release_spec['Maven'])
    unpacked_artifact = unpack_artifact(downloaded)

    print('Downloading manifest')
    current_manifest = get_manifest()
    new_manifest = set_version_in_manifest(current_manifest, args.version)

    print('Uploading release')
    upload_maven_release(unpacked_artifact)
    print('Uploading new manifest')
    upload_maven_manifest(new_manifest)

    # cleanup
    os.remove(downloaded)
    shutil.rmtree(unpacked_artifact)
    print('Success! \U0001F596')


def get_release_spec(version):
    repo_path = checkout_repository(version.release_branch)

    cmd = [
        'git',
        '-C', repo_path,
        'notes',
        '--ref', 'artifacts',
        'show', 'HEAD',
    ]
    artifact_notes = subprocess.check_output(cmd).decode('utf-8').strip()
    artifact_re = re.compile(r'^(?P<artifact>\w+)/(?P<detail>\w+):\s*(?P<content>.+)$')
    artifacts = defaultdict(dict)
    for line in artifact_notes.split('\n'):
        line = line.strip()
        match = artifact_re.match(line)
        artifact, detail, content = match.groups()
        artifacts[artifact][detail] = content
    return artifacts


def download_artifact(details):
    return download_file_with_checksum(details['url'], details['sha256'])


def unpack_artifact(artifact_path):
    unpacked_path = tempfile.mkdtemp()
    with tarfile.open(artifact_path, mode='r:xz') as framework:
        framework.extractall(path=unpacked_path)
    return unpacked_path


def get_manifest():
    s3_object = s3.Object(MAVEN_BUCKET, MANIFEST_KEY)
    return s3_object.get()['Body'].read().decode('utf-8')


def set_version_in_manifest(string_manifest, version):
    manifest = ET.fromstring(string_manifest.encode('utf-8'))
    version_str = str(version)
    versioning = manifest.findall('versioning')[0]

    # Set the new version as the newest release
    release = versioning.findall('release')[0]
    existing_release_version = Version.from_string(release.text)
    if version > existing_release_version:
        release.text = version_str
    else:
        print('Existing release is newer (%s), not updating release in manifest' %
            str(existing_release_version))

    # Add it to the release list
    versions = versioning.findall('versions')[0]
    for version_node in versions.findall('version'):
        if version_node.text == version_str:
            print('Already released this version, not adding version to manifest')
            break
    else:
        version_node = ET.SubElement(versions, 'version')
        version_node.text = version_str

    # Update lastUpdated
    last_updated = versioning.findall('lastUpdated')[0]
    last_updated.text = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

    prettify(manifest)

    memory_xml = io.StringIO()
    ET.ElementTree(manifest).write(memory_xml, xml_declaration=True, encoding='unicode')
    return memory_xml.getvalue()


def upload_maven_release(unpacked_path):
    for dirname, directories, filenames in os.walk(unpacked_path):
        for filename in filenames:
            filepath = os.path.join(dirname, filename)
            key = os.path.relpath(filepath, unpacked_path)
            s3.Object(MAVEN_BUCKET, key).upload_file(filepath,
                ExtraArgs={'ACL': 'public-read'})


def upload_maven_manifest(manifest):
    public_extra_args = {'ACL': 'public-read'}
    manifest_bytes = manifest.encode('utf-8')
    fileobj = io.BytesIO(manifest_bytes)
    s3.Object(MAVEN_BUCKET, MANIFEST_KEY).upload_fileobj(fileobj,
        ExtraArgs=public_extra_args)

    for digest_method in ('md5', 'sha1'):
        digest = getattr(hashlib, digest_method)(manifest_bytes).hexdigest()
        digest_fileobj = io.BytesIO(digest.encode('utf-8'))
        digest_key = '%s.%s' % (MANIFEST_KEY, digest_method)
        s3.Object(MAVEN_BUCKET, digest_key).upload_fileobj(digest_fileobj,
            ExtraArgs=public_extra_args)


def prettify(element, indent='  '):
    # Creds to http://stackoverflow.com/a/38573964/5590192 for this
    queue = [(0, element)]  # (level, element)
    while queue:
        level, element = queue.pop(0)
        children = [(level + 1, child) for child in list(element)]
        if children:
            element.text = '\n' + indent * (level+1)  # for child open
        if queue:
            element.tail = '\n' + indent * queue[0][0]  # for sibling open
        else:
            element.tail = '\n' + indent * (level-1)  # for parent close
        queue[0:0] = children  # prepend so children come before siblings


def download_file_with_checksum(url, checksum):
    parsed_url = urllib.parse.urlparse(url)
    bucket_name = parsed_url.netloc.split('.', 1)[0]
    key = parsed_url.path[1:]
    destination = tempfile.NamedTemporaryFile(delete=False)
    s3_object = s3.Object(bucket_name, key)
    s3_object.download_fileobj(destination)

    hash_state = hashlib.sha256()
    with open(destination.name, 'rb') as fh:
        for chunk in iter(lambda: fh.read(32*2**10), b''):
            hash_state.update(chunk)

    received_checksum = hash_state.hexdigest()
    assert received_checksum == checksum, 'Received file did not match expected checksum!'
    return destination.name


def checkout_repository(branch):
    cached_repo_path = get_cached_repo_path()
    _checkout_repository(ANDROID_REPO, cached_repo_path, branch)
    return cached_repo_path


def get_cached_repo_path():
    return os.path.join(os.path.expanduser('~'), '.cache', 'megacool-sdk', 'android')


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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')

    args = parser.parse_args()

    args.version = Version.from_string(args.version)

    return args


if __name__ == '__main__':
    main()
