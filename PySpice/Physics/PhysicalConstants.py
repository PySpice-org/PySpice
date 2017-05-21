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
#
# Physical Constants from Particle Data Group 2013
#   http://pdg.lbl.gov/2013/reviews/rpp2013-rev-phys-constants.pdf
#
####################################################################################################

####################################################################################################

pi = 3.141592653589793238 # π = 3.141 592 653 589 793 238

####################################################################################################

speed_of_light_in_vacuum = c = 299792458 # 299 792 458 m s−1
electron_charge_magnitude = e = q = 1.602176565e-19 # 1.602 176 565(35)×10−19 C = 4.803 204 50(11)×10−10 esu

permeability_of_free_space = mu0 = 4*pi*1e-7 # 4π × 10−7 N A−2 = 12.566 370 614 ... ×10−7 N A−2
permittivity_of_free_space = epsilon0 = 1./(mu0*c**2) # 8.854 187 817 ... ×10−12 F m −1

avogadro_constant = Na = 6.02214129e23 # 6.022 141 29(27)×1023 mol−1
boltzmann_constant = k = 1.3806488e-23 # 1.380 6488(13)×10−23 J K−1 = 8.617 3324(78)×10−5 eV K−1

# 1 eV = 1.602 176 565(35) × 10−19 J
# 1 eV/c2 = 1.782 661 845(39) × 10−36 kg

####################################################################################################

# 0 ◦C ≡ 273.15 K
def degree_to_kelvin(x):
    return x + 273.15
def kelvin_to_degree(x):
    return x - 273.15

def temperature(degree=None, kelvin=None):
    if degree is not None:
        return degree_to_kelvin(degree)
    else:
        return kelvin

# kT at 300 K = [38.681 731(35)]−1 eV
def kT(degree=None, kelvin=None):
    return k*temperature(degree=degree, kelvin=kelvin)
