####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
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

__all__ = ['SpiceInclude']

####################################################################################################

from pathlib import Path
from typing import Iterator
import hashlib
import logging
import os

import yaml

from PySpice.Spice.Parser import SpiceFile, ParseError
# from PySpice.Spice.Parser import Subcircuit as ParserSubcircuit
# from PySpice.Spice.Parser import Model as ParserModel

####################################################################################################

NEWLINE = os.linesep

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Mixin:

    ##############################################

    @classmethod
    def from_yaml(cls, data: dict) -> 'Mixin':
        args = [data[_] for _ in ('name', 'description')]
        return cls(*args)

    ##############################################

    def __init__(self, name: str, description: str = '') -> None:
        self._name = name
        self._description = description

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    ##############################################

    def to_yaml(self) -> dict:
        return {
            'name': self._name,
            'description': self._description,
        }

####################################################################################################

class Model(Mixin):

    ##############################################

    @classmethod
    def from_yaml(cls, data: dict) -> 'Model':
        args = [data[_] for _ in ('name', 'type', 'description')]
        return cls(*args)

    ##############################################

    def __init__(self, name: str, type_: str, description: str = '') -> None:
        super().__init__(name, description)
        self._type = type_

    ##############################################

    @property
    def type(self) -> str:
        return self._type

    ##############################################

    def to_yaml(self) -> dict:
        _ = super().to_yaml()
        _.update({'type': self._type})
        return _

    ##############################################

    def __repr__(self) -> str:
        return f'Model {self._name} {self._type} "{self._description}"'

####################################################################################################

class Subcircuit(Mixin):

    """
    Subcircuit definitions are for example:
    ```
    .SUBCKT 1N4148 1 2

    .SUBCKT d1n5919brl 2 1

    .SUBCKT LMV981 1 3 6 2 4 5
    # for pinout: +IN -IN +V -V OUT NSD
    ```

    and a call is:
    ```
    X1 2 4 17 3 1 MULTI
    ```
    """

    ##############################################

    @classmethod
    def from_yaml(cls, data: dict) -> 'Subcircuit':
        args = [data[_] for _ in ('name', 'nodes', 'description')]
        return cls(*args)

    ##############################################

    def __init__(self, name: str, nodes: list[str], description: str = '') -> None:
        super().__init__(name, description)
        self._nodes = nodes

    ##############################################

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> Iterator[str]:
        return iter(self._nodes)

    ##############################################

    def to_yaml(self) -> dict:
        _ = super().to_yaml()
        _.update({'nodes': self._nodes})
        return _

    ##############################################

    def __repr__(self) -> str:
        return f'Subcircuit {self._name} {self._nodes} "{self._description}"'

####################################################################################################

