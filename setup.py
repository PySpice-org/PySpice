#! /usr/bin/env python3

####################################################################################################
#
# PySpice - A Spice package for Python
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

import glob
import os
import sys

from setuptools import setup, find_packages

####################################################################################################

required_python_version = (3, 6)
if sys.version_info < required_python_version:
    sys.stderr.write('ERROR: PySpice requires Python {}.{}\n'.format(*required_python_version))
    sys.exit(1)

####################################################################################################

# ported from py2 execfile
# exec(compile(open('setup_data.py').read(), 'setup_data.py', 'exec'))
from setup_data import setup_dict

####################################################################################################

# Fixme: could check for ngspice, Xyce, libngspice.so etc.

# check a simulator is installed
# try:
#     rc = subprocess.check_call(('ngspice', '--version'), stdout=sys.stderr)
# except FileNotFoundError:
#     sys.stderr.write('\n\nWarning: You must install ngspice\n\n')

####################################################################################################

install_requires = []

if os.name == 'nt':
    install_requires += [
        'requests', # requests==2.23.0
    ]

####################################################################################################

setup_dict.update(dict(
    install_requires=install_requires,
))

####################################################################################################

setup(**setup_dict)
