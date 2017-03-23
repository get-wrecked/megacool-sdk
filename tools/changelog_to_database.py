#!./venv/bin/python

import argparse
import datetime
import os
import psycopg2
import re

DATABASE = os.environ.get('DATABASE_URL', 'postgres://vagrant:vagrant@10.10.10.20/vagrant')
VERSION_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)((?:-)(\w+))?$')
HEADER_RE = re.compile(r'^(' + VERSION_RE.pattern[1:-1] + r') - (\d+-\d+-\d+)$')
SKIP_LINE_RE = re.compile(r'^[=-]+$')

class Release(object):

    def __init__(self, version, release_date, changes):
        self.version = version
        self.release_date = release_date
        self.changes = changes

    @property
    def version(self):
        label = '-%s' % self.version_label if self.version_label else ''
        return '%d.%d.%d%s' % (self.version_major, self.version_minor, self.version_patch,
            label)


    @version.setter
    def version(self, new_version):
        match = VERSION_RE.match(new_version)

        if not match:
            raise ValueError('Not a valid release version: %s' % new_version)

        self.version_major = int(match.group(1))
        self.version_minor = int(match.group(2))
        self.version_patch = int(match.group(3))
        self.version_label = match.group(5) or ''


    def download_url(self, platform):
        if platform == 'Unity':
            filename = 'Megacool.unitypackage'
        elif platform == 'iOS':
            filename = 'Megacool.framework.tar.gz'
        elif platform == 'Android':
            filename = 'Megacool.aar'
        else:
            raise ValueError('Invalid platform: %s' % platform)

        return 'https://megacool-files.s3-accelerate.amazonaws.com/v%s/%s' % (
            self.version, filename)


    def __str__(self):
        return 'Release(%s, %s)' % (self.version, self.release_date.strftime('%Y-%m-%d'))


    def to_db_tuple(self):
        return (
            self.version_major,
            self.version_minor,
            self.version_patch,
            self.version_label,
            self.download_url('Unity'),
            self.download_url('iOS'),
            self.download_url('Android'),
            self.release_date,
            self.changes,
        )


def main():
    args = get_args()
    releases = parse_changelog(args.changelog)
    insert_releases_to_database(releases)


def parse_changelog(changelog):
    releases = []
    has_first_header = False
    changes = []
    version = None
    release_date = None
    with open(changelog) as fh:
        for line in fh:
            line = line.rstrip()
            header_match = HEADER_RE.match(line)
            if header_match:
                if has_first_header:
                    releases.append(Release(version, release_date, '\n'.join(changes)))
                    changes = []
                has_first_header = True
                release_date = datetime.datetime.strptime(header_match.group(7), '%Y-%m-%d')
                version = header_match.group(1)
                continue

            if not has_first_header:
                continue

            skip_line_match = SKIP_LINE_RE.match(line)
            if skip_line_match:
                continue

            changes.append(line)
        releases.append(Release(version, release_date, '\n'.join(changes)))

    return releases


def insert_releases_to_database(releases):
    release_tuples = [release.to_db_tuple() for release in releases]
    query = '''
        insert into sdk_releases
            (version_major, version_minor, version_patch, version_label, download_url_unity,
             download_url_ios, download_url_android, released_at, changes)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        on conflict (version_major, version_minor, version_patch, version_label)
        do update set
            changes = excluded.changes,
            "updatedAt" = now()
        where sdk_releases.changes != excluded.changes
    '''
    connection = psycopg2.connect(DATABASE)
    with connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, release_tuples)
    connection.close()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('changelog')
    return parser.parse_args()


if __name__ == '__main__':
    main()
