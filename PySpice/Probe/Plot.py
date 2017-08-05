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

# Fixme: versus PySpice.Plot ???

####################################################################################################

"""This module implements plotting helper."""

####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

def plot(waveform, *args, **kwargs):

    """Plot a waveform using the current Axes instance or the one specified by the *axis* key
    argument. Additional parameters are passed to the Matplotlib plot function.

    """

    axis = kwargs.get('axis', plt.gca())
    if 'axis' in kwargs:
        del kwargs['axis']
    axis.plot(waveform.abscissa, waveform, *args, **kwargs)
