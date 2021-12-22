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

__all__ = ['Builder', 'ToPython']

####################################################################################################

import logging
import os

from PySpice.Spice.BasicElement import SubCircuitElement
from PySpice.Spice.Element import ElementParameterMetaClass
from PySpice.Spice.ElementParameter import FlagParameter
from PySpice.Spice.Netlist import Circuit, SubCircuit, Node
from .HighLevelParser import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Translator:

    ##############################################

    def handle(self, obj):
        cls = obj.__class__.__name__
        handler = getattr(self, f'handle_{cls}')
        return handler(obj)

####################################################################################################

class Builder(Translator):

    _logger = _module_logger.getChild('Builder')

    ##############################################

    def __init__(self) -> None:
        self._circuit = None
        self._ground = None

    ##############################################

    @property
    def circuit(self) -> Circuit:
        return self._circuit

    ##############################################

    def translate(self, spice_code:SpiceSource, ground: int=Node.SPICE_GROUND_NUMBER) -> Circuit:
        """Build a :class:`Circuit` instance.

        Use the *ground* parameter to specify the node which must be translated to 0 (SPICE ground node).

        """
        self._circuit = Circuit(spice_code.title)
        self._ground = ground

        for obj in spice_code.obj_lines:
            self.handle(obj)

        return self._circuit

    ##############################################

    def handle_Ac(self, obj: Ac) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Control(self, obj: Control) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Csparam(self, obj: Csparam) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Dc(self, obj: Dc) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Distorsion(self, obj: Distorsion) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Element(self, obj: Element) -> None:
        factory = getattr(self._circuit, obj.factory.ALIAS)
        nodes = obj.translate_ground_node(self._ground)
        parameters = [str(_) for _ in obj._parameters]
        kwargs = obj.dict_parameters
        if obj.letter != 'X':
            # args = nodes + parameters
            args = nodes
            kwargs['raw_spice'] = ' '.join(parameters)
        else:    # != Spice
            args = parameters + nodes
        self._logger.debug(str((obj.letter, obj.name, args, kwargs)))
        self._logger.debug(str((nodes, parameters)))
        # factory(obj.name, *args, **kwargs)
        factory(obj.name, *args, **kwargs)

    ##############################################

    def handle_Else(self, obj: Else) -> None:
        raise NotImplementedError

    ##############################################

    def handle_ElseIf(self, obj: ElseIf) -> None:
        raise NotImplementedError

    ##############################################

    def handle_EndControl(self, obj: EndControl) -> None:
        raise NotImplementedError

    ##############################################

    def handle_End(self, obj: End) -> None:
        pass

    ##############################################

    def handle_EndIf(self, obj: EndIf) -> None:
        raise NotImplementedError

    ##############################################

    def handle_EndSubcircuit(self, obj: EndSubcircuit) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Fourier(self, obj: Fourier) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Function(self, obj: Function) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Global(self, obj: Global) -> None:
        raise NotImplementedError

    ##############################################

    def handle_If(self, obj: If) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Include(self, obj: Include) -> None:
        self._circuit.include(obj.path)

    ##############################################

    def handle_InitialCondition(self, obj: InitialCondition) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Library(self, obj: Library) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Measure(self, obj: Measure) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Model(self, obj: Model) -> None:
        self._circuit.model(obj._name, obj._model_type, **obj._parameters)

    ##############################################

    def handle_NodeSet(self, obj: NodeSet) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Noise(self, obj: Noise) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Op(self, obj: Op) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Options(self, obj: Options) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Param(self, obj: Param) -> None:
        raise NotImplementedError

    ##############################################

    def handle_PeriodicSteadyState(self, obj: PeriodicSteadyState) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Plot(self, obj: Plot) -> None:
        raise NotImplementedError

    ##############################################

    def handle_PoleZero(self, obj: PoleZero) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Print(self, obj: Print) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Probe(self, obj: Probe) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Save(self, obj: Save) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Sensitivity(self, obj: Sensitivity) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Subcircuit(self, obj: Subcircuit, ground=Node.SPICE_GROUND_NUMBER) -> None:
        subcircuit = SubCircuit(obj._name, *obj._nodes)
        SpiceParser._build_circuit(subcircuit, obj._statements, ground)
        return subcircuit

    ##############################################

    def handle_Temperature(self, obj: Temperature) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Title(self, obj: Title) -> None:
        self._circuit.title = str(obj)

    ##############################################

    def handle_Transient(self, obj: Transient) -> None:
        raise NotImplementedError

    ##############################################

    def handle_Width(self, obj: Width) -> None:
        raise NotImplementedError

####################################################################################################

