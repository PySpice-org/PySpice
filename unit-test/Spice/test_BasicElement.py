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

from PySpice.Spice.BasicElement import *
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

class TestBasicElement(unittest.TestCase):

    ##############################################

    def _test_spice_declaration(self, element, spice_declaration):

        self.assertEqual(str(element), spice_declaration)

    ##############################################

    def test(self):

        self._test_spice_declaration(Resistor(Circuit(''), '1', 'n1', 'n2', 100),
                                     'R1 n1 n2 100')
        self._test_spice_declaration(Resistor(Circuit(''), '1', 'n1', 'n2', kilo(1)),
                                     'R1 n1 n2 1k')
        self._test_spice_declaration(Resistor(Circuit(''), '1', 'n1', 'n2', kilo(1),
                                              ac=kilo(2),
                                              multiplier=2,
                                              scale=1.5,
                                              temperature=25, device_temperature=26,
                                              noisy=True),
                                     'R1 n1 n2 1k ac=2k dtemp=26 m=2 noisy=1 scale=1.5 temp=25')
        self._test_spice_declaration(Resistor(Circuit(''), '1', 'n1', 'n2', kilo(1),
                                              noisy=False),
                                     'R1 n1 n2 1k')

        self._test_spice_declaration(XSpiceElement(Circuit(''), '1', 1, 0, model='cap'),
                                     'A1 1 0 cap')

####################################################################################################

if __name__ == '__main__':

    unittest.main()
