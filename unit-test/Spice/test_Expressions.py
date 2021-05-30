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

from PySpice.Spice.Expressions import *

####################################################################################################


class TestExpression:

    def test_symbol(self):
        x = Symbol('x')
        V_3 = V(Symbol("3"))
        cos_V_3 = Cos(V_3)
        values = {str(V_3): 25}
        print(cos_V_3(**values))
        y = Symbol('y')
        add = Add(x, y)
        print(add)
        V_5 = V("5")
        print(V_5)
        print(Cos(27))
        print(Cos(27)())


if __name__ == '__main__':

    unittest.main()
