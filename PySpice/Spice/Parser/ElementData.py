####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

__all__ = ['elements']

####################################################################################################

import logging

####################################################################################################

from PySpice.Spice.Element import ElementParameterMetaClass
from PySpice.Spice.ElementParameter import FlagParameter

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class ElementData:

    """This class represents a device prefix letter."""

    ##############################################

    def __init__(self, letter: str, classes) -> None:

        # Fixme: _ & property

        self.letter = letter
        self.classes = classes

        number_of_positionals_min = 1000
        number_of_positionals_max = 0
        has_optionals = False
        for element_class in classes:
            number_of_positionals = element_class.number_of_positional_parameters
            number_of_positionals_min = min(number_of_positionals_min, number_of_positionals)
            number_of_positionals_max = max(number_of_positionals_max, number_of_positionals)
            has_optionals = max(has_optionals, bool(element_class.optional_parameters))

        self.number_of_positionals_min = number_of_positionals_min
        self.number_of_positionals_max = number_of_positionals_max
        self.has_optionals = has_optionals

        self.multi_devices = len(classes) > 1
        self.has_variable_number_of_pins = letter in ('Q', 'X') # NPinElement, Q has 3 to 4 pins
        if self.has_variable_number_of_pins:
            self.number_of_pins = None
        else:
            # Q and X are single
            self.number_of_pins = classes[0].number_of_pins

        self.has_flag = False
        for element_class in classes:
            for parameter in element_class.optional_parameters.values():
                if isinstance(parameter, FlagParameter):
                    self.has_flag = True

    ##############################################

    def __len__(self) -> int:
        return len(self.classes)

    ##############################################

    def __iter__(self):
        return iter(self.classes)

    ##############################################

    @property
    def single(self):
        if not self.multi_devices:
            return self.classes[0]
        else:
            raise NameError()

####################################################################################################

elements = {}
def _init() -> None:
    for letter, classes in ElementParameterMetaClass._classes.items():
        element_data = ElementData(letter, classes)
        elements[letter] = element_data
        elements[letter.lower()] = element_data
_init()

####################################################################################################

if __name__ == '__main__':
    for element_data in sorted(elements.values(), key=lambda x: len(x)):
        print(element_data.letter,
              len(element_data),
              element_data.number_of_positionals_min, element_data.number_of_positionals_max,
              element_data.has_optionals)

# Single:
# B 0 True
# D 1 True
# F 2 False
# G 1 False
# H 2 False
# I 1 False
# J 1 True
# K 3 False
# M 1 True
# S 2 False
# V 1 False
# W 3 False
# Z 1 True

# Two:
# E 0 1 False
# L 1 2 True

# Three:
# C 1 2 True
# R 1 2 True

# NPinElement:
# Q 1 1 True
# X 1 1 False
