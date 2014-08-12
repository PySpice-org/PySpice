####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from ..Unit.Units import Unit

####################################################################################################

class ParameterDescriptor(object):

    """ This base class implements a descriptor for element parameters. """

    ##############################################

    def __init__(self, default=None):

        self.default_value = default

        self.attribute_name = None

    ##############################################

    def __get__(self, instance, owner=None):

        try:
            return getattr(instance, '_' + self.attribute_name)
        except AttributeError:
            return self.default_value

    ##############################################

    def validate(self, value):

        return value
        
    ##############################################

    def __set__(self, instance, value):

        setattr(instance, '_' + self.attribute_name, value)

    ##############################################

    def nonzero(self, instance):

        return self.__get__(instance) is not None

    ##############################################

    def to_str(self, instance):

        raise NotImplementedError

####################################################################################################

class PositionalElementParameter(ParameterDescriptor):

    """ This class implements a descriptor for positional element parameters. """

    ##############################################

    def __init__(self, position, default=None, key_parameter=False):

        super(PositionalElementParameter, self).__init__(default)

        self.position = position
        self.key_parameter = key_parameter

    ##############################################

    def __repr__(self):

        return self.__class__.__name__

    ##############################################

    def to_str(self, instance):

        return str(self.__get__(instance))

    ##############################################

    def __cmp__(self, other):

        return cmp(self.key_parameter, other.key_parameter)

####################################################################################################

class ElementNamePositionalParameter(PositionalElementParameter):

    """ This class implements an element name positional element parameter. """

    ##############################################

    def validate(self, value):

        return str(value)

####################################################################################################

class ExpressionPositionalParameter(PositionalElementParameter):

    """ This class implements an expression positional element parameter. """

    ##############################################

    def validate(self, value):

        return str(value)

####################################################################################################

class FloatPositionalParameter(PositionalElementParameter):

    """ This class implements a float positional element parameter. """

    ##############################################

    def validate(self, value):

        if isinstance(value, Unit):
            return value
        else:
            return Unit(value)

####################################################################################################

class InitialStatePositionalParameter(PositionalElementParameter):

    """ This class implements an initial state positional element parameter. """

    ##############################################

    def validate(self, value):

        return bool(value) # Fixme: check KeyParameter

    ##############################################

    def to__str_(self, instance):

        if self.__get__(instance):
            return 'on'
        else:
            return 'off'

####################################################################################################

class ModelPositionalParameter(PositionalElementParameter):

    """ This class implements a model positional element parameter. """

    ##############################################

    def validate(self, value):

        return str(value)

####################################################################################################

class ElementParameter(ParameterDescriptor):

    """ This class implements a descriptor for element parameters. """

    ##############################################

    def __init__(self, spice_name, default=None):

        super(ElementParameter, self).__init__(default)

        self.spice_name = spice_name

     ##############################################

    def __repr__(self):

        return self.__class__.__name__

####################################################################################################

class BoolKeyParameter(ElementParameter):

    """ This class implements a boolean key value element parameter. """

    ##############################################

    def __init__(self, spice_name, default=False):

        super(BoolKeyParameter, self).__init__(spice_name, default)

    ##############################################

    def nonzero(self, instance):

        return bool(self.__get__(instance))

    ##############################################

    def to_str(self, instance):

        if self.nonzero(instance):
            return '0'
        else:
            return '1'

####################################################################################################

class FlagKeyParameter(ElementParameter):

    """ This class implements a flag key value element parameter. """

    ##############################################

    def __init__(self, spice_name, default=False):

        super(FlagKeyParameter, self).__init__(spice_name, default)

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

class KeyValueParameter(ElementParameter):

    """ This class implements a key value pair element parameter. """

    ##############################################

    def str_value(self, instance):

        return str(self.__get__(instance))

    ##############################################

    def to_str(self, instance):

        if bool(self):
            return '{}={}'.format(self.spice_name, self.str_value(instance))
        else:
            return ''

####################################################################################################

class ExpressionKeyParameter(KeyValueParameter):

    """ This class implements an expression key value element parameter. """

    ##############################################

    def validate(self, value):

        return str(value)

####################################################################################################

class FloatKeyParameter(KeyValueParameter):

    """ This class implements a float key value element parameter. """

    ##############################################

    def validate(self, value):

        return float(value)

####################################################################################################

class FloatPairKeyParameter(KeyValueParameter):

    """ This class implements a float pair key value element parameter. """

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

class IntKeyParameter(KeyValueParameter):

    """ This class implements an integer key value element parameter. """

    ##############################################

    def validate(self, value):

        return int(value)

####################################################################################################
# 
# End
# 
####################################################################################################
