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

####################################################################################################

from pathlib import Path
import logging
import os
import sys

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def find_libraries():
    try:
        library_path = os.environ['PySpiceLibraryPath']
    except KeyError:
        # Fixme: only works for one level
        python_file = Path(sys.argv[0]).resolve()
        examples_root = python_file.parents[1]
        # .../PySpice/examples/diode/__example_rst_factory__nlrrr2fh.py .../PySpice/examples
        library_path = os.path.join(examples_root, 'libraries')
    _module_logger.info('SPICE library path is {}'.format(library_path))
    return library_path
