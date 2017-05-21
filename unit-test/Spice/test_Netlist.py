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

import unittest

####################################################################################################

from PySpice.Spice.Netlist import *
from PySpice.Unit.Units import *

####################################################################################################

class VoltageDivider(SubCircuitFactory):
    __name__ = 'VoltageDivider'
    __nodes__ = ('input', 'output_plus', 'output_minus')
    def __init__(self, **kwargs):
        super().__init__(title='Voltage Divider', **kwargs)
        self.R(1, 'input', 'output_plus', kilo(9))
        self.R(2, 'output_plus', 'output_minus', kilo(1))

####################################################################################################

class VoltageDividerCircuit(Circuit):
    def __init__(self, **kwargs):
        super().__init__(title='Voltage Divider', **kwargs)
        self.V('input', 'in', self.gnd, '10V')
        self.R(1, 'in', 'out', kilo(9))
        self.R(2, 'out', self.gnd, kilo(1))

####################################################################################################

class TestNetlist(unittest.TestCase):

    ##############################################

    def _test_spice_declaration(self, circuit, spice_declaration):

        self.assertEqual(str(circuit), spice_declaration[1:])

    ##############################################

    def _test_nodes(self, circuit, nodes):

        node_names = sorted([str(node.name) for node in circuit.nodes])
        nodes = sorted([str(node) for node in nodes])
        self.assertListEqual(node_names, nodes)

####################################################################################################

class TestSubCircuit(TestNetlist):

    ##############################################

    def test(self):

        spice_declaration = """
.subckt VoltageDivider input output_plus output_minus
R1 input output_plus 9k
R2 output_plus output_minus 1k
.ends VoltageDivider
"""
        self._test_spice_declaration(VoltageDivider(), spice_declaration)

####################################################################################################

class TestCircuit(TestNetlist):

    ##############################################

    def test(self):

        spice_declaration = """
.title Voltage Divider
Vinput in 0 10V
R1 in out 9k
R2 out 0 1k
.end
"""

        circuit = Circuit('Voltage Divider')
        circuit.V('input', 'in', circuit.gnd, '10V')
        circuit.R(1, 'in', 'out', kilo(9))
        circuit.R(2, 'out', circuit.gnd, kilo(1))
        self._test_spice_declaration(circuit, spice_declaration)

        circuit = VoltageDividerCircuit()
        self._test_spice_declaration(circuit, spice_declaration)

        self._test_nodes(circuit, (0, 'in', 'out'))

        self.assertEqual(circuit.R1.resistance, kilo(9))
        self.assertEqual(circuit['R2'].resistance, kilo(1))

        circuit.R1.resistance = kilo(10)
        self._test_spice_declaration(circuit, spice_declaration.replace('9k', '10k'))

        self.assertEqual(circuit.R1.plus.node, 'in')
        self.assertEqual(circuit.R1.minus.node, 'out')

        # .global .param .include .model

####################################################################################################

if __name__ == '__main__':

    unittest.main()
