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

####################################################################################################

import unittest

####################################################################################################

from PySpice.Spice.Expression.Parser import Parser

####################################################################################################

class TestParser(unittest.TestCase):

    ##############################################

    def test_parser(self):

        parser = Parser()

        parser.parse('1')

        parser.parse('.1')
        parser.parse('.123')
        parser.parse('1.')
        parser.parse('1.1')
        parser.parse('1.123')
        parser.parse('1.e2')
        parser.parse('1.e-2')
        parser.parse('1.123e2')
        parser.parse('1.123e-2')
        parser.parse('1.123e23')
        parser.parse('1.123e-23')

        parser.parse('-1')
        parser.parse('-1.1')

        parser.parse('! rised')

        parser.parse('1 ** 2')

        parser.parse('1 * 2')
        parser.parse('1 / 2')
        parser.parse('1 % 2')
        # parser.parse('1 \\ 2')
        parser.parse('1 + 2')

        parser.parse('1 == 2')
        parser.parse('1 != 2')
        parser.parse('1 >= 2')
        parser.parse('1 >= 2')
        parser.parse('1 < 2')
        parser.parse('1 > 2')

        parser.parse('x && y')
        parser.parse('x || y')

        parser.parse('c ? x : y')

        parser.parse('1 * -2')

        parser.parse('x * -y + z')

####################################################################################################

if __name__ == '__main__':

    unittest.main()
