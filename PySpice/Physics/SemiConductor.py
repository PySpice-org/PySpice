####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

""" This module provides semiconductor models.
"""

####################################################################################################

import numpy as np

####################################################################################################

import PySpice.Physics.PhysicalConstants as Cst

####################################################################################################

class ShockleyDiode(object):

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

####################################################################################################
# 
# End
# 
####################################################################################################
