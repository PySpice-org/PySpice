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

""" This module provides semiconductor models.
"""

####################################################################################################

import numpy as np

####################################################################################################

import PySpice.Physics.PhysicalConstants as Cst

####################################################################################################

class ShockleyDiode:

    """ This class provides an implementation of the Shockley Diode Model.
    """

    ##############################################

    def __init__(self,
                 Is=10e-12, # 10 pA
                 n=1,
                 degree=25, kelvin=None):

        self.Is = Is # reverse bias saturation current
        self.n = n # ideality factor or emission coefficient
        self.T = Cst.temperature(degree=degree, kelvin=kelvin)

    ##############################################

    @property
    def Vt(self):
        """ Thermal Voltage """
        return Cst.kT(kelvin=self.T) / Cst.q

    ##############################################

    def I(self, Vd):
        return self.Is*(np.exp(Vd/(self.n*self.Vt)) - 1)

    ##############################################

    def rd(self, Vd):
        """ Dynamic resistance defined by dVd/dI. """
        return self.n*self.Vt/self.I(Vd)
