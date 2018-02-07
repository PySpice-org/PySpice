####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

def to_absolute_path(path):

    # Expand ~ . and Remove trailing '/'

    return os.path.abspath(os.path.expanduser(path))

####################################################################################################

def parent_directory_of(file_name, step=1):

    directory = file_name
    for i in range(step):
        directory = os.path.dirname(directory)
    return directory

####################################################################################################

def find(file_name, directories):

    if isinstance(directories, bytes):
        directories = (directories,)
    for directory in directories:
        for directory_path, sub_directories, file_names in os.walk(directory):
            if file_name in file_names:
                return os.path.join(directory_path, file_name)

    raise NameError("File %s not found in directories %s" % (file_name, str(directories)))
