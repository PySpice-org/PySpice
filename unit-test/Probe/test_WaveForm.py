####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
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

import numpy as np
from numpy import testing as np_test

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.WaveForm import *
from PySpice.Unit import *

####################################################################################################

class TestUnits(unittest.TestCase):

    ##############################################

    @staticmethod
    def _test_unit_values(values, true_array):

        np_test.assert_almost_equal(values.as_ndarray(True), true_array)

    ##############################################

    # @unittest.skip('')
    def test(self):

        np_array1 = np.arange(10)
        array1 = u_mV(np_array1)
        np_true_array1 = np_array1 / 1000

        np_array2 = np.arange(10, 20)
        array2 = u_mV(np_array2)
        np_true_array2 = np_array2 / 1000

        name = 'waveform1'
        waveform1 = WaveForm(name, array1.prefixed_unit, array1.shape)
        waveform1[...] = array1
        print(repr(waveform1))
        self._test_unit_values(waveform1, np_true_array1)
        self.assertEqual(waveform1.prefixed_unit, U_mV)
        self.assertEqual(waveform1.name, name)

        waveform1 = WaveForm.from_unit_values(name, array1)
        print(repr(waveform1))
        self._test_unit_values(waveform1, np_true_array1)
        self.assertEqual(waveform1.prefixed_unit, U_mV)
        self.assertEqual(waveform1.name, name)

        name = 'waveform2'
        waveform2 = WaveForm.from_unit_values(name, array2)
        print(repr(waveform2))
        self._test_unit_values(waveform2, np_true_array2)
        self.assertEqual(waveform2.prefixed_unit, U_mV)
        self.assertEqual(waveform2.name, name)

        waveform3 = waveform2 - waveform1
        print(repr(waveform3))
        self._test_unit_values(waveform3, np_true_array2 - np_true_array1)
        self.assertEqual(waveform3.prefixed_unit, U_mV)
        self.assertEqual(waveform3.name, '')

        waveform4 = waveform3.convert(U_uV)
        print(waveform4, type(waveform4))

####################################################################################################

if __name__ == '__main__':

    unittest.main()
