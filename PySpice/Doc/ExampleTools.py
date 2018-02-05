####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
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

####################################################################################################

import logging
import os
import sys

from PySpice.Tools.Path import parent_directory_of

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def find_libraries():

    try:
        library_path = os.environ['PySpiceLibraryPath']
    except KeyError:
        # Fixme: only works for one level
        python_file = os.path.abspath(sys.argv[0])
        examples_root = parent_directory_of(python_file, step=2)
        # .../PySpice/examples/diode/__example_rst_factory__nlrrr2fh.py .../PySpice/examples
        library_path = os.path.join(examples_root, 'libraries')

    _module_logger.info('SPICE library path is {}'.format(library_path))

    return library_path
