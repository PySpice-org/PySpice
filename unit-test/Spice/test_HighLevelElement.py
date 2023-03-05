####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2019 Fabrice Salvaire
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

from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

class TestHighLevelElement(unittest.TestCase):

    ##############################################

    def _test_spice_declaration(self, element, spice_declaration):
        self.assertEqual(str(element), spice_declaration)

    ##############################################

    def test(self):

        self._test_spice_declaration(
            PieceWiseLinearVoltageSource(
                Circuit(''),
                'pwl1', '1', '0',
                values=[(0, 0), (10@u_ms, 0), (11@u_ms, 5@u_V), (20@u_ms, 5@u_V)],
            ),
            'vpwl1 1 0 pwl(0s 0v 10ms 0v 11ms 5v 20ms 5v r=0s td=0.0s)',
        )

        self._test_spice_declaration(
            PieceWiseLinearVoltageSource(
                Circuit(''),
                'pwl1', '1', '0',
                values=[(0, 0), (10@u_ms, 0), (11@u_ms, 5@u_V), (20@u_ms, 5@u_V)],
                repeat_time=12@u_ms, time_delay=34@u_ms,
            ),
            'vpwl1 1 0 pwl(0s 0v 10ms 0v 11ms 5v 20ms 5v r=12ms td=34ms)',
        )

        self._test_spice_declaration(
            PieceWiseLinearVoltageSource(
                Circuit(''),
                'pwl1', '1', '0',
                values=[(0, 0), (10@u_ms, 0), (11@u_ms, 5@u_V), (20@u_ms, 5@u_V)],
                repeat_time=12@u_ms, time_delay=34@u_ms,
                dc=50@u_V,
            ),
            'vpwl1 1 0 dc 50v pwl(0s 0v 10ms 0v 11ms 5v 20ms 5v r=12ms td=34ms)',
        )

####################################################################################################

if __name__ == '__main__':
    unittest.main()
