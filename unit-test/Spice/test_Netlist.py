####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
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
        super(VoltageDivider, self).__init__(title='Voltage Divider', **kwargs)
        self.R(1, 'input', 'output_plus', kilo(9))
        self.R(2, 'output_plus', 'output_minus', kilo(1))

####################################################################################################

class VoltageDividerCircuit(Circuit):
    def __init__(self, **kwargs):
        super(VoltageDividerCircuit, self).__init__(title='Voltage Divider', **kwargs)
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
.ends
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

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
# 
# End
# 
####################################################################################################
