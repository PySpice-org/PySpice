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

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import *
from PySpice.Unit import *

####################################################################################################

class VoltageDivider(SubCircuitFactory):
    __name__ = 'VoltageDivider'
    __nodes__ = ('input', 'output_plus', 'output_minus')
    def __init__(self):
        super().__init__()
        self.R(1, 'input', 'output_plus', 9@u_kΩ)
        self.R(2, 'output_plus', 'output_minus', 1@u_kΩ)

####################################################################################################

class VoltageDividerCircuit(Circuit):
    def __init__(self):
        super().__init__(title='Voltage Divider')
        self.V('input', 'in', self.gnd, '10V')
        self.R(1, 'in', 'out', 9@u_kΩ)
        self.R(2, 'out', self.gnd, 1@u_kΩ)

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
R1 input output_plus 9kOhm
R2 output_plus output_minus 1kOhm
.ends VoltageDivider
"""
        self._test_spice_declaration(VoltageDivider(), spice_declaration)

####################################################################################################

class TestCircuit(TestNetlist):

    ##############################################

    def test_basic(self):

        spice_declaration = """
.title Voltage Divider
Vinput in 0 10V
R1 in out 9kOhm
R2 out 0 1kOhm
"""
# .end

        circuit = Circuit('Voltage Divider')
        circuit.V('input', 'in', circuit.gnd, '10V')
        circuit.R(1, 'in', 'out', 9@u_kΩ)
        circuit.R(2, circuit.out, circuit.gnd, 1@u_kΩ) # out node is defined
        self._test_spice_declaration(circuit, spice_declaration)

        circuit = VoltageDividerCircuit()
        self._test_spice_declaration(circuit, spice_declaration)

        self._test_nodes(circuit, (0, 'in', 'out'))

        self.assertTrue(circuit.R1.minus.node is circuit.out)

        self.assertEqual(str(circuit.R1.plus.node), 'in')
        self.assertEqual(str(circuit.R1.minus.node), 'out')

        self.assertEqual(str(circuit['in']), 'in')
        self.assertEqual(str(circuit['out']), 'out')
        self.assertEqual(str(circuit.out), 'out')

        # for pin in circuit.out:
        #     print(pin)

        self.assertEqual(circuit.out.pins, set((circuit.R1.minus, circuit.R2.plus)))

        self.assertEqual(circuit.R1.resistance, 9@u_kΩ)
        self.assertEqual(circuit['R2'].resistance, 1@u_kΩ)

        circuit.R1.resistance = 10@u_kΩ
        self._test_spice_declaration(circuit, spice_declaration.replace('9k', '10k'))

        # .global .param .include .model

    ##############################################

    def test_ground_node(self):

        circuit = Circuit('')
        circuit.V('input', 'in', circuit.gnd, '10V')
        circuit.R(1, 'in', 'out', 9@u_kΩ)
        circuit.R(2, 'out', circuit.gnd, 1@u_kΩ)

        self.assertTrue(circuit.has_ground_node())

        circuit = Circuit('')
        circuit.V('input', 'in', 'fake_ground', '10V')
        circuit.R(1, 'in', 'out', 9@u_kΩ)
        circuit.R(2, 'out', 'fake_ground', 1@u_kΩ)

        self.assertFalse(circuit.has_ground_node())

    ##############################################

    def test_raw_spice(self):

        spice_declaration = """
.title Voltage Divider
R2 out 0 1kOhm
Vinput in 0 10V
R1 in out 9kOhm
"""
# .end

        circuit = Circuit('Voltage Divider')
        circuit.V('input', 'in', circuit.gnd, '10V')
        circuit.R(1, 'in', 'out', raw_spice='9kOhm')
        circuit.raw_spice += 'R2 out 0 1kOhm'
        self._test_spice_declaration(circuit, spice_declaration)

    ##############################################

    def test_keyword_clash(self):

        circuit = Circuit('')
        model = circuit.model('Diode', 'D', is_=1, rs=2)
        self.assertEqual(model.is_, 1)
        self.assertEqual(model['is'], 1)
        self.assertEqual(str(model), '.model Diode D (is=1 rs=2)')

####################################################################################################

if __name__ == '__main__':

    unittest.main()
