####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
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
