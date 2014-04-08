####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

import math
import unittest

####################################################################################################

from PySpice.Units import *
            
####################################################################################################

class TestUnits(unittest.TestCase):

    ##############################################

    def __init__(self, method_name):

        super(TestUnits, self).__init__(method_name)

    ##############################################
        
    def test_units(self):

        self.assertEqual(str(kilo(1)), '1k')
        self.assertEqual(float(kilo(1)), 1000.)

        self.assertTrue(kilo(1))
        self.assertFalse(kilo(0))

        self.assertEqual(kilo(1), kilo(1))
        self.assertNotEqual(kilo(1), kilo(2))

        self.assertEqual(+kilo(1), kilo(1))
        self.assertEqual(-kilo(1), kilo(-1))
        self.assertEqual(kilo(1) + kilo(2), kilo(3))
        self.assertEqual(kilo(2) - kilo(1), kilo(1))
        self.assertEqual(kilo(2) * kilo(3), kilo(6))
        self.assertEqual(kilo(6) / kilo(3), kilo(2))
        self.assertEqual(kilo(2)**3, kilo(8))

        self.assertTrue(kilo(1) < kilo(2))
        self.assertTrue(kilo(1) <= kilo(1))
        self.assertTrue(kilo(2) > kilo(1))
        self.assertTrue(kilo(1) >= kilo(1))

        self.assertEqual(kilo(1) + 2, kilo(1.002))
        self.assertEqual(kilo(1) + Unit(2), kilo(1.002))
        self.assertEqual(kilo(1) + milli(2000), kilo(1.002))

        self.assertEqual(math.sqrt(kilo(10)), 100)

        self.assertEqual(float(kilo(2).inverse()), 1/2000.)

        # Doesn't work
        # self.assertEqual(2 + kilo(1), kilo(1.002))

    ##############################################
        
    def test_frequency(self):

        self.assertEqual(Frequency(50).period, 1/50.)
        self.assertEqual(Frequency(50).pulsation, 2*math.pi*50)
        self.assertEqual(Period(1/50.).frequency, 50.)
        self.assertEqual(Period(1/50.).pulsation, 2*math.pi*50)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################
