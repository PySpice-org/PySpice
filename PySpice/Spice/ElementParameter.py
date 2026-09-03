####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This modules implements the machinery to define element's parameters as descriptors.

"""

####################################################################################################

from typing import TYPE_CHECKING

from ..Unit import Unit
from .unit import str_spice

if TYPE_CHECKING:
    from .Element import Element

####################################################################################################

class ParameterDescriptor:

    """This base class implements a descriptor for element parameters.

    Public Attributes:

      :attr:`attribute_name`
        Name of the attribute in the element's class

      :attr:`default_value`
        The default value

    """

    ##############################################

    def __init__(self, default: bool | int | None = None) -> None:
        self._default_value = default
        self._attribute_name: str = None  # ty: ignore[invalid-assignment]

    ##############################################

    @property
    def default_value(self) -> bool | int | None:
        return self._default_value

    @property
    def attribute_name(self) -> str:
        return self._attribute_name

    @attribute_name.setter
    def attribute_name(self, name: str) -> None:
        self._attribute_name = name

    ##############################################

    def __get__(self, instance: Element, owner=None):
        try:
            return getattr(instance, '_' + self._attribute_name)
        except AttributeError:
            return self.default_value

    ##############################################

    def __set__(self, instance: Element, value):
        setattr(instance, '_' + self._attribute_name, value)

    ##############################################

    def __repr__(self) -> str:
        return self.__class__.__name__

    ##############################################

    def validate(self, value):
        """Validate the parameter's value."""
        return value

    ##############################################

    def nonzero(self, instance: Element) -> bool:
        return self.__get__(instance) is not None

    ##############################################

    def to_str(self, instance: Element) -> str:
        """Convert the parameter's value to SPICE syntax."""
        raise NotImplementedError

    ##############################################

    def __lt__(self, other) -> bool:
        return self._attribute_name < other.attribute_name

####################################################################################################

class PositionalElementParameter(ParameterDescriptor):

    """This class implements a descriptor for positional element parameters.

    Public Attributes:

      :attr:`key_parameter`
        Flag to specify if the parameter is passed as key parameter in Python

      :attr:`position`
        Position of the parameter in the element definition

    """

    ##############################################

    def __init__(self, position: int, default=None, key_parameter: bool = False) -> None:
        super().__init__(default)
        self._position = position
        self._key_parameter = key_parameter

    ##############################################

    @property
    def position(self) -> int:
        return self._position

    @property
    def key_parameter(self) -> bool:
        return self._key_parameter

    ##############################################

    def to_str(self, instance: Element) -> str:
        return str_spice(self.__get__(instance))

    ##############################################

    def __lt__(self, other) -> bool:
        return self._position < other.position

####################################################################################################

class ElementNamePositionalParameter(PositionalElementParameter):

    """This class implements an element name positional parameter."""

    ##############################################

    def validate(self, value) -> str:
        return str(value)

####################################################################################################

class ExpressionPositionalParameter(PositionalElementParameter):

    """This class implements an expression positional parameter. """

    ##############################################

    def validate(self, value) -> str:
        return str(value)

####################################################################################################

class FloatPositionalParameter(PositionalElementParameter):

    """This class implements a float positional parameter."""

    ##############################################

    def __init__(self, position: int, unit=None, **kwargs) -> None:
        super().__init__(position, **kwargs)
        self._unit = unit

    ##############################################

    def validate(self, value) -> Unit:  # ty: ignore[invalid-type-form]
        if isinstance(value, Unit):  # ty: ignore[invalid-argument-type]
            return value
        else:
            return Unit(value)  # ty: ignore[call-non-callable]

####################################################################################################

class InitialStatePositionalParameter(PositionalElementParameter):

    """This class implements an initial state (on, off) positional parameter."""

    ##############################################

    def validate(self, value) -> bool:
        return bool(value)  # Fixme: check KeyParameter

    ##############################################

    def to_str(self, instance: Element) -> str:
        if self.__get__(instance):
            return 'on'
        else:
            return 'off'

####################################################################################################

class ModelPositionalParameter(PositionalElementParameter):

    """This class implements a model positional parameter. """

    ##############################################

    def validate(self, value) -> str:
        return str(value)

####################################################################################################

class FlagParameter(ParameterDescriptor):

    """This class implements a flag parameter.

    Public Attributes:

      :attr:`spice_name`
        Name of the parameter

    """

    ##############################################

    def __init__(self, spice_name: str, default: bool = False) -> None:
        super().__init__(default)
        self.spice_name = spice_name

    ##############################################

    def nonzero(self, instance: Element) -> bool:
        return bool(self.__get__(instance))

    ##############################################

    def to_str(self, instance: Element) -> str:
        if self.nonzero(instance):
            return 'off'
        else:
            return ''

####################################################################################################

class KeyValueParameter(ParameterDescriptor):

    """This class implements a key value pair parameter.

    Public Attributes:

      :attr:`spice_name`
        Name of the parameter

    """

    ##############################################

    def __init__(self, spice_name: str, default=None) -> None:
        super().__init__(default)
        self.spice_name = spice_name

    ##############################################

    def str_value(self, instance: Element) -> str:
        return str_spice(self.__get__(instance))

    ##############################################

    def to_str(self, instance: Element) -> str:
        if bool(self):
            _ = self.str_value(instance)
            return f'{self.spice_name}={_}'
        else:
            return ''

####################################################################################################

class BoolKeyParameter(KeyValueParameter):

    """This class implements a boolean key parameter."""

    ##############################################

    def nonzero(self, instance: Element) -> bool:
        return bool(self.__get__(instance))

    ##############################################

    def str_value(self, instance: Element) -> str:
        if self.nonzero(instance):
            return '1'
        else:
            return '0'

####################################################################################################

class ExpressionKeyParameter(KeyValueParameter):

    """This class implements an expression key parameter."""

    ##############################################

    def validate(self, value) -> str:
        return str(value)

####################################################################################################

class FloatKeyParameter(KeyValueParameter):

    """This class implements a float key parameter."""

    ##############################################

    def __init__(self, spice_name: str, unit=None, **kwargs) -> None:
        super().__init__(spice_name, **kwargs)
        self._unit = unit

    ##############################################

    def validate(self, value) -> float:
        return float(value)

####################################################################################################

class FloatPairKeyParameter(KeyValueParameter):

    """This class implements a float pair key parameter. """

    ##############################################

    def validate(self, pair) -> tuple[float, float]:  # ty: ignore[invalid-method-override]
        if len(pair) == 2:
            return (float(pair[0]), float(pair[1]))
        else:
            raise ValueError()

    ##############################################

    def str_value(self, instance: Element) -> str:
        return ','.join([str(value) for value in self.__get__(instance)])

####################################################################################################

class FloatTripletKeyParameter(FloatPairKeyParameter):

    """This class implements a triplet key parameter."""

    ##############################################

    def validate(self, uplet) -> tuple[float, float, float]:  # ty: ignore[invalid-method-override]
        if len(uplet) == 3:
            return (float(uplet[0]), float(uplet[1]), float(uplet[2]))
        else:
            raise ValueError()

####################################################################################################

class IntKeyParameter(KeyValueParameter):

    """This class implements an integer key parameter."""

    ##############################################

    def validate(self, value) -> int:
        return int(value)
