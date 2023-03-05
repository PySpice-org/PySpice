####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 jmgc / Fabrice Salvaire
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

from pathlib import Path
import os
import unittest

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.EBNFSpiceParser import SpiceParser

####################################################################################################

path = Path(__file__).parent

with open(path.joinpath('hsop77.cir')) as fh:
    hsop77 = fh.read()

with open(path.joinpath('hsada4077.cir')) as fh:
    hsada4077 = fh.read()

####################################################################################################

def circuit_gft(prb):
    circuit_file = SpiceParser.parse(source=prb[0])
    circuit = circuit_file.build()
    circuit.parameter('prb', str(prb[1]))
    # Fixme: simulate with Xyce, CI !!!
    simulator = circuit.simulator(simulator='xyce-serial')
    simulator.save('all')
    return simulator

####################################################################################################

class TestSpiceParser(unittest.TestCase):

    ##############################################

    #@unittest.skip('')
    def test_parser(self):
        for source in (hsop77, hsada4077):
            results = list(map(circuit_gft, [(source, -1), (source, 1)]))
            self.assertEqual(len(results), 2)
            values = str(results[0])
            self.assertNotRegex(values, r'(\.ic)')

    ##############################################

    #@unittest.skip('')
    def test_subcircuit(self):
        circuit = Circuit('')
        circuit.include('./mosdriver.lib')
        circuit.X('test', 'mosdriver', '0', '1', '2', '3', '4', '5', '6', '7')
        circuit.BehavioralSource('test', '1', '0', voltage_expression='if(False, 0, 1)', smoothbsrc=1)
        print(circuit)

####################################################################################################

if __name__ == '__main__':
    unittest.main()
