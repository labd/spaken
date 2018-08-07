#!/usr/bin/env python
import os
import shutil
import tempfile
import time

import click
from pip._internal import main as pip_command

from spaken import __version__
from spaken.exceptions import StorageException
from spaken.finder import collect_filenames
from spaken.helpers import (
    get_storage_backend, parse_requirements, write_requirements)


class Command:

    def run(self, bucket_uri, destination, requirements, binary_packages=None):
        start_time = time.time()
        self.binary_packages = binary_packages

        if not os.path.exists(destination):
            os.makedirs(destination, mode=0o700, exist_ok=True)
        elif not os.path.isdir(destination):
            raise IOError("Destination is not a dir")

        packages, pip_arguments = parse_requirements(requirements)
        self._pip_arguments = pip_arguments

        self._destination = destination
        self._work_path = tempfile.mkdtemp()

        try:
            self._storage = get_storage_backend(bucket_uri)
        except StorageException as exc:
            click.secho(
                "Error connecting to the storage backend (%s)" % exc, fg='red')
            self._storage = None

        with tempfile.TemporaryDirectory() as tmp_path:
            self._temp_path = tmp_path

            if self._storage:
                missing_packages = self.download_wheel_files(packages)
            else:
                missing_packages = packages

            if missing_packages:
                self.download_sources(missing_packages)

                if self._storage:
                    self.upload_wheel_files()
                self.move_new_files_to_dest()

        duration = time.time() - start_time
        click.secho("\nAll done (%.2f seconds)  🚀\n" % duration, fg='green')

    def download_wheel_files(self, requirements):
        """Download pre-compiled packages from the wheel repository"""
        click.secho("Downloading pre-build wheel files", fg='green')

        filenames = self._storage.list_files()
        items, missing = collect_filenames(filenames, requirements)

        for item in items:
            target = os.path.join(self._destination, os.path.basename(item))
            if os.path.exists(target):
                click.echo(" - %s (already exists, skipping)" % item)
            else:
                click.echo(" - %s" % item)
                self._storage.get(item, target)
        return missing

    def download_sources(self, packages):
        """Download source packages from the pypi server and generate wheel
        files.

        """
        if not packages:
            return

        click.secho("Generating %d new wheel files" % len(packages), fg='green')

        tmp_reqfile = os.path.join(self._temp_path, 'requirements.txt')
        write_requirements(packages, self._pip_arguments, tmp_reqfile)

        binary_flags = []
        if self.binary_packages:
            binary_flags = ['--only-binary', self.binary_packages]

        pip_command([
            'wheel',
            '--requirement', tmp_reqfile,
            '--wheel-dir', self._temp_path,
            '--no-binary', ':all:'
        ] + binary_flags)

    def upload_wheel_files(self):
        """Upload all wheel files in the given path to the given bucket uri"""
        filenames = list(self._yield_new_files())
        click.secho("Uploading %d new wheel files" % len(filenames), fg='green')
        for local_path, filename in filenames:
            self._storage.upload(local_path, filename)

    def move_new_files_to_dest(self):
        for local_path, filename in self._yield_new_files():
            shutil.move(
                local_path, os.path.join(self._destination, filename))

    def _yield_new_files(self):
        filenames = [
            fn for fn in os.listdir(self._temp_path) if fn.endswith('.whl')
        ]

        if not filenames:
            return

        for filename in filenames:
            local_path = os.path.join(self._temp_path, filename)
            yield (local_path, filename)


@click.command()
@click.option('--bucket-uri', required=True)
@click.option('--dest', default='wheelhouse')
@click.option('--requirement', '-r', required=True)
@click.option('--binary-packages', type=str, default=None)
@click.version_option(version=__version__)
def main(bucket_uri, dest, requirement, binary_packages):
    cmd = Command()
    cmd.run(bucket_uri, dest, requirement, binary_packages)


if __name__ == '__main__':
    main()
