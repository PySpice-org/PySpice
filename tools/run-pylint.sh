#! /bin/bash

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

for d in bin PySpice ; do
  for i in `find $d -name '*.py' | sort -n` ; do
    echo Check $i
    pylint --output-format=parseable --rcfile=pylintrc.ini --errors-only $i
  done
done

####################################################################################################
# 
# End
# 
####################################################################################################
