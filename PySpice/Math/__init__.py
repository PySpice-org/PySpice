####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

"""This module implements mathematical functions.
"""

####################################################################################################

import math

####################################################################################################

def odd(x):
    """Return True is *x* is odd"""
    return x & 1

def even(x):
    """Return True is *x* is even"""
    return not(odd(x))

####################################################################################################

def rms_to_amplitude(x):
    r"""Return :math:`x \sqrt{2}`"""
    return x * math.sqrt(2)

def amplitude_to_rms(x):
    r"""Return :math:`x / \sqrt{2}`"""
    return x / math.sqrt(2)
