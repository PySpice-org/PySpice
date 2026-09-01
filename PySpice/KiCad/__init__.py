####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'PythonDumper',
    'Spicedumper',
]

####################################################################################################

import logging
import os
from collections.abc import Callable
from typing import cast

try:
    from kicadrw.sexp.schema import KiCadSchema, Symbol
except ImportError:
    KiCadSchema = None  # ty: ignore[invalid-assignment]

####################################################################################################

_module_logger = logging.getLogger(__name__)

LINESEP = os.linesep

type ElementHandler = Callable[[PythonDumper, Symbol], str]

####################################################################################################

class BaseDumper:

    def generic_wrapper(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            return self.on_generic(element, symbol)
        return wrapper

    def generic_model_wrapper(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            return self.on_generic_model(element, symbol)
        return wrapper

    def source(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            return self.on_source(element, symbol)
        return wrapper

    GROUND = 0

    SYMBOL_MAP: dict[str, ElementHandler | int] = {
        'R': generic_wrapper('R'),
        'L': generic_wrapper('L'),
        'C': generic_wrapper('C'),
        'D': generic_model_wrapper('D'),
        'GND': GROUND,  # Fixme: typing is int
        'V': source('V'),
        # 'VDC': source('V'),
        # 'VPULSE': source('V'),
    }

    ##############################################

    def __init__(self, kicad_schema: KiCadSchema, use_pyspice_unit: bool = False) -> None:
        self._use_pyspice_unit = use_pyspice_unit
        self._code = []

        for symbol in kicad_schema.symbols_by_reference:
            self._logger.info(f"Symbol {symbol.lib_name} {symbol.reference} {symbol.simulation_device}")
            handler = self.find_symbol(symbol)
            match handler:
                case None:
                    self._logger.warning(f"any correspondance for '{symbol.lib_name}' '{symbol.reference}' '{symbol.simulation_device}'")
                case int():  # for ground i.e. != self.GROUND
                    pass
                case _:
                    _ = handler(self, symbol)
                    self._code.append(_)

    ##############################################

    def find_symbol(self, symbol: Symbol) -> ElementHandler | int | None:
        name = symbol.simulation_device
        if not name:
            _, name = symbol.lib_name.split(':')
        return self.SYMBOL_MAP.get(name, None)

    ##############################################

    def __str__(self) -> str:
        return LINESEP.join(self._code)

####################################################################################################

class SpiceDumper(BaseDumper):

    _logger = _module_logger.getChild('SpiceDumper')

    ##############################################

    def _pins(self, symbol: Symbol) -> list[int | str]:
        pins: list[int | str] = []
        for pin in symbol.pins:
            _id = cast(int | str, pin.inet.id)  # Fixme: due to None...
            # if _id == 0:
            #     _id = 'GND'
            pins.append(_id)
        return pins

    ##############################################

    def _unit_value(self, element: str, symbol: Symbol) -> str:
        return symbol.value

    ##############################################

    def _str_args(self, raw_args: list[str | int | float]) -> str:
        args = []
        for arg in raw_args:
            # if isinstance(arg, str) and ('@' in arg or arg.startswith('circuit.')):
            #     pass
            if isinstance(arg, (int, float)):
                arg = str(arg)
            args.append(arg)
        return ' '.join(args)

    ##############################################

    def on_generic(self, element: str, symbol: Symbol) -> str:
        self._logger.info(f"Element '{symbol.reference}' params='{symbol.simulation_paramaters}'")
        reference = symbol.reference[len(element):]
        value = self._unit_value(element, symbol)
        args = [reference, *self._pins(symbol), value]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"{element}{args_str}"

    ##############################################

    def on_generic_model(self, element: str, symbol: Symbol) -> str:
        self._logger.info(f"Element with model '{symbol.reference}' pins='{symbol.simulation_pins}' params='{symbol.simulation_paramaters}'")
        # Fixme: check XD
        reference = symbol.reference[len(element):]   # +1
        # pin_names = [_.name for _ in symbol.pins]
        pins = self._pins(symbol)
        # match pin_names:
        #     case ('K', 'A'):
        #         pins = list(reversed(pins))
        args = [reference, *pins]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        model_name = f'__{symbol.value}{reference}'
        lines = [
            f".model {model_name} {element} {symbol.simulation_paramaters}",
            f"{element}{args_str} {model_name}",
        ]
        # Fixme: __str__ join
        return LINESEP.join(lines)

    ##############################################

    def on_source(self, element: str, symbol: Symbol) -> str:
        self._logger.info(f"Source '{symbol.simulation_device}' type='{symbol.simulation_type}' params='{symbol.simulation_paramaters}'")
        reference = symbol.reference[len(element):]
        args = [reference, *self._pins(symbol)]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"{element}{args_str} {symbol.simulation_type}( {symbol.simulation_paramaters} )"

####################################################################################################

class PythonDumper:

    _logger = _module_logger.getChild('PythonDumper')

    def generic_wrapper(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            return self.on_generic(element, symbol)
        return wrapper

    def generic_model_wrapper(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            return self.on_generic_model(element, symbol)
        return wrapper

    def source(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            return self.on_source(element, symbol)
        return wrapper

    GROUND = 0

    # SYMBOL_MAP = {
    #     'Device:C': generic_wrapper('C'),
    #     'Device:R': generic_wrapper('R'),
    #     'Simulation_SPICE:D':  generic_model_wrapper('D'),
    #     'power:GND': GROUND,
    #     'spice-ngspice:0': GROUND,
    #     'spice-ngspice:C': generic_wrapper('C'),
    #     'spice-ngspice:CHOKE': None,
    #     'spice-ngspice:CURRENT_MEASURE': None,
    #     'spice-ngspice:Csmall': generic_wrapper('C'),
    #     'spice-ngspice:DIODE':  generic_model_wrapper('D'),
    #     'spice-ngspice:INDUCTOR': generic_wrapper('L'),
    #     'spice-ngspice:ISOURCE': generic_wrapper('I'),
    #     'spice-ngspice:ISRC_ICTL': None,
    #     'spice-ngspice:ISRC_VCTL': None,
    #     'spice-ngspice:NMOS': None,
    #     'spice-ngspice:OPAMP': None,
    #     'spice-ngspice:PMOS': None,
    #     'spice-ngspice:QNPN': None,
    #     'spice-ngspice:QPNP': None,
    #     'spice-ngspice:R': generic_wrapper('R'),
    #     'spice-ngspice:Rsmall': generic_wrapper('R'),
    #     'spice-ngspice:SWITCH': None,
    #     'spice-ngspice:TOGGLE': None,
    #     'spice-ngspice:VSOURCE': generic_wrapper('V'),
    #     'spice-ngspice:VSRC_ICTL': None,
    #     'spice-ngspice:VSRC_VCTL': None,
    #     'spice-ngspice:Vsrc': generic_wrapper('V'),
    #     'spice-ngspice:ZENOR': None,
    # }

    SYMBOL_MAP: dict[str, ElementHandler | int] = {
        'R': generic_wrapper('R'),
        'L': generic_wrapper('L'),
        'C': generic_wrapper('C'),
        'D': generic_model_wrapper('D'),
        'GND': GROUND,  # Fixme: typing is int
        'V': source('V'),
        # 'VDC': source('V'),
        # 'VPULSE': source('V'),
    }

    ##############################################

    def __init__(self, kicad_schema: KiCadSchema, use_pyspice_unit: bool = False) -> None:
        self._use_pyspice_unit = use_pyspice_unit
        self._code = []

        for symbol in kicad_schema.symbols_by_reference:
            self._logger.info(f"Symbol {symbol.lib_name} {symbol.reference} {symbol.simulation_device}")
            handler = self.find_symbol(symbol)
            match handler:
                case None:
                    self._logger.warning(f"any correspondance for '{symbol.lib_name}' '{symbol.reference}' '{symbol.simulation_device}'")
                case int():  # for ground i.e. != self.GROUND
                    pass
                case _:
                    _ = handler(self, symbol)
                    self._code.append(_)

    ##############################################

    def find_symbol(self, symbol: Symbol) -> ElementHandler | int | None:
        name = symbol.simulation_device
        if not name:
            _, name = symbol.lib_name.split(':')
        return self.SYMBOL_MAP.get(name, None)

    ##############################################

    def __str__(self) -> str:
        return LINESEP.join(self._code)

    ##############################################

    def _pins(self, symbol: Symbol) -> list[int | str]:
        pins: list[int | str] = []
        for pin in symbol.pins:
            _id = cast(int | str, pin.inet.id)  # Fixme: due to None...
            if _id == 0:
                _id = 'circuit.gnd'
            pins.append(_id)
        return pins

    ##############################################

    def _unit_value(self, element: str, symbol: Symbol) -> str:
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

    def _str_args(self, raw_args: list[str | int | float]) -> str:
        args = []
        for arg in raw_args:
            if isinstance(arg, str) and ('@' in arg or arg.startswith('circuit.')):
                pass
            elif isinstance(arg, (int, float)):
                arg = str(arg)
            elif isinstance(arg, (str)):
                arg = "'" + arg + "'"
                # arg = '"' + arg + '"'
            args.append(arg)
        return ', '.join(args)

    ##############################################

    def on_generic(self, element: str, symbol: Symbol) -> str:
        self._logger.info(f"Element {symbol.reference} {symbol.simulation_paramaters}")
        reference = symbol.reference[len(element):]
        value = self._unit_value(element, symbol)
        args = [reference, *self._pins(symbol), value]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"circuit.{element}({args_str})"

    ##############################################

    def on_generic_model(self, element: str, symbol: Symbol) -> str:
        self._logger.info(f"Element with model {symbol.reference} {symbol.simulation_pins} {symbol.simulation_paramaters}")
        # Fixme: check XD
        reference = symbol.reference[len(element):]   # +1
        pin_names = [_.name for _ in symbol.pins]
        pins = self._pins(symbol)
        match pin_names:
            case ('K', 'A'):
                pins = list(reversed(pins))
        args = [reference, *pins]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"circuit.{element}({args_str}, model='{symbol.value}')"

    ##############################################

    def on_source(self, element: str, symbol: Symbol) -> str:
        self._logger.info(f"Source {symbol.simulation_device} {symbol.simulation_type} {symbol.simulation_paramaters}")
        reference = symbol.reference[len(element):]
        match symbol.simulation_type.upper():
            case 'PULSE':
                element = 'PulseVoltageSource'
        args = [reference, *self._pins(symbol)]
        params = ''
        if symbol.simulation_paramaters:
            sep = ', '
            params = sep.join(symbol.simulation_paramaters.split(' '))
        else:
            value = self._unit_value(element, symbol)
            if symbol.reference[0] in ('V',):
                value += '@u_V'
            args.append(value)
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        if params:
            params = sep + params
        return f"circuit.{element}({args_str}{params})"
