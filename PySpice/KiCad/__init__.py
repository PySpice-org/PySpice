####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'PythonDumper',
    'SpiceDumper',
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

type ElementHandler = Callable[[BaseDumper, Symbol], str | list[str]]

####################################################################################################

class BaseDumper:

    _logger = _module_logger.getChild('BaseDumper')

    def generic_wrapper(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            self.on_generic_log(element, symbol)
            return self.on_generic(element, symbol)
        return wrapper

    def generic_model_wrapper(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            self.on_generic_model_log(element, symbol)
            return self.on_generic_model(element, symbol)
        return wrapper

    def source(element: str) -> ElementHandler:
        def wrapper(self, symbol):
            self.on_source_log(element, symbol)
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

    def __init__(self, kicad_schema: KiCadSchema) -> None:
        self._code: list[str] = []

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
                    match _:
                        case str():
                            self._code.append(_)
                        case _:
                            self._code += _

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

    def on_generic_log(self, element: str, symbol: Symbol) -> None:
        self._logger.info(f"Element '{symbol.reference}' params='{symbol.simulation_paramaters}'")

    ##############################################

    def on_generic_model_log(self, element: str, symbol: Symbol) -> None:
        self._logger.info(f"Element with model '{symbol.reference}' pins='{symbol.simulation_pins}'  value='{symbol.value}' params='{symbol.simulation_paramaters}'")

    ##############################################

    def on_source_log(self, element: str, symbol: Symbol) -> None:
        self._logger.info(f"Source '{symbol.simulation_device}' type='{symbol.simulation_type}' value='{symbol.value}' params='{symbol.simulation_paramaters}'")

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
        reference = symbol.reference[len(element):]
        value = self._unit_value(element, symbol)
        args = [reference, *self._pins(symbol), value]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"{element}{args_str}"

    ##############################################

    def on_generic_model(self, element: str, symbol: Symbol) -> list[str]:
        # Fixme: check XD
        reference = symbol.reference[len(element):]   # +1
        pins = self._pins(symbol)
        args = [reference, *pins]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        model_name = f'__{symbol.value}{reference}'
        return [
            f".model {model_name} {element} {symbol.simulation_paramaters}",
            f"{element}{args_str} {model_name}",
        ]

    ##############################################

    def on_source(self, element: str, symbol: Symbol) -> str:
        reference = symbol.reference[len(element):]
        args = [reference, *self._pins(symbol)]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        if symbol.simulation_paramaters:
            return f"{element}{args_str} {symbol.simulation_type}( {symbol.simulation_paramaters} )"
        else:
            value = self._unit_value(element, symbol)
            return f"{element}{args_str} {symbol.simulation_type} {value}"

####################################################################################################

class PythonDumper(BaseDumper):

    _logger = _module_logger.getChild('PythonDumper')

    SEP = ', '

    ##############################################

    def __init__(self, kicad_schema: KiCadSchema, use_pyspice_unit: bool = False) -> None:
        self._use_pyspice_unit = use_pyspice_unit
        super().__init__(kicad_schema)

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
        return self.SEP.join(args)

    ##############################################

    def _split_parameters(self, symbol: Symbol) -> dict[str, str]:
        d = {}
        for _ in symbol.simulation_paramaters.split(' '):
            key, value = _.split('=')
            d[key] = value
        return d

    def _format_parameters(self, symbol: Symbol) -> str:
        return self.SEP.join([f"{key}='{value}'" for key, value in self._split_parameters(symbol).items()])

    ##############################################

    def on_generic(self, element: str, symbol: Symbol) -> str:
        reference = symbol.reference[len(element):]
        value = self._unit_value(element, symbol)
        args = [reference, *self._pins(symbol), value]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"circuit.{element}({args_str})"

    ##############################################

    def on_generic_model(self, element: str, symbol: Symbol) -> list[str]:
        # Fixme: check XD
        reference = symbol.reference[len(element):]   # +1
        pin_names = [_.name for _ in symbol.pins]
        pins = self._pins(symbol)
        match pin_names:
            case ('K', 'A'):
                pins = list(reversed(pins))
        args = [reference, *pins]
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        model_name = f'{symbol.value}{reference}'
        # Fixme: versus match
        mode_type = {
            'D': 'diode',
        }[element]
        parameters = self._format_parameters(symbol)
        return [
            f"circuit.model({model_name}, {mode_type}, {parameters})",
            f"circuit.{element}({args_str}, model='{model_name}')",
        ]

    ##############################################

    def on_source(self, element: str, symbol: Symbol) -> str:
        reference = symbol.reference[len(element):]
        match symbol.simulation_type.upper():
            case 'PULSE':
                element = 'PulseVoltageSource'
        args = [reference, *self._pins(symbol)]
        parameters = ''
        if symbol.simulation_paramaters:
            parameters = self._format_parameters(symbol)
            if parameters:
                parameters = self.SEP + parameters
        else:
            value = self._unit_value(element, symbol)
            if symbol.reference[0] in ('V',):
                value += '@u_V'
            args.append(value)
        args_str = self._str_args(args)  # ty: ignore[invalid-argument-type]
        return f"circuit.{element}({args_str}{parameters})"
