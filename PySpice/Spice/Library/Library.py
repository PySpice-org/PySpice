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

    def __init__(self, root_path: str | Path, scan: bool = False, recurse: bool = False, section: bool = False) -> None:
        # recurse will be removed in the future maybe. it's here because skidl uses it
        # if recurse:
        #     scan = recurse
        self._path = PathTools.expand_path(root_path)
        if not self._path.exists():
            self._path.mkdir(parents=True)
            self._logger.info(f"Created {self._path}")
        # elif self._path.is_file():
        #     self._path = self._path.parent
        self._subcircuits = {}
        self._models = {}
        self._recurse = recurse
        self._section = section
        if not scan:
            if self.has_db_path:
                self.load()
                '''Check if the library has the our path in the subcircuits.'''
                paths = {Path(sub_path) for sub_path in self._subcircuits.values()}
                if self._path not in paths:
                    scan = True 
            else:
                self._logger.info("Initialize library...")
                scan = True
        if scan:
            self.scan()
            self.save()

    ##############################################

    @property
    def db_path(self) -> Path:
        if self._path.is_file():
            # If the db path is for a file, use the file's parent directory
            return self._path.parent.joinpath('db.pickle')
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
        
        # Handle the case where self._path is a file, not a directory
        if self._path.is_file():
            # Check if the file has a valid extension
            _ = self._path.suffix.lower()
            if _ in self.EXTENSIONS:
                try:
                    self._handle_library(self._path)
                except Exception as e:
                    self._logger.warning(f"Failed to parse {self._path}: {e}")
            return
                
        # Handle the case where self._path is a directory
        for path in PathTools.walk(self._path):
            _ = path.suffix.lower()
            if _ in self.EXTENSIONS:
                try:
                    self._handle_library(path)
                except Exception as e:
                    self._logger.warning(f"Failed to parse {path}: {e}")

    ##############################################

    def _handle_library(self, path: Path) -> None:
        spice_include = SpiceInclude(path, recurse=self._recurse, section=self._section)
        # Fixme: check overwrite
        self._models.update({_.name: str(_.path) for _ in spice_include.models})
        self._subcircuits.update({_.name: str(_.path) for _ in spice_include.subcircuits})

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
        
        # First, check if the requested item exists directly
        path = None
        if name in self._subcircuits:
            path = self._subcircuits[name]
        elif name in self._models:
            path = self._models[name]
        else:
            # Item not found directly - warn and raise KeyError
            available = list(self._subcircuits.keys()) + list(self._models.keys())
            available_str = ", ".join(available[:10])
            if len(available) > 10:
                available_str += f", ... ({len(available)-10} more)"
            self._logger.warning(f"Library item '{name}' not found in {self._path}. Available: {available_str}")
            raise KeyError(name)
        
        # Create SpiceInclude with recursion enabled if requested
        spice_include = SpiceInclude(path, recurse=self._recurse)
        
        try:
            # Try to get the item directly from this SpiceInclude
            return spice_include[name]
        except KeyError:
            # Item exists in index but not in the file - search in parent directory
            self._logger.info(f"Item '{name}' referenced in {path} but not found there. Searching in sibling files...")
            
            # Try to find the component in sibling library files
            original_path = Path(path)
            parent_dir = original_path.parent
            
            # Try looking for the item in other library files in the same directory
            for lib_ext in self.EXTENSIONS:
                for sibling_file in parent_dir.glob(f"*{lib_ext}"):
                    if sibling_file == original_path:
                        continue  # Skip the original file
                        
                    try:
                        self._logger.info(f"Checking {sibling_file} for {name}")
                        sibling_include = SpiceInclude(sibling_file, recurse=self._recurse)
                        # Check if this file contains our item
                        for subckt in sibling_include.subcircuits:
                            if subckt.name == name:
                                return subckt
                        for model in sibling_include.models:
                            if model.name == name:
                                return model
                    except Exception as e:
                        self._logger.warning(f"Error checking {sibling_file}: {e}")
            
            # If we still can't find it, try one last method - force reparse everything
            try:
                self._logger.info(f"Attempting one last search with forced reparse for {name}")
                reparse_include = SpiceInclude(path, rewrite_yaml=True, recurse=True)
                return reparse_include[name]
            except KeyError:
                # Detailed error message when all recovery attempts fail
                raise KeyError(f"'{name}' referenced in library index but not found in any source file. Check your include hierarchy.")

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
