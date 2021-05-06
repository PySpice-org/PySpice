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

__all__ = [
    'LAST_VERSION',
    'SIMULATION_TYPE',
]

####################################################################################################

# For a new ngspice relase, we just have to check this file hasn't changed
#   ngspice-xx/src/include/ngspice/sim.h

SIMULATION_TYPE = {}

SIMULATION_TYPE[26] = (
    'no_type',
    'time',
    'frequency',
    'voltage',
    'current',
    'output_n_dens',
    'output_noise',
    'input_n_dens',
    'input_noise',
    'pole',
    'zero',
    's_parameter',
    'temperature',
    'res',
    'impedance',
    'admittance',
    'power',
    'phase',
    'db',
    'capacitance',
    'charge',
)

SIMULATION_TYPE[27] = (
    'no_type',
    'time',
    'frequency',
    'voltage',
    'current',
    'voltage_density',
    'current_density',
    'sqr_voltage_density',
    'sqr_current_density',
    'sqr_voltage',
    'sqr_current',
    'pole',
    'zero',
    's_parameter',
    'temperature',
    'res',
    'impedance',
    'admittance',
    'power',
    'phase',
    'db',
    'capacitance',
    'charge',
)

LAST_VERSION = 34   # released on January 31st, 2021

for version in range(28, LAST_VERSION +1):
    SIMULATION_TYPE[version] = SIMULATION_TYPE[27]

SIMULATION_TYPE['last'] = SIMULATION_TYPE[LAST_VERSION]
