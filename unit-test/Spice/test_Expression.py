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

####################################################################################################

import unittest

####################################################################################################

from PySpice.Spice.Parser.Parser import SpiceParser

####################################################################################################

class TestParser(unittest.TestCase):

    ##############################################

    def test_parser(self):

        parser = SpiceParser()

        # Test commands with numeric expressions
        parser.parse('R1 1 0 1')
        parser.parse('R2 1 0 .1')
        parser.parse('R3 1 0 .123')
        parser.parse('R4 1 0 1.')
        parser.parse('R5 1 0 1.1')
        parser.parse('R6 1 0 1.123')
        parser.parse('R7 1 0 1.e2')
        parser.parse('R8 1 0 1.e-2')
        parser.parse('R9 1 0 1.123e2')
        parser.parse('R10 1 0 1.123e-2')
        parser.parse('R11 1 0 1.123e23')
        parser.parse('R12 1 0 1.123e-23')

        parser.parse('R13 1 0 -1')
        parser.parse('R14 1 0 -1.1')

        # Test behavioural sources with expressions
        parser.parse('B1 1 0 V=1 ** 2')
        parser.parse('B2 1 0 V=1 * 2')
        parser.parse('B3 1 0 V=1 / 2')
        parser.parse('B4 1 0 V=1 % 2')
        parser.parse('B5 1 0 V=1 + 2')

        # Test if statements and comparisons in expressions
        parser.parse('B6 1 0 V=1 == 2 ? 3 : 4')
        parser.parse('B7 1 0 V=1 != 2 ? 3 : 4')
        parser.parse('B8 1 0 V=1 >= 2 ? 3 : 4')
        parser.parse('B9 1 0 V=1 < 2 ? 3 : 4')
        parser.parse('B10 1 0 V=1 > 2 ? 3 : 4')

        # Test boolean operations
        parser.parse('B11 1 0 V=x && y ? 1 : 0')
        parser.parse('B12 1 0 V=x || y ? 1 : 0')

        # Test combination of operations
        parser.parse('B13 1 0 V=1 * -2')
        parser.parse('B14 1 0 V=x * -y + z')

####################################################################################################

if __name__ == '__main__':

    unittest.main()
