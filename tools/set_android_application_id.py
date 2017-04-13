#!/usr/bin/env python
"""
Fix the Megacool unitypackage for Unity versions that either don't use Gradle
or use Unity < 5.5.

Basically hardcodes the `${applicationId}` used in gradle projects with your
application id since the package is not compatible with Unity's internal
packaging system or the legacy ADT system.

The input can also be a normal Android .aar.
"""

# Internals:
# .unitypackage files are compressed tarballs. Each entry in the tarball is a
# directory with two or three files: `asset` (optional), `asset.meta` and
# `pathname`. `pathname` contains the name the `asset` will get when unpacked
# by Unity.
#
# One of the files in the unitypackage is the Megacool Android library, as an
# .aar file. .aar's are zipfiles, and the Manifest is located at the root. We
# unpack the unitypackage, locate the android .aar, unpack it, modify the
# manifest, then re-zip the .aar and finally re-tar the unitypackage.

from __future__ import unicode_literals

import argparse
import os
import shutil
import tarfile
import tempfile
import zipfile


def main():
    args = get_args()

    is_unitypackage = not zipfile.is_zipfile(args.input)

    if is_unitypackage:
        unpacked_unitypackage = unpack_unitypackage(args.input)
        megacool_aar = find_megacool_aar(unpacked_unitypackage)
    else:
        megacool_aar = args.input

    unpacked_aar = unpack_aar(megacool_aar)

    modify_manifest(unpacked_aar, args.application_id)

    repack_aar(unpacked_aar, megacool_aar)

    if is_unitypackage:
        repack_unitypackage(unpacked_unitypackage, args.input)
        shutil.rmtree(unpacked_unitypackage)

    shutil.rmtree(unpacked_aar)

    print('Success! \U0001F596')


def unpack_unitypackage(unitypackage):
    target_dir = tempfile.mkdtemp()
    with tarfile.open(unitypackage, 'r:gz') as package:
        package.extractall(target_dir)
    return target_dir


def find_megacool_aar(unpacked_unitypackage):
    for guid in os.listdir(unpacked_unitypackage):
        path_file = os.path.join(unpacked_unitypackage, guid, 'pathname')
        with open(path_file) as fh:
            path = fh.read().strip()
        if path == 'Assets/Megacool/Plugins/Android/megacool-unity.aar':
            return os.path.join(unpacked_unitypackage, guid, 'asset')


def unpack_aar(aar):
    unpack_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(aar) as aar_zip_fh:
        aar_zip_fh.extractall(unpack_dir)
    return unpack_dir


def modify_manifest(unpacked_aar, application_id):
    manifest_path = os.path.join(unpacked_aar, 'AndroidManifest.xml')
    with open(manifest_path) as fh:
        manifest = fh.read()
    with open(manifest_path, 'w') as fh:
        fh.write(manifest.replace(r'${applicationId}', application_id))


def repack_aar(unpacked_aar, destination):
    with zipfile.ZipFile(destination, mode='w') as fh:
        for dirpath, directories, filenames in os.walk(unpacked_aar):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                archive_name = os.path.relpath(filepath, unpacked_aar)
                fh.write(filepath, archive_name)


def repack_unitypackage(unpacked_unitypackage, destination):
    temp_destination = tempfile.NamedTemporaryFile(delete=False)
    with tarfile.open(fileobj=temp_destination, mode='w:gz') as package:
        for guid in os.listdir(unpacked_unitypackage):
            package.add(os.path.join(unpacked_unitypackage, guid), arcname=guid)
    os.rename(temp_destination.name, destination)


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',
        help='Path to the unity package or Android .aar to modify')
    parser.add_argument('application_id',
        help='The application id to set in the new package')
    return parser.parse_args()


if __name__ == '__main__':
    main()
