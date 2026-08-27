####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 jmgc / Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

import pickle
import tempfile
import unittest

import numpy as np

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.WaveForm import WaveForm
from PySpice.Unit.Unit import UnitValues
from PySpice.Unit import u_kHz

####################################################################################################

class TestPickle(unittest.TestCase):

    ##############################################

    def test_ndarray(self):
        array = np.ndarray((1, 1))
        with tempfile.TemporaryFile() as fh:
            pickle.dump(array, fh)
            fh.seek(0)
            new_array = pickle.load(fh)
        self.assertEqual(array, new_array)

    ##############################################

    def test_unit_values(self):
        unit_values = UnitValues(u_kHz(100).prefixed_unit, (1, 1))
        new_unit_values = pickle.loads(pickle.dumps(unit_values))
        self.assertEqual(unit_values, new_unit_values)

    ##############################################

    def test_waveform(self):
        waveform = WaveForm('Test', u_kHz(100).prefixed_unit, (1, 1))
        new_waveform = pickle.loads(pickle.dumps(waveform))
        self.assertEqual(waveform, new_waveform)

####################################################################################################

if __name__ == '__main__':
    unittest.main()
