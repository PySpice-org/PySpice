import unittest
from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Parser import SpiceParser
from multiprocessing import Pool, cpu_count
import os


def circuit_gft(prb):
    circuit_file = SpiceParser('HSOP77case.net')
    circuit = circuit_file.build_circuit()
    circuit.parameter('prb', str(prb))
    simulator = circuit.simulator(simulator='xyce-serial')
    simulator.save(['all'])
    return simulator.ac(start_frequency=10 - 2,
                        stop_frequency=1e9,
                        number_of_points=10,
                        variation='dec'), simulator


class TestSpiceParser(unittest.TestCase):
    def test_parser(self):
        results = list(map(circuit_gft, [-1, 1]))
        self.assertEqual(len(results), 2)
        self.assertIn('Ninp', results[0][0].nodes)
        circuit = results[0][1]
        values = str(circuit)
        self.assertNotRegex(values, r'(\.ic)')

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
