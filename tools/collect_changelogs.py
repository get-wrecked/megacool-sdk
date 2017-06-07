#!./venv/bin/python

import argparse
import datetime
import os
import re
import subprocess
import sys
from collections import namedtuple

VERSION_RE = re.compile(r'^([0-9]+)\.([0-9]+)\.([0-9]+)(-[a-z0-9-]+)?$')
REPOSITORIES = {
    'iOS': 'ssh://git@github.com/megacool/megacool-ios-sdk',
    'Unity': 'ssh://git@github.com/megacool/megacool-ios-unity-wrapper',
    'Android': 'ssh://git@github.com/megacool/megacool-android-sdk',
}


class Version(namedtuple('Version', 'major minor patch label')):

    def __str__(self):
        label = '-%s' % self.label if self.label else ''
        return '%d.%d.%d%s' % self

    @property
    def release_branch(self):
        return '%d.%d.x' % (self.major, self.minor)


def main():
    args = parse_args()
    checkout_repositories(args.version.release_branch)
    collect_changelogs(args.version)


def checkout_repositories(branch):
    sdk_versions = set()
    for name, repo_url in REPOSITORIES.items():
        cached_repo_path = get_cached_repo_path(name)
        checkout_repository(repo_url, cached_repo_path, branch)
        repo_sdk_version = get_repo_sdk_version(cached_repo_path)
        if repo_sdk_version:
            # Only core repositories define the version, not wrappers
            sdk_versions.add(repo_sdk_version)
    if len(sdk_versions) != 1:
        raise ValueError('SDK repos does not agree on SDK version, found %s' %
            ' and '.join(sdk_versions))



def collect_changelogs(version):
    with open('CHANGELOG.md') as fh:
        changelog_lines = fh.readlines()
    changelog_header = ''.join(changelog_lines[:5])
    existing_changelog = ''.join(changelog_lines[5:])

    new_changelog = []
    for name, repo_url in REPOSITORIES.items():
        cached_repo_path = get_cached_repo_path(name)
        changelog = get_changelog_from_repo(cached_repo_path)
        if changelog:
            new_changelog.append('>>>> %s changes: <<<<\n%s' % (name, changelog))
            print('%s changelog: \n%s' % (name, changelog))

    datestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    version_header = '%s - %s' % (str(version), datestamp)

    with open('CHANGELOG.md', 'w') as fh:
        fh.write(changelog_header)
        fh.write('%s\n%s\n\n' % (version_header, '='*len(version_header)))
        fh.write('\n'.join(new_changelog))
        fh.write('\n\n')
        fh.write(existing_changelog)


def get_cached_repo_path(repo_name):
    return os.path.join(os.path.expanduser('~'), '.cache', 'megacool-sdk', repo_name.lower())


def get_changelog_from_repo(repo_path):
    with open(os.path.join(repo_path, 'UNRELEASED.md')) as fh:
        return fh.read()


def checkout_repository(url, directory, branch):
    '''Idempotentially ensures the repo at the given url is checked out in the given directory at
    the given branch.
    '''
    if not os.path.exists(directory):
        clone_cmd = [
            'git',
            'clone', url,
            directory,
        ]
        subprocess.check_call(clone_cmd)
    else:
        subprocess.check_call([
            'git',
            '-C', directory,
            'fetch', '--all',
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
    ])


def get_repo_sdk_version(repo_path):
    # This script exists in all of our core SDK repos by convention, but not in wrappers
    get_version_script = os.path.join(repo_path, 'tools', 'get-version.sh')

    try:
        version_bytes = subprocess.check_output([get_version_script], cwd=repo_path)
    except FileNotFoundError:
        return None
    return version_bytes.decode('utf-8').strip()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    version_match = VERSION_RE.match(args.version)
    if not version_match:
        sys.stderr.write('Invalid version, must be formatted like 2.0.1 or 3.2.1-rc1')
        sys.exit(1)
    groups = [int(part) for part in version_match.groups()[:3]]
    label = version_match.group(4) or ''
    groups.append(label)
    args.version = Version(*groups)

    return args


if __name__ == '__main__':
    main()