class SpiceInclude:

    INCLUDE_PREFIX = '.include '

    _logger = _module_logger.getChild('SpiceInclude')

    ##############################################

    def __init__(self, path: str | Path, rewrite_yaml: bool = False) -> None:
        self._path = Path(path)
        self._extension = None

        self._description = ''
        self._inner_includes = []
        self._inner_libraries = []
        self._models = []
        self._subcircuits = []
        self._digest = None
        self._recursive_digest = None

        # Fixme:
        # rewrite_yaml = True
        # Fixme: check still valid !
        if not rewrite_yaml and self.yaml_path.exists():
            self.load_yaml()
            # self.dump()
        else:
            self.parse()
            self.write_yaml()

    ##############################################

    # def dump(self) -> None:
    #     print(self._path)
    #     for _ in self._models:
    #         print(repr(_))
    #     for _ in self._subcircuits:
    #         print(repr(_))

    ##############################################

    @property
    def path(self) -> Path:
        return self._path

    @property
    def extension(self) -> str:
        # Fixme: cache ???
        if self._extension is None:
            self._extension = self._path.suffix.lower()
        return self._extension

    @property
    def mtime(self) -> float:
        return self._path.stat().st_mtime

    @property
    def yaml_path(self) -> str:
        return Path(str(self._path) + '.yaml')

    @property
    def description(self) -> str:
        return self._description

    @property
    def inner_includes(self) -> Iterator[Path]:
        return iter(self._inner_includes)

    @property
    def inner_libraries(self) -> Iterator[Path]:
        return iter(self._inner_libraries)

    @property
    def subcircuits(self) -> Iterator[Subcircuit]:
        return iter(self._subcircuits)

    @property
    def models(self) -> Iterator[Model]:
        return iter(self._models)

    ##############################################

    def parse(self) -> None:
        self._logger.info(f"Parse {self._path}")
        try:
            spice_file = SpiceFile(self._path)
        except ParseError as exception:
            # Parse problem with this file, so skip it and keep going.
            self._logger.warn(f"Parse error in Spice library {self._path}{NEWLINE}{exception}")
        self._inner_includes = [Path(str(_)) for _ in spice_file.includes]
        self._inner_libraries = [Path(str(_)) for _ in spice_file.libraries]
        for subcircuit in spice_file.subcircuits:
            # name = self._suffix_name(subcircuit.name)
            _ = Subcircuit(subcircuit.name, subcircuit.nodes)
            self._subcircuits.append(_)
        if spice_file.is_only_model:
            for model in spice_file.models:
                # name = self._suffix_name(model.name)
                _ = Model(model.name, model.type)
                self._models.append(_)

    ##############################################

    def _suffix_name(self, name: str) -> str:
        if self.extension.endswith('@xyce'):
            name += '@xyce'
        return name

    ##############################################

    def write_yaml(self):
        with open(self.yaml_path, 'w', encoding='utf8') as fh:
            data = {
                # 'path': str(self._path),
                'path': self._path.name,
                # Fixme: float
                'date': self.mtime,
                'digest': self.digest,
                'description': self._description,
            }
            if self._models:
                data['models'] = [_.to_yaml() for _ in self.models]
            if self._subcircuits:
                data['subcircuits'] = [_.to_yaml() for _ in self.subcircuits]
            if self._inner_includes:
                data['inner_includes'] = self._inner_includes
            if self._inner_libraries:
                data['inner_libraries'] = self._inner_libraries
            # data['recursive_digest'] = self.recursive_digest
            fh.write(yaml.dump(data, sort_keys=False))

    ##############################################

    def _read_yaml(self) -> dict:
        with open(self.yaml_path, 'r', encoding='utf8') as fh:
            data = yaml.load(fh.read(), Loader=yaml.SafeLoader)
        return data

    ##############################################

    def load_yaml(self) -> None:
        self._logger.info(f"Load {self.yaml_path}")
        data = self._read_yaml()
        self._description = data['description']
        if 'models' in data:
            self._models = [Model.from_yaml(_) for _ in data['models']]
        if 'subcircuits' in data:
            self._subcircuits = [Subcircuit.from_yaml(_) for _ in data['subcircuits']]
        if 'inner_libraries' in data:
            self._inner_includes = data['inner_includes']
        if 'inner_libraries' in data:
            self._inner_libraries = data['inner_libraries']

    ##############################################

    def _compute_digest(self, func) -> str:
        with open(self._path, 'rb') as fh:
            _ = func(fh.read()).hexdigest()
        return _

    ##############################################

    def _sha1(self) -> str:
        return self._compute_digest(hashlib.sha1)

    ##############################################

    def _compute_recursive_digest(self) -> str:
        if self._inner_includes:
            return self._digest + '[' + '/'.join([_.digest for _ in self._inner_includes]) + ']'
        else:
            return self._digest

    ##############################################

    @property
    def digest(self) -> str:
        if self._digest is None:
            self._digest = self._sha1()
        return self._digest

    @property
    def recursive_digest(self) -> str:
        if self._recursive_digest is None:
            self._recursive_digest = self._compute_recursive_digest()
        return self._recursive_digest
