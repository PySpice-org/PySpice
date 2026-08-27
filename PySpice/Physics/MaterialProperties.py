# -*- coding: utf-8 -*-

####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

class Copper:

    atomic_number = 29

    atomic_mass = 63.546 * 1e-3 # kg
    density = 8.96 * 1e3 # kg·m−3
    thermal_conductivity = 401 # W·m−1·K−1
    electrical_resistivity = 16.78 * 1e-9 # Ω·m @20 °C
    electron_mobility = - 4.6 * 1e3 # m2·V−1·s−1

    ##############################################

    def electrical_resistance_for_conductor(self, degree):
        """ Used to compute conductor resistance. """
        rho0 = 16e-3 # Ω·m·mm−2
        return rho0 * (1 + .00393 * degree)
