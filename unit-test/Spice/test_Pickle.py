import unittest
from PySpice.Probe.WaveForm import WaveForm
from PySpice.Unit.SiUnits import Second
from PySpice.Unit.Unit import UnitValues, PrefixedUnit
from PySpice.Unit import u_kHz
import pickle
import os
import tempfile
import numpy as np

class TestPickle(unittest.TestCase):
    def test_ndarray(self):
        array = np.ndarray((1, 1))
        with tempfile.TemporaryFile() as fp:
            pickle.dump(array, fp)
            fp.seek(0)
            new_array = pickle.load(fp)
        self.assertEqual(array, new_array)

    def test_unit_values(self):
        unit_values = UnitValues(u_kHz(100).prefixed_unit, (1, 1))
        new_unit_values = pickle.loads(pickle.dumps(unit_values))
        self.assertEqual(unit_values, new_unit_values)

    def test_waveforms(self):
        waveform = WaveForm("Test", u_kHz(100).prefixed_unit, (1, 1))
        new_waveform = pickle.loads(pickle.dumps(waveform))
        self.assertEqual(waveform, new_waveform)
