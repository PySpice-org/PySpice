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
import sys

from setuptools import setup, find_packages
setuptools_available = True

####################################################################################################

required_python_version = (3, 6)
if sys.version_info < required_python_version:
    sys.stderr.write('ERROR: PySpice requires Python {}.{}\n'.format(*required_python_version))
    sys.exit(1)

####################################################################################################

# Fixme: could check for ngspice, Xyce, libngspice.so etc.

# check a simulator is installed
# try:
#     rc = subprocess.check_call(('ngspice', '--version'), stdout=sys.stderr)
# except FileNotFoundError:
#     sys.stderr.write('\n\nWarning: You must install ngspice\n\n')

####################################################################################################

exec(compile(open('setup_data.py').read(), 'setup_data.py', 'exec'))

####################################################################################################

setup_dict.update(dict(
    # include_package_data=True, # Look in MANIFEST.in
    packages=find_packages(exclude=['unit-test']),
    scripts=glob.glob('bin/*'),
    # [
    #     'bin/...',
    # ],
    package_data={
        'PySpice.Config': ['logging.yml'],
        'PySpice.Spice.NgSpice': ['api.h'],
    },

    platforms='any',
    zip_safe=False, # due to data files

    classifiers=[
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Education',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        ],

    install_requires=[
        'PyYAML',
        'cffi',
        'matplotlib',
        'numpy',
        'ply',
        'scipy',
    ],
))

####################################################################################################

setup(**setup_dict)
