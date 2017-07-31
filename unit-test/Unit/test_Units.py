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

import math
import unittest

####################################################################################################

from PySpice.Unit import *
from PySpice.Unit.Unit import SiDerivedUnit, UnitMetaclass

####################################################################################################

class TestUnits(unittest.TestCase):

    ##############################################

    def __init__(self, method_name):

        super().__init__(method_name)

    # @unittest.skip('')
    def test_si_derivate_unit(self):

        self.assertEqual(SiDerivedUnit().is_anonymous(), True)
        self.assertEqual(bool(SiDerivedUnit()), False)

        si_power1 = SiDerivedUnit('m')
        si_power2 = SiDerivedUnit('s')

        self.assertEqual(bool(si_power1), True)

        self.assertEqual(si_power1, SiDerivedUnit(power={'m': 1}))
        self.assertEqual(si_power2, SiDerivedUnit(power={'s': 1}))

        self.assertEqual(si_power1.is_base_unit(), True)
        self.assertEqual((si_power1 * si_power2).is_base_unit(), False)

        self.assertEqual(si_power1.inverse(), SiDerivedUnit(power={'m': -1}))
        self.assertEqual(si_power1 * si_power2, SiDerivedUnit(power={'m': 1, 's': 1}))
        self.assertEqual(si_power1 / si_power2, SiDerivedUnit(power={'m': 1, 's': -1}))

        self.assertEqual(si_power1 * si_power2, SiDerivedUnit('m*s'))
        self.assertEqual(si_power1 / si_power2, SiDerivedUnit('m*s^-1'))

        self.assertEqual(str(si_power1 / si_power2), 'm*s^-1')

    ##############################################

    def _test_canonise(self, unit, string):

        self.assertEqual(unit.canonise().str_spice(), string)

    ##############################################

    # @unittest.skip('')
    def test_units(self):

        self.assertEqual(kilo(1).str_spice(), '1k')
        self.assertEqual(float(kilo(1)), 1000.)

        self.assertTrue(kilo(1))
        self.assertFalse(kilo(0))

        self.assertEqual(kilo(1), kilo(1))
        self.assertNotEqual(kilo(1), kilo(2))

        self.assertEqual(+kilo(1), kilo(1))
        self.assertEqual(-kilo(1), kilo(-1))
        self.assertEqual(kilo(1) + kilo(2), kilo(3))
        self.assertEqual(kilo(2) - kilo(1), kilo(1))
        self.assertEqual(kilo(1) + Unit(2), kilo(1.002))
        self.assertEqual(kilo(1) + milli(2000), kilo(1.002))

        # self.assertEqual(float(kilo(1) + 2), 1002.)
        # self.assertEqual(float(kilo(1) + Unit(2)), 1002.)
        # self.assertEqual(kilo(1) + 2, kilo(1.002))
        # self.assertEqual(2 + kilo(1), kilo(1.002))

        self.assertEqual(kilo(2) * kilo(3), mega(6))
        self.assertEqual(kilo(2) * 3, kilo(6))
        self.assertEqual(kilo(6) / kilo(3), Unit(2))
        self.assertEqual(kilo(6) / 3, kilo(2))
        self.assertEqual(3 * kilo(2), kilo(6))

        self.assertEqual(kilo(2)**3, kilo(8))

        self.assertTrue(kilo(1) < kilo(2))
        self.assertTrue(kilo(1) <= kilo(1))
        self.assertTrue(kilo(2) > kilo(1))
        self.assertTrue(kilo(1) >= kilo(1))

        self.assertEqual(math.sqrt(kilo(10)), 100)

        self.assertEqual(float(kilo(2).inverse()), 1/2000.)

        self.assertEqual(str(u_kHz(123.4)), '123.4 kHz')
        self.assertEqual(str(u_MHz(123.4)), '123.4 MHz')
        self.assertEqual(u_MHz(123.4).str_spice(), '123.4MegHz')

        self._test_canonise(Unit(-.0009), '-900.0u')
        self._test_canonise(Unit(-.001), '-1.0m')
        self._test_canonise(Unit(.0009999), '999.9u')
        self._test_canonise(Unit(.001), '1.0m')
        self._test_canonise(Unit(.010), '10.0m')
        self._test_canonise(Unit(.100), '100.0m')
        self._test_canonise(Unit(.999), '999.0m')
        self._test_canonise(kilo(.0001), '100.0m')
        self._test_canonise(kilo(.001), '1.0')
        self._test_canonise(kilo(.100), '100.0')
        self._test_canonise(kilo(.999), '999.0')
        self._test_canonise(kilo(1), '1k') # Fixme: .0
        self._test_canonise(kilo(1000), '1.0Meg')

    ##############################################

    # @unittest.skip('')
    def test_unit_conversion(self):

        # for units in UnitMetaclass.__hash_map__.values():
        #     print(units, [x for x in units if x.is_default_unit()])

        self.assertEqual(u_ms(20).inverse(), Frequency(50))
        self.assertEqual(Frequency(50).inverse(), u_ms(20))
        self.assertEqual(u_Hz(50).inverse(), u_ms(20))

    ##############################################

    def test_frequency(self):

        self.assertEqual(Frequency(50).period, 1/50.)
        self.assertEqual(u_Hz(50).period, u_s(1/50.))
        self.assertEqual(Frequency(50).pulsation, 2*math.pi*50)
        self.assertEqual(Period(1/50.).frequency, 50.)
        self.assertEqual(u_s(1/50.).frequency, u_Hz(50.))
        self.assertEqual(Period(1/50.).pulsation, 2*math.pi*50)

####################################################################################################

if __name__ == '__main__':

    unittest.main()
