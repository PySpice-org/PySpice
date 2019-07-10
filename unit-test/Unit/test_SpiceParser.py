import unittest
from PySpice.Spice.Netlist import Circuit
import os


class TestSpiceParser(unittest.TestCase):
    def test_subcircuit(self):
        print(os.getcwd())
        circuit = Circuit('Diode Characteristic Curve')
        circuit.include(os.path.join(os.getcwd(), 'mosdriver.lib'))
        circuit.X('test', 'mosdriver', '0', '1', '2', '3', '4', '5')
        circuit.BehavioralSource('test', '1', '0', voltage_expression='if(0, 0, 1)', smoothbsrc=1)
        print(circuit)
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
