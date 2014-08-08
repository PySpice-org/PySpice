####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) 2014 Salvaire Fabrice
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

import os

####################################################################################################

def merge_include(lines, doc_path):
    for line_index, line in enumerate(lines):
        if line.startswith('.. include::'):
            include_file_name = line.split('::')[-1].strip()
            with open(os.path.join(doc_path, include_file_name)) as f:
                include_lines = f.readlines()
            lines[line_index] = remove_include(include_lines)
    return ''.join(lines)

def remove_include(lines):
    for line_index, line in enumerate(lines):
        if line.startswith('.. include::'):
            lines[line_index] = ''
    return ''.join(lines)

####################################################################################################

# Utility function to read the README file.
# Used for the long_description.
def read(file_name):

    source_path = os.path.dirname(os.path.realpath(__file__))
    if os.path.basename(source_path) == 'tools':
        source_path = os.path.dirname(source_path)
    elif 'build/bdist' in source_path:
        source_path = source_path[:source_path.find('build/bdist')]
    absolut_file_name = os.path.join(source_path, file_name)
    doc_path = os.path.join(source_path, 'doc', 'sphinx', 'source')

    # Read and merge includes
    with open(absolut_file_name) as f:
        lines = f.readlines()
    text = merge_include(lines, doc_path)

    return text

####################################################################################################

setup_dict = dict(
    name='PySpice',
    version='0.1.0',
    author='Fabrice Salvaire',
    author_email='fabrice.salvaire@orange.fr',
    description='PySpice is a Python Package to generate and steer Berkeley Spice circuit, '
    ' to simulate them and finally analyse the output using Python.',
    license="GPLv3",
    keywords="spice, berkeley, ngspice, circuit, simulation, electronic",
    url='https://github.com/FabriceSalvaire/PySpice',
    scripts=[],
    packages=['PySpice'],
    data_files = [],
    long_description=read('README.txt'),
    # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Education",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        ],
    # install_requires=[
    #     # 'numpy',
    #     # 'matplotlib',
    #     ],
    )

####################################################################################################
#
# End
#
####################################################################################################
