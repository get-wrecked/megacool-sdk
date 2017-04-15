#!./venv/bin/python
# coding: utf-8

import argparse
import datetime
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import textwrap
import zipfile
from contextlib import closing

import boto3
import jinja2
import requests


def main():
    args = get_args()
    ios_release = build_release_archive(args.version)
    release_url = upload_release(args.version, ios_release)
    os.remove(ios_release)
    podspec = build_podspec(args.version, release_url)
    submit_pod(podspec)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    return parser.parse_args()


def build_release_archive(version):
    # First writes the intended archive contents to a directory, then packages that
    # directory as zip. Could easily be extended or modified to different formats if desired
    # (like tarballs), but keeping only zip for now since it works cross-platform and is
    # "easy" to build in a reproducible manner.
    # Note that while shutil.make_archive seems like it should be able to assist here, it
    # does not handle symlinks correctly, and does not create reproducible tarballs.
    print('Building template release')
    license = textwrap.dedent('''\
        All text and design is copyright © 2017 Megacool Inc.
        All rights reserved. Terms of use as defined at https://megacool.co/terms applies.
    ''').encode('utf-8')
    readme = textwrap.dedent('''\
        Megacool SDK
        ============

        Megacool is a viral growth solution that helps you spread
        user-generated GIFs and link them back to your app.

        Head over to [the documentation](https://docs.megacool.co/quickstart) to get started!
    ''').encode('utf-8')

    # Add meta files
    archive_dir = tempfile.mkdtemp()
    with open(os.path.join(archive_dir, 'LICENSE.md'), 'wb') as fh:
        fh.write(license)
    with open(os.path.join(archive_dir, 'README.md'), 'wb') as fh:
        fh.write(readme)
    shutil.copy2('CHANGELOG.md', os.path.join(archive_dir, 'CHANGELOG.md'))

    # Download and extract Megacool.framework
    # TODO: Get this from a git note in the ios sdk repo
    framework_url = 'https://megacool-files.s3-accelerate.amazonaws.com/v{version}/Megacool.framework.tar.gz'.format(
        version=version)
    framework = download_file(framework_url)
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
    version_re = re.compile(r'%s - (\d{4})-(\d{2})-(\d{2})$' % version)
    with open('CHANGELOG.md') as fh:
        for line in fh:
            match = version_re.match(line.strip())
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                # Since we release as zip we'll not use UTC since zip uses local times.
                return datetime.datetime(year, month, day).timestamp()


def download_file(url):
    destination = tempfile.NamedTemporaryFile(delete=False)
    with closing(requests.get(url, stream=True)) as response:
        response.raise_for_status()
        for chunk in iter(response.iter_content(64*2**10, b'')):
            destination.write(chunk)
    destination.close()
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
            s.social_media_url = "https://twitter.com/bemegacool"

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
        version=version,
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


if __name__ == '__main__':
    main()
