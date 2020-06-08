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
from zipfile import ZipFile
import argparse
import os
import shutil
import sys
import tempfile

import requests

####################################################################################################

# Archive:  resources/ngspice-31_dll_64.zip
#   Spice64_dll/dll-mingw/
#   Spice64_dll/dll-mingw/libgcc_s_seh-1.dll
#   Spice64_dll/dll-mingw/libgomp-1.dll
#   Spice64_dll/dll-mingw/libwinpthread-1.dll
#   Spice64_dll/dll-mingw/msys-ngspice-0.dll
#   Spice64_dll/dll-vs/
#   Spice64_dll/dll-vs/ngspice.dll
#   Spice64_dll/dll-vs/vcomp140.dll
#   Spice64_dll/include/
#   Spice64_dll/include/ngspice/
#   Spice64_dll/include/ngspice/sharedspice.h
#   Spice64_dll/lib/
#   Spice64_dll/lib/about-libs.txt
#   Spice64_dll/lib/lib-mingw/
#   Spice64_dll/lib/lib-mingw/libngspice.dll.a
#   Spice64_dll/lib/lib-mingw/libngspice.la
#   Spice64_dll/lib/lib-vs/
#   Spice64_dll/lib/lib-vs/ngspice.exp
#   Spice64_dll/lib/lib-vs/ngspice.lib
#   Spice64_dll/lib/ngspice/
#   Spice64_dll/lib/ngspice/analog.cm
#   Spice64_dll/lib/ngspice/digital.cm
#   Spice64_dll/lib/ngspice/spice2poly.cm
#   Spice64_dll/lib/ngspice/table.cm
#   Spice64_dll/lib/ngspice/xtradev.cm
#   Spice64_dll/lib/ngspice/xtraevt.cm
#   Spice64_dll/share/
#   Spice64_dll/share/ngspice/
#   Spice64_dll/share/ngspice/scripts/
#   Spice64_dll/share/ngspice/scripts/spinit

####################################################################################################

