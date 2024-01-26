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
from typing import Iterable, Iterator

import logging
import os
import pickle
import re

from PySpice.Spice.Parser import Subcircuit, Model
from PySpice.Tools import PathTools
from .SpiceInclude import SpiceInclude, is_yaml

####################################################################################################

NEWLINE = os.linesep

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

    def __init__(self, root_path: str | Path, scan: bool = False) -> None:
        self._path = PathTools.expand_path(root_path)
        if not self._path.exists():
            self._path.mkdir(parents=True)
            self._logger.info(f"Created {self._path}")
        self._subcircuits = {}
        self._models = {}
        if not scan:
            if self.has_db_path:
                self.load()
            else:
                self._logger.info("Initialize library...")
                scan = True
        if scan:
            self.scan()
            self.save()

    ##############################################

    @property
    def db_path(self) -> Path:
        return self._path.joinpath('db.pickle')

    @property
    def has_db_path(self) -> bool:
        return self.db_path.exists()

    ##############################################

    def __bool__(self) -> bool:
        return bool(self._subcircuits or self._models)

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
        # self.__dict__.update(state)
        self._subcircuits = state['subcircuits']
        self._models = state['models']

    ##############################################

    def save(self) -> None:
        with open(self.db_path, 'wb') as fh:
            _ = self.__getstate__()
            pickle.dump(_, fh)

    def load(self) -> None:
        self._logger.info(f"Load {self.db_path}")
        with open(self.db_path, 'rb') as fh:
            _ = pickle.load(fh)
            self.__setstate__(_)

    ##############################################

    def _category_path(self, category: str) -> Path:
        category = category.split('/')
        return self._path.joinpath(*category)

    ##############################################

    def add_category(self, category: str) -> None:
        path = self._category_path(category)
        if not path.exists():
            path.mkdir(parents=True)
            self._logger.info(f"Created {path}")
        else:
            self._logger.info(f"category '{category}' already exists")

    ##############################################

    def _list_categories(self, path: Path | str, level: int = 0) -> str:
        text = ''
        indent = ' '*4*level
        for entry in sorted(os.scandir(path), key=lambda entry: entry.name):
            if entry.is_dir():
                text += f'{indent}{entry.name}' + NEWLINE
                text += self._list_categories(entry.path, level+1)
        return text

    def list_categories(self) -> str:
        return self._list_categories(self._path)

    ##############################################

    def scan(self) -> None:
        self._logger.info(f"Scan {self._path}...")
        for path in PathTools.walk(self._path):
            _ = path.suffix.lower()
            if _ in self.EXTENSIONS:
                self._handle_library(path)

    ##############################################

    def _handle_library(self, path: Path) -> None:
        spice_include = SpiceInclude(path)
        # Fixme: check overwrite
        self._models.update({_.name: path for _ in spice_include.models})
        self._subcircuits.update({_.name: path for _ in spice_include.subcircuits})

    ##############################################

    def delete_yaml(self) -> None:
        for path in PathTools.walk(self._path):
            if is_yaml(path):
                self._logger.info(f"{NEWLINE}Delete {path}")
                path.unlink()

    ##############################################

    def __getitem__(self, name: str) -> Subcircuit | Model:
        if not self:
            self._logger.warning("Empty library")
        if name in self._subcircuits:
            path = self._subcircuits[name]
        elif name in self._models:
            path = self._models[name]
        else:
            # print('Library {} not found in {}'.format(name, self._path))
            # self._logger.warn('Library {} not found in {}'.format(name, self._path))
            raise KeyError(name)
        # Fixme: lazy ???
        return SpiceInclude(path)[name]

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

    def search(self, regexp: str) -> Iterable[tuple[str, SpiceInclude]]:
        """ Return dict of all models/subcircuits with names matching regex. """
        regexp = re.compile(regexp)
        models_subcircuits = {**self._models, **self._subcircuits}
        if not models_subcircuits:
            self._logger.warning("Empty library")
        for name, _ in models_subcircuits.items():
            if regexp.search(name):
                yield name, SpiceInclude(_)
