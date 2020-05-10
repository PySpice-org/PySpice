####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2019 Fabrice Salvaire
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

__all__ = ['install_windows_dll']

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

from pathlib import Path
from zipfile import ZipFile
import tempfile

import requests

from . import NGSPICE_SUPPORTED_VERSION
#! NGSPICE_SUPPORTED_VERSION = 31

####################################################################################################

BASE_URL = 'https://sourceforge.net/projects/ngspice/files'
RELEASE_URL = BASE_URL + '/ng-spice-rework/'
WINDOWS_DLL_URL = RELEASE_URL + '/{0}/ngspice-{0}_dll_64.zip'

####################################################################################################

def donwload_file(url, dst_path):
    print('Get {} ... -> {}'.format(url, dst_path))
    response = requests.get(url, allow_redirects=True)
    assert(response.status_code == requests.codes.ok)
    with open(dst_path, mode='wb') as fh:
        fh.write(response.content)

####################################################################################################

def install_windows_dll():
    with tempfile.TemporaryDirectory() as tmp_directory:
        tmp_directory = Path(tmp_directory)
        url = WINDOWS_DLL_URL.format(NGSPICE_SUPPORTED_VERSION)
        zip_path = tmp_directory.joinpath('ngspice-{}_dll_64.zip'.format(NGSPICE_SUPPORTED_VERSION))
        dst_path = Path(__file__).parent
        donwload_file(url, zip_path)
        with ZipFile(zip_path) as zip_file:
            zip_file.extractall(path=dst_path)
        print('Extracted {} in {}'.format(zip_path, dst_path))
