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

""" This module provides an implementation for enumerate.

The enumerate factory :func:`EnumFactory` builds a enumerate from a list of names and assigns to
these constants a value from 0 to N-1, where N is the number of constants.  For example::

  enum = EnumFactory('Enum1', ('cst1', 'cst2'))

builds a enumerate with *cst1* set to 0 and *cst2* set to 1.

We can get a constant's value using an integer context like::

  int(enum.cst1)

and the constant's name using::

  repr(enum.cst1)

We can test constant equality using::

  enum1.cst == enum2.cst

or with something that understand the *int* protocol::

  enum1.cst == obj
  # equivalent to
  int(enum1.cst) == int(obj)

The number of constants could be retrieved with::

  len(enum)

The enumerate factory :func:`ExplicitEnumFactory` is a variant that permits to specify the values of
the constants::

  enum2 = ExplicitEnumFactory('Enum2', {'cst1':1, 'cst2':3})

We can test if a value is in the enumerate using::

  constant_value in enum2

"""

####################################################################################################

# __all__ = ['EnumFactory', 'ExplicitEnumFactory']

####################################################################################################

class ReadOnlyMetaClass(type):

    """ This meta class implements a class where attributes are read only. """

    ##############################################

    def __setattr__(self, name, value):

        raise NotImplementedError

####################################################################################################

class EnumMetaClass(ReadOnlyMetaClass):

    """ This meta class implements the :func:`len` protocol. """

    ##############################################

    def __len__(self):

        return self._size

    ##############################################

    def __getitem__(self, i):

        return self._index[i]

####################################################################################################

class ExplicitEnumMetaClass(ReadOnlyMetaClass):

    """ This meta class implements the operator ``in``. """

    ##############################################

    def __contains__(self, item):

        return item in self.constants

####################################################################################################

class EnumConstant:

    """ Define an Enum Constant """

    ##############################################

    def __init__(self, name, value):

        self._name = name
        self._value = value

    ##############################################

    def __eq__(self, other):

        return self._value == int(other)

    ##############################################

    def __int__(self):

        return self._value

    ##############################################

    def __hash__(self):

        return self._value

    ##############################################

    def __repr__(self):

        return self._name

####################################################################################################

def EnumFactory(enum_name, enum_tuple):

    """ Return an :class:`EnumMetaClass` instance, where *enum_name* is the class name and
    *enum_tuple* is an iterable of constant's names.
    """

    index = [EnumConstant(name, value) for value, name in enumerate(enum_tuple)]

    obj_dict = {}
    obj_dict['_size'] = len(enum_tuple)
    obj_dict['_index'] = index
    obj_dict.update({str(enum):enum for enum in index})

    return EnumMetaClass(enum_name, (), obj_dict)

####################################################################################################

def ExplicitEnumFactory(enum_name, enum_dict):

    """ Return an :class:`ExplicitEnumMetaClass` instance, where *enum_name* is the class name and
    *enum_dict* is a dict of constant's names and their values.
    """

    obj_dict = {}
    obj_dict['constants'] = list(enum_dict.values())
    for name, value in list(enum_dict.items()):
        obj_dict[name] = EnumConstant(name, value)

    return ExplicitEnumMetaClass(enum_name, (), obj_dict)
