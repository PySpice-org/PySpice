####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2019 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
            'Vpwl1 1 0 PWL(0s 0V 10ms 0V 11ms 5V 20ms 5V)',
        )

        self._test_spice_declaration(
            PieceWiseLinearVoltageSource(
                Circuit(''),
                'pwl1', '1', '0',
                values=[(0, 0), (10@u_ms, 0), (11@u_ms, 5@u_V), (20@u_ms, 5@u_V)],
                repeat_time=12@u_ms, delay_time=34@u_ms,
            ),
            'Vpwl1 1 0 PWL(0s 0V 10ms 0V 11ms 5V 20ms 5V r=12ms td=34ms)',
        )

        self._test_spice_declaration(
            PieceWiseLinearVoltageSource(
                Circuit(''),
                'pwl1', '1', '0',
                values=[(0, 0), (10@u_ms, 0), (11@u_ms, 5@u_V), (20@u_ms, 5@u_V)],
                repeat_time=12@u_ms, delay_time=34@u_ms,
                dc=50@u_V,
            ),
            'Vpwl1 1 0 DC 50V PWL(0s 0V 10ms 0V 11ms 5V 20ms 5V r=12ms td=34ms)',
        )

####################################################################################################

if __name__ == '__main__':
    unittest.main()
