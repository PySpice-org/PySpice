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

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Expressions import *
import math as m

####################################################################################################


class TestExpression(unittest.TestCase):

    def test_symbol(self):
        x = Symbol('x')
        V_3 = V(Symbol("3"))
        cos_V_3 = Cos(V_3)
        values = {str(V_3): 25}
        self.assertAlmostEqual(m.cos(25), cos_V_3(**values))
        y = Symbol('y')
        add = Add(x, y)
        add_operator = x + y
        self.assertEqual("(x + y)", add)
        self.assertEqual("(x + y)", add_operator)
        add_float = x + 5.
        self.assertEqual("(x + 5.0)", add_float)
        add_float = 5. + x
        self.assertEqual("(5.0 + x)", add_float)
        V_5 = V("5")
        self.assertEqual("v(5)",V_5)
        self.assertEqual("cos(27)", Cos(27))
        self.assertEqual(m.cos(27), Cos(27)())
        self.assertTrue(Xor(True, False)())
        self.assertFalse(Xor(True, True)())
        self.assertTrue(Xor(False, True)())
        self.assertFalse(Xor(False, False)())

    def test_expression(self):
        print(If(V("v_sw", "gnd") < 2. * Symbol("v_3v") / 3., 1, 1e-6))
        circuit = Circuit("Simulation")
        circuit.BehavioralResistor('b',
                                   'na',
                                   'nb',
                                   resistance_expression=If(V("v_sw", "gnd") < 2. * Symbol("v_3v") / 3., 1, 1e-6))
        print(circuit)

if __name__ == '__main__':

    unittest.main()
