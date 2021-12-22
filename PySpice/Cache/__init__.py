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

# Simulation outputs should be identical if
#   same simulator and version
#   same inputs

__all__ = ["SimulationCache"]

####################################################################################################

from pathlib import Path
import hashlib

# http://www.grantjenks.com/docs/diskcache
from diskcache import Cache

####################################################################################################

class SpiceInclude:

    INCLUDE_PREFIX = '.include '

    ##############################################

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._inner_includes = []
        self._walk()
        self._digest = self.sha1()
        self._recursive_digest = self._compute_recursive_digest()

    ##############################################

    @property
    def path(self) -> Path:
        return self._path

    ##############################################

    def _compute_digest(self, func) -> str:
        with open(self._path, 'rb') as fh:
            _ = func(fh.read()).hexdigest()
        return _

    ##############################################

    def sha1(self) -> str:
        return self._compute_digest(hashlib.sha1)

    ##############################################

    @classmethod
    def parse_include(self, line):
        line = line.strip()
        if line.startswith(self.INCLUDE_PREFIX):
            path = line[len(self.INCLUDE_PREFIX):].strip()
            if path:
                return Path(path)
        return None

    ##############################################

    def _walk(self) -> None:
        with open(self._path, 'r') as fh:
            for line in fh.readlines():
                path = self.parse_include(line)
                if path is not None:
                    include = SpiceInclude(path)
                    self._inner_includes.append(include)

    ##############################################

    def _compute_recursive_digest(self) -> str:
        if self._inner_includes:
            return self._digest + '[' + '/'.join([_.digest for _ in self._inner_includes]) + ']'
        else:
            return self._digest

    ##############################################

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def recursive_digest(self) -> str:
        return self._recursive_digest

    @property
    def inner_includes(self) -> str:
        return iter(self._inner_includes)

####################################################################################################

class SimulationCache:

    ##############################################

    def __init__(self, path: str | Path=None):
        """
        Cache directory will be set to a temporary directory like "/tmp/diskcache-...", if *Path* is None.
        """
        self._cache = Cache(path)

    ##############################################

    def __del__(self):
        # Each thread that accesses a cache should also call close on the cache.
        self._cache.close()

    ##############################################

    @property
    def impl(self) -> Cache:
        return self._cache

    @property
    def directory(self) -> str:
        return self._cache.directory

    ##############################################

    def simulation_key(self, simulation) -> str:
        raw_spice_code = str(simulation)
        lines = []
        # Replace .include lines by recursive digest
        for line in raw_spice_code.splitlines():
        #  for path in simulation.circuit.includes:
            path = SpiceInclude.parse_include(line)
            if path is not None:
                include = SpiceInclude(path)
                lines.append(f'.include {include.path.name} {include.recursive_digest}')
            else:
                lines.append(line)
        # Replace os.linesep to a portable separator
        spice_code = '@@'.join(lines)
        return f'{simulation.simulator_name}/{simulation.simulator_version}/{spice_code}'

    ##############################################

    def add(self, analysis):
        pass

    ##############################################

    def get(self, simulation):
        pass

####################################################################################################

class CachedSimulation:

    ##############################################

    def __init__(self, spice_code):
        pass
