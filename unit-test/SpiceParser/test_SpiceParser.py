####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 jmgc / Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from pathlib import Path
import os
import unittest

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Parser import SpiceParser

####################################################################################################

path = Path(__file__).parent

with open(path.joinpath('hsop77.cir')) as fh:
    hsop77 = fh.read()

with open(path.joinpath('hsada4077.cir')) as fh:
    hsada4077 = fh.read()

####################################################################################################

def circuit_gft(prb):
    circuit_file = SpiceParser(source=prb[0])
    circuit = circuit_file.build_circuit()
    circuit.parameter('prb', str(prb[1]))
    # Fixme: simulate with Xyce, CI !!!
    simulator = circuit.simulator(simulator='xyce-serial')
    simulator.save(['all'])
    return simulator

####################################################################################################

class TestSpiceParser(unittest.TestCase):

    ##############################################

    @unittest.skip('')
    def test_parser(self):
        for source in (hsop77, hsada4077):
            results = list(map(circuit_gft, [(source, -1), (source, 1)]))
            self.assertEqual(len(results), 2)
            values = str(results[0])
            self.assertNotRegex(values, r'(\.ic)')

    ##############################################

    @unittest.skip('')
    def test_subcircuit(self):
        circuit = Circuit('')
        circuit.include('.../mosdriver.lib')
        circuit.X('test', 'mosdriver', '0', '1', '2', '3', '4', '5')
        circuit.BehavioralSource('test', '1', '0', voltage_expression='if(0, 0, 1)', smoothbsrc=1)
        print(circuit)

####################################################################################################

if __name__ == '__main__':
    unittest.main()
