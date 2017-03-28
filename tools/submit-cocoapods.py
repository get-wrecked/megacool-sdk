#!./venv/bin/python
# coding: utf-8

from __future__ import unicode_literals

import argparse
import os
import shutil
import textwrap
import tempfile
import subprocess

import jinja2


def main():
    args = get_args()
    podspec = build_podspec(args.version)
    print(podspec)
    submit_pod(podspec)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    return parser.parse_args()


def build_podspec(version):
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
                :file => "megacool/LICENSE.md"
            }
            s.authors = {
                "Nicolaj Broby Petersen" => "nicolaj@megacool.co",
                "Tarjei Husøy" => "tarjei@megacool.co"
            }
            s.social_media_url = "https://twitter.com/bemegacool"

            s.source = {
                :http => "https://megacool-files.s3-accelerate.amazonaws.com/v2.1.2/megacool-sdk-ios-2.1.2.tgz"
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
    ''')).render(version=version).encode('utf-8')


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
