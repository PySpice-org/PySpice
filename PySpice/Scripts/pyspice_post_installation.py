####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Tool to perform post installation.

"""

####################################################################################################

from pathlib import Path
import argparse
import os

####################################################################################################

class PySpicePostInstallation:

    ##############################################

    def __init__(self):

        parser = argparse.ArgumentParser(description='Tool to perform PySpice Post Installation.')

        parser.add_argument(
            '--install-ngspsice-dll',
            action='store_true',
            help='install Windows DLL',
        )

        parser.add_argument(
            '--force-install-ngspice-dll',
            action='store_true',
            help='force DLL installation (for debug only)',
        )

        parser.add_argument(
            '--ngspice-version',
            type=int, default=None,
            help='NgSpice version to install',
        )

        parser.add_argument(
            '--check-install',
            action='store_true',
            help='check installation',
        )

        parser.add_argument(
            '--download-example',
            action='store_true',
            help='download examples',
        )

        self._args = parser.parse_args()

        if self._args.install_ngspice_dll:
            self.install_ngspice_dll()
        if self._args.check_install:
            self.check_installation()
        if self._args.download_example:
            self.download_example()

    ##############################################

    def install_ngspice_dll(self):

        if os.name == 'nt' or self._args.force_install_ngspice_dll:
            from PySpice.Spice.NgSpice.Installer import install_windows_dll
            install_windows_dll(self._args.ngspice_version)

    ##############################################

    def check_installation(self):

        """Tool to check PySpice is correctly installed.

        """

        import ctypes.util

        try:
            print('Load PySpice module')
            import PySpice
            print('loaded {} version {}'.format(PySpice.__file__, PySpice.__version__))
        except ModuleNotFoundError:
            print('PySpice module not found')
            return

        import PySpice.Logging.Logging as Logging
        logger = Logging.setup_logging(logging_level='INFO')

        from PySpice.Config import ConfigInstall
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared

        ##############################################

        message = '''
        NgSpiceShared configuration is
          NgSpiceShared.NGSPICE_PATH = {0.NGSPICE_PATH}
          NgSpiceShared.LIBRARY_PATH = {0.LIBRARY_PATH}
        '''
        print(message.format(NgSpiceShared))

        ##############################################

        if ConfigInstall.OS.on_windows:
            print('OS is Windows')
            library = NGSPICE_PATH.LIBRARY_PATH
        elif ConfigInstall.OS.on_osx:
            print('OS is OSX')
            library = 'ngspice'
        elif ConfigInstall.OS.on_linux:
            print('OS is Linux')
            library = 'ngspice'
        else:
            raise NotImplementedError

        library_path = ctypes.util.find_library(library)
        print('Found in library search path: {}'.format(library_path))

        ##############################################

        print('\nLoad NgSpiceShared')
        ngspice = NgSpiceShared(verbose=True)

        if ConfigInstall.OS.on_linux:
            # For Linux see DLOPEN(3)
            # Apparently there is no simple way to get the path of the loaded library ...
            # But we can look in the process maps
            pid = os.getpid()
            maps_path = '/proc/{}/maps'.format(pid)
            with open(maps_path) as fh:
                for line in fh:
                    if '.so' in line and 'ngspice' in line:
                        parts = [x for x in line.split() if x]
                        path = parts[-1]
                        print('loaded {}'.format(path))
                        break

        message = '''
        Ngspice version is {0.ngspice_version}
          has xspice: {0.has_xspice}
          has cider {0.has_cider}
        '''
        print(message.format(ngspice))

        command = 'version -f'
        print('> ' + command)
        print(ngspice.exec_command(command))

        print()
        print('PySpice should work as expected')

    ##############################################

    def download_example(self):

        import shutil
        import tempfile
        from zipfile import ZipFile
        import PySpice
        from PySpice.Spice.NgSpice.Installer import donwload_file

        version = PySpice.__version__

        GITHUB_URL = 'https://github.com/FabriceSalvaire/PySpice'
        RELEASE_URL = GITHUB_URL + '/archive/v{}.zip'.format(version)
        zip_path = 'examples.zip'

        dst_path = input("Enter the path where you want to extract examples: ")
        dst_path = Path(dst_path).resolve()
        dst_parent = dst_path.parent
        if not dst_parent.exists():
            print("Directory {} doesn't exists".format(dst_parent))
            return

        with tempfile.TemporaryDirectory() as tmp_directory:
            donwload_file(RELEASE_URL, zip_path)
            with ZipFile(zip_path) as zip_file:
                zip_file.extractall(path=tmp_directory)
            examples_path = Path(tmp_directory).joinpath('PySpice-{}'.format(version), 'examples')
            shutil.copytree(examples_path, dst_path)
            print('Extracted examples in {}'.format(dst_path))

####################################################################################################

def main():
    _ = PySpicePostInstallation()
