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

__all__ = [
    'is_yaml',
    'SpiceInclude',
]

####################################################################################################

from collections import namedtuple
from datetime import datetime
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

YAML_EXTENSION = '.yaml'

def is_yaml(path: Path) -> bool:
    _ = path.suffix.lower()
    return _ == YAML_EXTENSION

####################################################################################################

Pin = namedtuple('Pin', ['index', 'name', 'internal_node'])

####################################################################################################

class Mixin:

    ##############################################

    @classmethod
    def from_yaml(cls, include: 'SpiceInclude', data: dict) -> 'Mixin':
        args = [data[_] for _ in ('name', 'description')]
        return cls(include, *args)

    ##############################################

    def __init__(self, include: 'SpiceInclude', name: str, description: str = '') -> None:
        self._include = include
        self._name = name
        self._description = description

    ##############################################

    @property
    def include(self) -> 'SpiceInclude':
        return self._include

    @property
    def path(self) -> Path:
        return self._include.path

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
    def from_yaml(cls, include: 'SpiceInclude', data: dict) -> 'Model':
        args = [data[_] for _ in ('name', 'type', 'description')]
        return cls(include, *args)

    ##############################################

    def __init__(self, include: 'SpiceInclude', name: str, type_: str, description: str = '') -> None:
        super().__init__(include, name, description)
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

# Fixme: SubCircuit to be consistent with netlist
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

    _logger = _module_logger.getChild('Subcircuit')

    ##############################################

    @classmethod
    def from_yaml(cls, include: 'SpiceInclude', data: dict) -> 'Subcircuit':
        args = [data[_] for _ in ('name', 'nodes', 'description')]
        return cls(include, *args)

    ##############################################

    def __init__(self, include: 'SpiceInclude', name: str, nodes: list[str], description: str = '') -> None:
        super().__init__(include, name, description)
        self._valid = False
        self._nodes = []
        self._pin_map = {}
        self._parse_nodes(nodes)

    ##############################################

    def _parse_nodes(self, nodes: list[str]) -> None:
        self._valid = True
        for index, node_str in enumerate(nodes):
            internal_node = None
            name = None
            if isinstance(node_str, int):
                internal_node = node_str
            else:
                node_str = node_str.strip()
                i = node_str.find(' ')
                if i >= 1:
                    try:
                        internal_node = int(node_str[:i])
                    except ValueError:
                        self._logger.error(f"Invalid pin format {node_str} for {self.name}")
                    name = node_str[i:].strip()
            if internal_node and name:
                _ = Pin(index, name, internal_node)
                self._nodes.append(_)
                # Fixme: useful ?
                # self._pin_map[internal_node] = _
                self._pin_map[name] = _
            else:
                self._valid = False

    ##############################################

    def __repr__(self) -> str:
        return f'Subcircuit {self._name} {self._nodes} "{self._description}"'

    def __bool__(self) -> bool:
        return self._valid

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> Iterator[str]:
        return iter(self._nodes)

    @property
    def number_of_pins(self) -> int:
        # Fixme: self._nodes ?
        return len(self)

    ##############################################

    @property
    def pin_names(self) -> list[str]:
        return list(self._pin_map.keys())

    ##############################################

    def to_yaml(self) -> dict:
        _ = super().to_yaml()
        _.update({'nodes': self._nodes})
        return _

    ##############################################

    def map_nodes(self, **kwargs) -> list[str]:
        # Fixme: if name is not valid python id ?
        N = self.number_of_pins
        if len(kwargs) != N:
            raise NameError(f"wrong number of nodes {len(kwargs)} != {N}")
        nodes = [None] * N
        for name, node in kwargs.items():
            pin = self._pin_map[name]
            nodes[pin.index] = node
        return nodes

####################################################################################################

class SpiceInclude:

    INCLUDE_PREFIX = '.include '

    _logger = _module_logger.getChild('SpiceInclude')

    ##############################################

    def __init__(self, path: str | Path, rewrite_yaml: bool = False) -> None:
        self._path = Path(path)   # .resolve()
        self._extension = None

        self._description = ''
        self._inner_includes = []
        self._inner_libraries = []
        self._models = {}
        self._subcircuits = {}
        self._digest = None
        self._recursive_digest = None

        # Fixme: check still valid !
        if not rewrite_yaml and self.has_yaml:
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
    def mtime(self) -> datetime:
        _ = self._path.stat().st_mtime
        return datetime.fromtimestamp(_)

    @property
    def yaml_path(self) -> str:
        # self._path.parent(f'{self._path.name}{YAML_EXTENSION}')
        return self._path.with_suffix(YAML_EXTENSION)

    @property
    def has_yaml(self) -> bool:
        return self.yaml_path.exists()

    @property
    def description(self) -> str:
        return self._description

    ##############################################

    @property
    def inner_includes(self) -> Iterator[Path]:
        return iter(self._inner_includes)

    @property
    def inner_libraries(self) -> Iterator[Path]:
        return iter(self._inner_libraries)

    ##############################################

    @property
    def subcircuits(self) -> Iterator[Subcircuit]:
        # Fixme: iter ?
        return iter(self._subcircuits.values())

    @property
    def models(self) -> Iterator[Model]:
        return iter(self._models.values())

    def __getitem__(self, name: str) -> Subcircuit | Model:
        if name in self._subcircuits:
            return self._subcircuits[name]
        elif name in self._models:
            return self._models[name]
        else:
            message = f"Library {self.path} contains:{NEWLINE}"
            def add_line(item):
                nonlocal message
                message += f'    - {item}{NEWLINE}'
            message += f"  Subcircuits:{NEWLINE}"
            for _ in self._subcircuits:
                add_line(_)
            for _ in self._models:
                add_line(_)
            self._logger.error(message)
            raise KeyError(name)

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
            _ = Subcircuit(self, subcircuit.name, subcircuit.nodes)
            self._subcircuits[_.name] = _
        if spice_file.is_only_model:
            for model in spice_file.models:
                # name = self._suffix_name(model.name)
                _ = Model(self, model.name, model.type)
                self._models[_.name] = _

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
                'date': self.mtime.isoformat(),
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
            models = [Model.from_yaml(self, _) for _ in data['models']]
            self._models = {_.name: _ for _ in models}
        if 'subcircuits' in data:
            subcircuits = [Subcircuit.from_yaml(self, _) for _ in data['subcircuits']]
            self._subcircuits = {_.name: _ for _ in subcircuits}
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
