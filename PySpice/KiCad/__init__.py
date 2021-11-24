####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = [
    'PythonDumper',
]

####################################################################################################

import os

# from KiCadTools.Schema import KiCadSchema

####################################################################################################

class PythonDumper:

    def generic_wrapper(element):
        def wrapper(self, symbol):
            return self.on_generic(element, symbol)
        return wrapper

    def generic_model_wrapper(element):
        def wrapper(self, symbol):
            return self.on_generic_model(element, symbol)
        return wrapper

    SYMBOL_MAP = {
        'spice-ngspice:0': None,
        'spice-ngspice:C': generic_wrapper('C'),
        'spice-ngspice:CHOKE': None,
        'spice-ngspice:CURRENT_MEASURE': None,
        'spice-ngspice:Csmall': generic_wrapper('C'),
        'spice-ngspice:DIODE':  generic_model_wrapper('D'),
        'spice-ngspice:INDUCTOR': generic_wrapper('L'),
        'spice-ngspice:ISOURCE': generic_wrapper('I'),
        'spice-ngspice:ISRC_ICTL': None,
        'spice-ngspice:ISRC_VCTL': None,
        'spice-ngspice:NMOS': None,
        'spice-ngspice:OPAMP': None,
        'spice-ngspice:PMOS': None,
        'spice-ngspice:QNPN': None,
        'spice-ngspice:QPNP': None,
        'spice-ngspice:R': generic_wrapper('R'),
        'spice-ngspice:Rsmall': generic_wrapper('R'),
        'spice-ngspice:SWITCH': None,
        'spice-ngspice:TOGGLE': None,
        'spice-ngspice:VSOURCE': generic_wrapper('V'),
        'spice-ngspice:VSRC_ICTL': None,
        'spice-ngspice:VSRC_VCTL': None,
        'spice-ngspice:Vsrc': generic_wrapper('V'),
        'spice-ngspice:ZENOR': None,
    }

    ##############################################

    def __init__(self, kicad_schema, use_pyspice_unit=False):

        self._use_pyspice_unit = use_pyspice_unit
        self._code = []

        for symbol in kicad_schema.symbols_by_reference:
            handler = self.SYMBOL_MAP.get(symbol.lib_name, None)
            if handler is not None:
                _ = handler(self, symbol)
                self._code.append(_)

    ##############################################

    def __str__(self):
        return os.linesep.join(self._code)

    ##############################################

    def _pins(self, symbol):
        pins = []
        for pin in symbol.pins:
            _id = pin.net_id.id
            if _id == 0:
                _id = 'circuit.gnd'
            pins.append(_id)
        return pins

    ##############################################

    def _unit_value(self, element, symbol):
        value = symbol.value
        if not self._use_pyspice_unit:
            return value
        power = value[-1]
        # Fixme: complete...
        #  Meg
        if element == 'R':
            unit = 'Ω'
        elif element == 'C':
            unit = 'F'
        if power in 'pnumk':
            value = value[:-1]
            value = f"{value}@u_{power}{unit}"
        return value

    ##############################################

    def _str_args(self, raw_args):
        args = []
        for arg in raw_args:
            if isinstance(arg, str) and ('@' in arg or arg.startswith('circuit.')):
                pass
            elif isinstance(arg, (int, float)):
                arg = str(arg)
            elif isinstance(arg, (str)):
                # arg = "'" + arg + "'"
                arg = '"' + arg + '"'
            args.append(arg)
        return ', '.join(args)

    ##############################################

    def on_generic(self, element, symbol):
        reference = symbol.reference[len(element):]
        value = self._unit_value(element, symbol)
        args = [reference, *self._pins(symbol), value]
        args_str = self._str_args(args)
        return f"circuit.{element}({args_str})"

    ##############################################

    def on_generic_model(self, element, symbol):
        # Fixme: check XD
        reference = symbol.reference[len(element)+1:]
        args = [reference, symbol.value, *self._pins(symbol)]
        args_str = self._str_args(args)
        return f"circuit.{element}({args_str})"
