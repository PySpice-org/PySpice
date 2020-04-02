import unittest
from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Parser import SpiceParser
from multiprocessing import Pool, cpu_count
import os


def multiple_sim(simulate, values):
    cpus = cpu_count() - 1
    if cpus == 0:
        cpus = 1
    pools = min(cpus, len(values))
    with Pool(pools) as p:
        analysis = p.map(simulate, values)
    return list(analysis)

def circuit_gft(prb):
    circuit_file = SpiceParser('HSOP77case.net')
    circuit = circuit_file.build_circuit()
    circuit.parameter('prb', str(prb))
    simulator = circuit.simulator(simulator='xyce-serial')
    simulator.save(['all'])
    return simulator.ac(start_frequency=10 - 2,
                        stop_frequency=1e9,
                        number_of_points=10,
                        variation='dec')


class TestSpiceParser(unittest.TestCase):
    def test_parser(self):
        results = multiple_sim(circuit_gft, [-1, 1])
        result = results[0]
        values = result.nodes['x']
        print(repr(values))

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
