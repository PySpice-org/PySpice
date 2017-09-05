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

import os

####################################################################################################

from ..Unit.Unit import UnitValue

####################################################################################################

def str_spice(obj):

    """Convert an object to a Spice compatible string."""

    if isinstance(obj, UnitValue):
        return obj.str_spice()
    else:
        return str(obj)

####################################################################################################

def join_lines(items, prefix=''):
    return os.linesep.join([prefix + str(item) for item in items if item is not None])

####################################################################################################

def join_list(items):
    return ' '.join([str_spice(item) for item in items if item is not None])

####################################################################################################

def join_dict(d):
    return ' '.join(["{}={}".format(key, str_spice(value)) for key, value in d.items() if value is not None])
