####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
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
