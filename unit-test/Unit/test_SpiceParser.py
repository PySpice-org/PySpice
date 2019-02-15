import unittest
from PySpice.Spice.Netlist import Circuit
import os


class TestSpiceParser(unittest.TestCase):
    def test_subcircuit(self):
        print(os.getcwd())
        circuit = Circuit('Diode Characteristic Curve')
        circuit.include(os.path.join(os.getcwd(), 'ucc27211.lib'))
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
