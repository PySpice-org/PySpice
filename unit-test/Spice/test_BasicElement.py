####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

import unittest

####################################################################################################

from PySpice.Spice.BasicElement import *
from PySpice.Unit.Units import *

####################################################################################################

class TestBasicElement(unittest.TestCase):

    ##############################################

    def _test_spice_declaration(self, element, spice_declaration):

        self.assertEqual(str(element), spice_declaration)

    ##############################################

    def test(self):

        self._test_spice_declaration(Resistor('1', 'n1', 'n2', 100),
                                     'R1 n1 n2 100')
        self._test_spice_declaration(Resistor('1', 'n1', 'n2', kilo(1)),
                                     'R1 n1 n2 1k')
        self._test_spice_declaration(Resistor('1', 'n1', 'n2', kilo(1),
                                              ac=kilo(2),
                                              multiplier=2,
                                              scale=1.5,
                                              temperature=25, device_temperature=26,
                                              noisy=True),
                                     'R1 n1 n2 1k ac=2k dtemp=26 m=2 noisy=1 scale=1.5 temp=25')
        self._test_spice_declaration(Resistor('1', 'n1', 'n2', kilo(1),
                                              noisy=False),
                                     'R1 n1 n2 1k')

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
# 
# End
# 
####################################################################################################
