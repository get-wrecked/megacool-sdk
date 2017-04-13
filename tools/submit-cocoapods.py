#!./venv/bin/python
# coding: utf-8

from __future__ import unicode_literals

import argparse
import os
import shutil
import StringIO
import subprocess
import tarfile
import tempfile
import textwrap
import time
import zipfile
from contextlib import closing

import boto3
import jinja2
import requests


def main():
    args = get_args()
    ios_release = build_release_archive(args.version)
    release_url = upload_release(args.version, ios_release)
    podspec = build_podspec(args.version, release_url)
    submit_pod(podspec)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    return parser.parse_args()


def build_release_archive(version):
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
    archive = tempfile.NamedTemporaryFile(delete=False)
    with zipfile.ZipFile(archive, 'w') as fh:
        add_file_to_archive(fh, 'megacool/LICENSE.md', license)
        add_file_to_archive(fh, 'megacool/README.md', readme)
        fh.write('CHANGELOG.md', arcname='megacool/CHANGELOG.md')
        # TODO: Get this from a git note in the ios sdk repo
        framework_url = 'https://megacool-files.s3-accelerate.amazonaws.com/v{version}/Megacool.framework.tar.gz'.format(
            version=version)
        framework = download_file(framework_url)
        framework_unpacked = tempfile.mkdtemp()
        with tarfile.open(framework, mode='r:gz') as framework:
            framework.extractall(path=framework_unpacked)
        for dirname, directories, filenames in os.walk(framework_unpacked):
            for filename in filenames:
                filepath = os.path.join(framework_unpacked, dirname, filename)
                arcname = os.path.join('megacool', os.path.relpath(filepath, framework_unpacked))
                fh.write(filepath, arcname=arcname)

    return archive.name


def upload_release(version, path):
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


def add_file_to_archive(archive, path, contents):
    info = zipfile.ZipInfo(path, time.gmtime()[:6])
    archive.writestr(info, contents)


def download_file(url):
    destination = tempfile.NamedTemporaryFile(delete=False)
    with closing(requests.get(url, stream=True)) as response:
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
                "FRAMEWORK_SEARCH_PATHS" => "\\"$(PODS_ROOT)/Megacool/**\\"",
                "OTHER_LDFLAGS" => "$(inherited) -ObjC"
            }

            s.source_files = "Megacool.framework/Versions/A/Headers/*.h"
            s.preserve_paths = ["LICENSE.md", "Megacool.framework"]
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

    with open(os.path.join(build_dir, 'Megacool.podspec'), 'w') as fh:
        fh.write(podspec)

    try:
        subprocess.check_call(['pod', 'trunk', 'push', 'Megacool.podspec'], cwd=build_dir)
    finally:
        shutil.rmtree(build_dir)


if __name__ == '__main__':
    main()
