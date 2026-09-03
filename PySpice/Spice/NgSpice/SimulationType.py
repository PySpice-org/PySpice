####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

__all__ = [
    'LAST_VERSION',
    'SIMULATION_TYPE',
]

####################################################################################################

# For a new ngspice relase, we just have to check this file hasn't changed
#   ngspice-xx/src/include/ngspice/sim.h vs local sim.h

SIMULATION_TYPE: dict[int | str, str] = {}

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

LAST_VERSION = 42   # released on 2023-12-27

for version in range(28, LAST_VERSION + 1):
    SIMULATION_TYPE[version] = SIMULATION_TYPE[27]

SIMULATION_TYPE['last'] = SIMULATION_TYPE[LAST_VERSION]
