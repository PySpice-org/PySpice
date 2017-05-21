# -*- coding: utf-8 -*-

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
