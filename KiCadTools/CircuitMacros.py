####################################################################################################
#
# KiCadTools - Python Tools for KiCad
# Copyright (C) 2021 Fabrice Salvaire
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

__all__ = [
    'CircuitMacrosDumper',
]

####################################################################################################

"""This dumper outputs a draft for Circuit_Macros.

"""

####################################################################################################

import os

####################################################################################################

class CircuitMacrosDumper:

    def generic_wrapper(element):
        def wrapper(self, symbol):
            return self.on_generic(element, symbol)
        return wrapper

    SYMBOL_MAP = {
        'spice-ngspice:0': None,
        'spice-ngspice:C': generic_wrapper('capacitor'),
        'spice-ngspice:CHOKE': None,
        'spice-ngspice:CURRENT_MEASURE': None,
        'spice-ngspice:Csmall': generic_wrapper('capacitor'),
        'spice-ngspice:DIODE':  generic_wrapper('diode'),
        'spice-ngspice:INDUCTOR': generic_wrapper('inductor'),
        'spice-ngspice:ISOURCE': None,
        'spice-ngspice:ISRC_ICTL': None,
        'spice-ngspice:ISRC_VCTL': None,
        'spice-ngspice:NMOS': None,
        'spice-ngspice:OPAMP': None,
        'spice-ngspice:PMOS': None,
        'spice-ngspice:QNPN': None,
        'spice-ngspice:QPNP': None,
        'spice-ngspice:R': generic_wrapper('resistor'),
        'spice-ngspice:Rsmall': generic_wrapper('resistor'),
        'spice-ngspice:SWITCH': None,
        'spice-ngspice:TOGGLE': None,
        'spice-ngspice:VSOURCE': generic_wrapper('source'),
        'spice-ngspice:VSRC_ICTL': None,
        'spice-ngspice:VSRC_VCTL': None,
        'spice-ngspice:Vsrc': generic_wrapper('source'),
        'spice-ngspice:ZENOR': None,
    }

    HEADER = """.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3

define(`bigdiode',
  `resized(2., `diode', $1)')

define(`bigzenerdiode',
  `resized(2., `reversed', `diode', $1, S)')

FOO: Here
  dot; "FOO" below;
  line right_ elen; dot;
  line right_ elen then down epsilon; "FOO" above;
  {
  }

"""

    FOOTER = """

.PE
"""

    ##############################################

    def __init__(self, kicad_schema):

        self._code = []
        for symbol in kicad_schema.symbols_by_position:
            handler = self.SYMBOL_MAP.get(symbol.lib_name, None)
            if handler is not None:
                _ = handler(self, symbol)
                self._code.append(_)

    ##############################################

    def __str__(self):
        return self.HEADER + os.linesep.join(self._code) + self.FOOTER

    ##############################################

    def on_generic(self, element, symbol):

        reference = symbol.reference

        angle = symbol.angle
        direction = '_'
        if element in ('capacitor', 'resistor', 'source'):
            if angle == 0:
                direction = 'up_'
            elif angle == 90:
                direction = 'right_'
            elif angle == 180:
                direction = 'down_'
            elif angle == 270:
                direction = 'left_'
        elif element in ('diode', 'zenerdiode'):
            if reference.startswith('X'):
                reference = reference[1:]
            if angle == 0:
                direction = 'right_'
            elif angle == 90:
                direction = 'down_'
            elif angle == 180:
                direction = 'left_'
            elif angle == 270:
                direction = 'up_'

        reference = f"{reference[0]}_{{{reference[1:]}}}"

        return f"  {element}({direction} elen); llabel(,{reference},); dot;"
