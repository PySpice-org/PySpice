####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
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

import logging
import os

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class DipoleMixin:

    _logger = _module_logger.getChild('DipoleMixin')

    ##############################################

    def __and__(self, other):
        from .Netlist import Node
        self._logger.info(f"Serial connection:{os.linesep}  [{type(self)} {self.name}] & [{type(other)} {other.name}]")
        plus = self.plus
        if isinstance(other, Node):
            plus += other
            return FakeDipole(self.minus, other)
        else:
            plus += other.minus
            return FakeDipole(self.minus, other.plus)

    ##############################################

    def __or__(self, other):
        self._logger.info(f"Parallel connection:{os.linesep}  [{type(self)} {self.name}] | [{type(other)} {other.name}]")
        minus = self.minus
        plus = self.plus
        minus += other.minus
        plus += other.plus
        return FakeDipole(self.minus, self.plus)

    ##############################################

    def __rand__(self, other):
        self._logger.info(f"Serial connection(rand):{os.linesep}  [{type(other)} {other.name}] & [{type(self)} {self.name}]")
        other += self.minus
        return FakeDipole(other, self.plus)

####################################################################################################

class FakeDipole(DipoleMixin):

    ##############################################

    def __init__(self, minus, plus):
        self._minus = minus
        self._plus = plus

    ##############################################

    @property
    def name(self):
        return f'[{self._minus}] => [{self._plus}]'

    ##############################################

    @property
    def minus(self):
        return self._minus

    @property
    def plus(self):
        return self._plus
