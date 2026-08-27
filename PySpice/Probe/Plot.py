####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
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