class ToPython(Translator):

    _logger = _module_logger.getChild('ToPython')

    ##############################################

    @classmethod
    def value_to_python(cls, x) -> str:
        if x:
            match x:
                case int():
                    return str(x)
                case str():
                    return f"'{x}'"
        else:
            return ''

    ##############################################

    @classmethod
    def values_to_python(cls, values: list) -> list[str]:
        return [cls.value_to_python(x) for x in values]

    ##############################################

    @classmethod
    def format_kwargs(cls, kwargs: dict) -> list[str]:
        return [f'{key}={cls.value_to_python(value)}' for key, value in kwargs.items()]

    ##############################################

    @classmethod
    def join_args(cls, args: list) -> str:
        return ', '.join(args)

    ##############################################

    def __init__(self) -> None:
        self._ground = None
        self._circuit_name = 'circuit'

    ##############################################

    def translate(self, spice_code:SpiceSource, ground=Node.SPICE_GROUND_NUMBER) -> str:
        self._ground = str(ground)
        source_code = ''

        # Fixme: if self.circuit:
        title = spice_code.title or ''
        source_code += f"circuit = Circuit('{title}')" + os.linesep
        for obj in spice_code.obj_lines:
            line = self.handle(obj)
            if line is not None:
                source_code += line + os.linesep

        return source_code

    ##############################################

    def handle_Ac(self, obj: Ac) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Control(self, obj: Control) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Csparam(self, obj: Csparam) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Dc(self, obj: Dc) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Distorsion(self, obj: Distorsion) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Element(self, obj: Element) -> str:
        args = [obj.name]
        nodes = obj.translate_ground_node(self._ground)
        parameters = [str(_) for _ in obj._parameters]
        if obj.letter != 'X':
            args += nodes + parameters
        else:    # != Spice
            args += parameters + nodes
        args = self.values_to_python(args)
        kwargs = self.format_kwargs(obj.dict_parameters)
        parameters = self.join_args(args + kwargs)
        return f'{self._circuit_name}.{obj.letter}({parameters})'

    ##############################################

    def handle_Else(self, obj: Else) -> str:
        raise NotImplementedError

    ##############################################

    def handle_ElseIf(self, obj: ElseIf) -> str:
        raise NotImplementedError

    ##############################################

    def handle_EndControl(self, obj: EndControl) -> str:
        raise NotImplementedError

    ##############################################

    def handle_End(self, obj: End) -> str:
        return None

    ##############################################

    def handle_EndIf(self, obj: EndIf) -> str:
        raise NotImplementedError

    ##############################################

    def handle_EndSubcircuit(self, obj: EndSubcircuit) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Fourier(self, obj: Fourier) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Function(self, obj: Function) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Global(self, obj: Global) -> str:
        raise NotImplementedError

    ##############################################

    def handle_If(self, obj: If) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Include(self, obj: Include) -> str:
        return f'{self._circuit_name}.include({obj})'

    ##############################################

    def handle_InitialCondition(self, obj: InitialCondition) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Library(self, obj: Library) -> str:
        return f'{self._circuit_name}.lib({obj})'

    ##############################################

    def handle_Measure(self, obj: Measure) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Model(self, obj: Model) -> str:
        args = self.values_to_python((obj.name, obj.model_type))
        kwargs = self.kwargs_to_python(self.parameters)
        parameters = self.join_args(args + kwargs)
        return f'{self._circuit_name}.model({parameters})'

    ##############################################

    def handle_NodeSet(self, obj: NodeSet) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Noise(self, obj: Noise) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Op(self, obj: Op) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Options(self, obj: Options) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Param(self, obj: Param) -> str:
        raise NotImplementedError

    ##############################################

    def handle_PeriodicSteadyState(self, obj: PeriodicSteadyState) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Plot(self, obj: Plot) -> str:
        raise NotImplementedError

    ##############################################

    def handle_PoleZero(self, obj: PoleZero) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Print(self, obj: Print) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Probe(self, obj: Probe) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Save(self, obj: Save) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Sensitivity(self, obj: Sensitivity) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Subcircuit(self, obj: Subcircuit, ground=Node.SPICE_GROUND_NUMBER) -> str:
        raise NotImplementedError
        # subcircuit_name = 'subcircuit_' + obj.name
        # args = self.values_to_python([subcircuit_name] + obj.nodes)
        # source_code = ''
        # source_code += '{} = SubCircuit({})'.format(subcircuit_name, obj.join_args(args)) + os.linesep
        # source_code += SpiceParser.netlist_to_python(subcircuit_name, obj, ground)
        # return source_code

    ##############################################

    def handle_Temperature(self, obj: Temperature) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Title(self, obj: Title) -> str:
        return f"{self._circuit_name} = (str(obj))"

    ##############################################

    def handle_Transient(self, obj: Transient) -> str:
        raise NotImplementedError

    ##############################################

    def handle_Width(self, obj: Width) -> str:
        raise NotImplementedError
