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

"""This modules implements the machinery to define element's parameters as descriptors.

"""

####################################################################################################

from ..Unit import Unit
from ..Tools.StringTools import str_spice

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

    def __init__(self, default=None):

        self._default_value = default
        self._attribute_name = None

    ##############################################

    @property
    def default_value(self):
        return self._default_value

    @property
    def attribute_name(self):
        return self._attribute_name

    @attribute_name.setter
    def attribute_name(self, name):
        self._attribute_name = name

    ##############################################

    def __get__(self, instance, owner=None):

        try:
            return getattr(instance, '_' + self._attribute_name)
        except AttributeError:
            return self.default_value

    ##############################################

    def __set__(self, instance, value):
        setattr(instance, '_' + self._attribute_name, value)

    ##############################################

    def __repr__(self):
        return self.__class__.__name__

    ##############################################

    def validate(self, value):

        """Validate the parameter's value."""

        return value

    ##############################################

    def nonzero(self, instance):
        return self.__get__(instance) is not None

    ##############################################

    def to_str(self, instance):

        """Convert the parameter's value to SPICE syntax."""

        raise NotImplementedError

    ##############################################

    def __lt__(self, other):
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

    def __init__(self, position, default=None, key_parameter=False):

        super().__init__(default)

        self._position = position
        self._key_parameter = key_parameter

    ##############################################

    @property
    def position(self):
        return self._position

    @property
    def key_parameter(self):
        return self._key_parameter

    ##############################################

    def to_str(self, instance):
        return str_spice(self.__get__(instance))

    ##############################################

    def __lt__(self, other):
        return self._position < other.position

####################################################################################################

class ElementNamePositionalParameter(PositionalElementParameter):

    """This class implements an element name positional parameter."""

    ##############################################

    def validate(self, value):
        return str(value)

####################################################################################################

class ExpressionPositionalParameter(PositionalElementParameter):

    """This class implements an expression positional parameter. """

    ##############################################

    def validate(self, value):
        return str(value)

####################################################################################################

class FloatPositionalParameter(PositionalElementParameter):

    """This class implements a float positional parameter."""

    ##############################################

    def __init__(self, position, unit=None, **kwargs):

        super().__init__(position, **kwargs)
        self._unit = unit

    ##############################################

    def validate(self, value):

        if isinstance(value, Unit):
            return value
        else:
            return Unit(value)

####################################################################################################

class InitialStatePositionalParameter(PositionalElementParameter):

    """This class implements an initial state (on, off) positional parameter."""

    ##############################################

    def validate(self, value):
        return bool(value) # Fixme: check KeyParameter

    ##############################################

    def to_str(self, instance):

        if self.__get__(instance):
            return 'on'
        else:
            return 'off'

####################################################################################################

class ModelPositionalParameter(PositionalElementParameter):

    """This class implements a model positional parameter. """

    ##############################################

    def validate(self, value):
        return str(value)

####################################################################################################

class FlagParameter(ParameterDescriptor):

    """This class implements a flag parameter.

    Public Attributes:

      :attr:`spice_name`
        Name of the parameter

    """

    ##############################################

    def __init__(self, spice_name, default=False):

        super().__init__(default)

        self.spice_name = spice_name

    ##############################################

    def nonzero(self, instance):
        return bool(self.__get__(instance))

    ##############################################

    def to_str(self, instance):

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

    def __init__(self, spice_name, default=None):

        super().__init__(default)

        self.spice_name = spice_name

    ##############################################

    def str_value(self, instance):
        return str_spice(self.__get__(instance))

    ##############################################

    def to_str(self, instance):

        if bool(self):
            return '{}={}'.format(self.spice_name, self.str_value(instance))
        else:
            return ''

####################################################################################################

class BoolKeyParameter(KeyValueParameter):

    """This class implements a boolean key parameter."""

    ##############################################

    def nonzero(self, instance):
        return bool(self.__get__(instance))

    ##############################################

    def str_value(self, instance):

        if self.nonzero(instance):
            return '1'
        else:
            return '0'

####################################################################################################

class ExpressionKeyParameter(KeyValueParameter):

    """This class implements an expression key parameter."""

    ##############################################

    def validate(self, value):
        return str(value)

####################################################################################################

class FloatKeyParameter(KeyValueParameter):

    """This class implements a float key parameter."""

    ##############################################

    def __init__(self, spice_name, unit=None, **kwargs):

        super().__init__(spice_name, **kwargs)
        self._unit = unit

    ##############################################

    def validate(self, value):
        return float(value)

####################################################################################################

class FloatPairKeyParameter(KeyValueParameter):

    """This class implements a float pair key parameter. """

    ##############################################

    def validate(self, pair):

        if len(pair) == 2:
            return (float(pair[0]), float(pair[1]))
        else:
            raise ValueError()

    ##############################################

    def str_value(self, instance):
        return ','.join([str(value) for value in self.__get__(instance)])

####################################################################################################

class FloatTripletKeyParameter(FloatPairKeyParameter):

    """This class implements a triplet key parameter."""

    ##############################################

    def validate(self, uplet):

        if len(uplet) == 3:
            return (float(uplet[0]), float(uplet[1]), float(uplet[2]))
        else:
            raise ValueError()

####################################################################################################

class IntKeyParameter(KeyValueParameter):

    """This class implements an integer key parameter."""

    ##############################################

    def validate(self, value):
        return int(value)
