####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = ['find_libraries', 'LIBRARY_PATH']

####################################################################################################

from pathlib import Path
import logging
import os
import sys

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

LIBRARY_PATH = 'spice-library'

def find_libraries(root: str='examples') -> Path:
    try:
        library_path = os.environ['PySpiceLibraryPath']
    except KeyError:
        examples_root = Path(sys.argv[0]).resolve()   # path of the Python file
        while True:
            examples_root = examples_root.parents[1]
            if examples_root.name == root:
                break
        library_path = examples_root.joinpath(LIBRARY_PATH)
    _module_logger.info(f'SPICE library path is {library_path}')
    return library_path
