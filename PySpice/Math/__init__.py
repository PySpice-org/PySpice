####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
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
