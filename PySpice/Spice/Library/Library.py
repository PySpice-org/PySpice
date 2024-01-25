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
import pickle
import re

from .SpiceInclude import SpiceInclude
from PySpice.Spice.Parser import SpiceFile, ParseError, Subcircuit, Model
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

    def __init__(self, root_path: str | Path, scan: bool=True) -> None:
        self._path = PathTools.expand_path(root_path)
        if not self._path.exists():
            os.mkdir(self._path)
            self._logger.info(f"Created {self._path}")

        self._subcircuits = {}
        self._models = {}

        if scan:
            self.scan()
            self.save()

    ##############################################

    @property
    def db_path(self) -> Path:
        return self._path.joinpath('db.pickle')

    ##############################################

    def __getstate__(self):
        # state = self.__dict__.copy()
        state = {
            'subcircuits': self._subcircuits,
            'models': self._models,
        }
        return state

    ##############################################

    def __setstate__(self, state):
        self.__dict__.update(state)

    ##############################################

    def save(self) -> None:
        with open(self.db_path, 'wb') as fh:
            pickle.dump(self.__getstate__(), fh)

    ##############################################

    def _category_path(self, category: str) -> Path:
        category = category.split('/')
        return self._path.joinpath(*category)

    ##############################################

    def add_category(self, category: str) -> None:
        path = self._category_path(category)
        if not path.exists():
            os.makedirs(path)
            self._logger.info(f"Created {path}")
        else:
            self._logger.info(f"category '{category}' already exists")

    ##############################################

    def _list_categories(self, path: Path | str, level: int=0) -> str:
        text = ''
        indent = ' '*4*level
        for entry in sorted(os.scandir(path), key=lambda entry: entry.name):
            if entry.is_dir():
                text += f'{indent}{entry.name}' + os.linesep
                text += self._list_categories(entry.path, level+1)
        return text

    def list_categories(self) -> str:
        return self._list_categories(self._path)

    ##############################################

    def scan(self) -> None:
        for path in PathTools.walk(self._path):
            extension = path.suffix.lower()
            if extension in self.EXTENSIONS:
                self._handle_library(path)

    ##############################################

    def _handle_library(self, path: Path) -> None:
        spice_include = SpiceInclude(path)
        self._models.update({_: path for _ in spice_include.models})
        self._subcircuits.update({_: path for _ in spice_include.subcircuits})

    ##############################################

    def delete_yaml(self) -> None:
        for path in PathTools.walk(self._path):
            extension = path.suffix.lower()
            if extension == '.yaml':
                self._logger.info(f"{os.linesep}Delete {path}")
                os.unlink(path)

    ##############################################

    def __getitem__(self, name: str) -> Subcircuit | Model:
        if name in self._subcircuits:
            return self._subcircuits[name]
        elif name in self._models:
            return self._models[name]
        else:
            # print('Library {} not found in {}'.format(name, self._path))
            # self._logger.warn('Library {} not found in {}'.format(name, self._path))
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