class PySpicePostInstallation:

    GITHUB_URL = 'https://github.com/FabriceSalvaire/PySpice'

    NGSPICE_BASE_URL = 'https://sourceforge.net/projects/ngspice/files'
    NGSPICE_RELEASE_URL = NGSPICE_BASE_URL + '/ng-spice-rework'
    NGSPICE_WINDOWS_DLL_URL = NGSPICE_RELEASE_URL + '/{0}/ngspice-{0}_dll_64.zip'
    NGSPICE_MANUAL_URL = NGSPICE_RELEASE_URL + '/{0}/ngspice-{0}-manual.pdf/download'

    ##############################################

    def run(self):

        parser = argparse.ArgumentParser(description='Tool to perform PySpice Post Installation.')

        parser.add_argument(
            '--ngspice-version',
            type=int, default=None,
            help='NgSpice version to install',
        )

        parser.add_argument(
            '--install-ngspice-dll',
            action='store_true',
            help='install Windows DLL',
        )

        parser.add_argument(
            '--force-install-ngspice-dll',
            action='store_true',
            help='force DLL installation (for debug only)',
        )

        parser.add_argument(
            '--download-ngspice-manual',
            action='store_true',
            help='download Ngspice manual',
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

        count = 0
        if self._args.install_ngspice_dll:
            self.install_ngspice_dll()
            count += 1

        if self._args.check_install:
            self.check_installation()
            count += 1

        if self._args.download_example:
            self.download_example()
            count += 1

        if self._args.download_ngspice_manual:
            self.download_ngspice_manual()
            count += 1

        if not count:
            parser.print_help()

    ##############################################

    def _donwload_file(self, url, dst_path):
        print('Get {} ... -> {}'.format(url, dst_path))
        response = requests.get(url, allow_redirects=True)
        assert(response.status_code == requests.codes.ok)
        with open(dst_path, mode='wb') as fh:
            fh.write(response.content)

    ##############################################

    @property
    def ngspice_version(self):
        if not hasattr(self, '_ngspice_version'):
            version = self._args.ngspice_version
            if version is None:
                from PySpice.Spice.NgSpice import NGSPICE_SUPPORTED_VERSION
                version = NGSPICE_SUPPORTED_VERSION
            self._ngspice_version = version
        return self._ngspice_version

    ##############################################

    def install_ngspice_dll(self):

        if not(os.name == 'nt' or self._args.force_install_ngspice_dll):
            return

        from PySpice.Spice import NgSpice

        with tempfile.TemporaryDirectory() as tmp_directory:
            tmp_directory = Path(tmp_directory)
            url = self.NGSPICE_WINDOWS_DLL_URL.format(self.ngspice_version)
            zip_path = tmp_directory.joinpath('ngspice-{}_dll_64.zip'.format(self.ngspice_version))
            dst_path = Path(NgSpice.__file__).parent
            self._donwload_file(url, zip_path)
            with ZipFile(zip_path) as zip_file:
                zip_file.extractall(path=dst_path)
            print('Extracted {} in {}'.format(zip_path, dst_path))

    ##############################################

    def download_ngspice_manual(self):
        url = self.NGSPICE_MANUAL_URL.format(self.ngspice_version)
        self._donwload_file(url, 'ngspice-manual-{}.pdf'.format(self.ngspice_version))

    ##############################################

    def check_installation(self):

        """Tool to check PySpice is correctly installed.

        """

        import ctypes.util

        print('OS:', sys.platform)
        print()

        print('Environments:')
        for _ in (
                'PATH',
                'LD_LIBRARY_PATH',
                'NGSPICE_LIBRARY_PATH',
                'SPICE_LIB_DIR',
                'SPICE_EXEC_DIR',
                'SPICE_ASCIIRAWFILE',
                'SPICE_SCRIPTS',
                'NGSPICE_MEAS_PRECISION',
                'SPICE_NO_DATASEG_CHECK',
                'NGSPICE_INPUT_DIR',
        ):
            print(_, os.environ.get(_, 'undefined'))
        print()

        try:
            print('Load PySpice module')
            import PySpice
            print('loaded {} version {}'.format(PySpice.__file__, PySpice.__version__))
            print()
        except ModuleNotFoundError:
            print('PySpice module not found')
            return

        import PySpice.Logging.Logging as Logging
        logger = Logging.setup_logging(logging_level='INFO')

        from PySpice.Config import ConfigInstall
        from PySpice.Spice import NgSpice
        from PySpice.Spice.NgSpice import NGSPICE_SUPPORTED_VERSION
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared

        print('ngspice supported version:', NGSPICE_SUPPORTED_VERSION)
        print()

        ##############################################

        message = os.linesep.join((
            'NgSpiceShared configuration is',
            '  NgSpiceShared.NGSPICE_PATH = {0.NGSPICE_PATH}',
            '  NgSpiceShared.LIBRARY_PATH = {0.LIBRARY_PATH}',
        ))
        print(message.format(NgSpiceShared))
        print()

        ##############################################

        cwd = Path(os.curdir).resolve()
        print('Working directory:', cwd)
        print()

        locale_ngspice = cwd.joinpath('ngspice-{}'.format(NGSPICE_SUPPORTED_VERSION))
        if locale_ngspice.exists() and locale_ngspice.is_dir():
            print('Found local ngspice:')
            for root, _, filenames in os.walk(locale_ngspice):
                for filename in filenames:
                    print(root, filename)
            print()


        ngspice_module_path = Path(NgSpice.__file__).parent
        print('NgSpice:', ngspice_module_path)
        for root, _, filenames in os.walk(ngspice_module_path):
            for filename in filenames:
                print(root, filename)
        print()

        ##############################################

        if ConfigInstall.OS.on_windows:
            print('OS is Windows')
            library = NgSpiceShared.LIBRARY_PATH
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
        print()

        if ngspice.spinit_not_found:
            print('WARNING: spinit was not found')
            print()

        message = os.linesep.join((
            'Ngspice version is {0.ngspice_version}',
            '  has xspice: {0.has_xspice}',
            '  has cider {0.has_cider}',
        ))
        print(message.format(ngspice))
        print()

        command = 'version -f'
        print('> ' + command)
        print(ngspice.exec_command(command))
        print()

        print('PySpice should work as expected')

    ##############################################

    def download_example(self):

        import PySpice
        version = PySpice.__version__

        RELEASE_URL = self.GITHUB_URL + '/archive/v{}.zip'.format(version)

        zip_path = 'examples.zip'

        dst_path = input("Enter the path where you want to extract examples: ")
        dst_path = Path(dst_path).resolve()
        dst_parent = dst_path.parent
        if not dst_parent.exists():
            print("Directory {} doesn't exists".format(dst_parent))
            return

        with tempfile.TemporaryDirectory() as tmp_directory:
            self._donwload_file(RELEASE_URL, zip_path)
            with ZipFile(zip_path) as zip_file:
                zip_file.extractall(path=tmp_directory)
            examples_path = Path(tmp_directory).joinpath('PySpice-{}'.format(version), 'examples')
            shutil.copytree(examples_path, dst_path)
            print('Extracted examples in {}'.format(dst_path))

####################################################################################################

def main():
    _ = PySpicePostInstallation()
    return _.run()
