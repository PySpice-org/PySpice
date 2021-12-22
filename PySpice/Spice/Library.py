####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

from pathlib import Path
from typing import Iterator

import logging
import os
import re

####################################################################################################

from .Parser import SpiceFile, ParseError, Subcircuit, Model
from PySpice.Tools import PathTools

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SpiceLibrary:

    """This class implements a Spice sub-circuits and models library.

    A library is a directory which is recursively scanned for '.lib' file and parsed for sub-circuit
    and models definitions.

    Example of usage::

        spice_library = SpiceLibrary('/some/path/')

    If the directory hierarchy contains a file that define a 1N4148 sub-circuit then we can retrieve
    the file path using::

        spice_library['1N4148']

    """

    _logger = _module_logger.getChild('Library')

    EXTENSIONS = (
        '.spice',
        '.lib',
        '.mod',
        '.lib@xyce',
        '.mod@xyce',
    )

    ##############################################

    def __init__(self, root_path: str | Path) -> None:

        self._directory = PathTools.expand_path(root_path)

        self._subcircuits = {}
        self._models = {}

        for path in PathTools.walk(self._directory):
            extension = path.suffix.lower()
            if extension in self.EXTENSIONS:
                self._handle_library(path, extension)

    ##############################################

    def _handle_library(self, path: Path, extension: str) -> None:
        self._logger.info(f"Parse {path}")
        try:
            library = SpiceFile(path)
            if library.is_only_subcircuit:
                for subcircuit in library.subcircuits:
                    name = self._suffix_name(subcircuit.name, extension)
                    self._subcircuits[name] = path
            elif library.is_only_model:
                for model in library.models:
                    name = self._suffix_name(model.name, extension)
                    self._models[name] = path
        except ParseError as exception:
            # Parse problem with this file, so skip it and keep going.
            self._logger.warn(f"Parse error in Spice library {path}{os.linesep}{exception}")

    ##############################################

    @staticmethod
    def _suffix_name(name: str, extension: str) -> str:
        if extension.endswith('@xyce'):
            name += '@xyce'
        return name

    ##############################################

    def __getitem__(self, name: str) -> Subcircuit | Model:
        if name in self._subcircuits:
            return self._subcircuits[name]
        elif name in self._models:
            return self._models[name]
        else:
            # print('Library {} not found in {}'.format(name, self._directory))
            # self._logger.warn('Library {} not found in {}'.format(name, self._directory))
            raise KeyError(name)

    ##############################################

    @property
    def subcircuits(self) -> Iterator[Subcircuit]:
        """ Dictionary of sub-circuits """
        return iter(self._subcircuits)

    @property
    def models(self) -> Iterator[Model]:
        """ Dictionary of models """
        return iter(self._models)

    # ##############################################

    # def iter_on_subcircuits(self):
    #     return self._subcircuits.itervalues()

    # ##############################################

    # def iter_on_models(self):
    #     return self._models.itervalues()

    # ##############################################

    def search(self, regexp: str) -> dict[str, Subcircuit | Model]:
        """ Return dict of all models/subcircuits with names matching regex s. """
        regexp = re.compile(regexp)
        matches = {}
        models_subcircuits = {**self._models, **self._subcircuits}
        for name, _ in models_subcircuits.items():
            if regexp.search(name):
                matches[name] = _
        return matches
