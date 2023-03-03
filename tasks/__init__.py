####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2019 Fabrice Salvaire
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

# http://www.pyinvoke.org

####################################################################################################

from invoke import task, Collection
 # import sys

####################################################################################################

# PYSPICE_SOURCE_PATH = Path(__file__).resolve().parent

####################################################################################################

from . import anaconda
from . import clean
from . import doc
from . import git
from . import github
from . import ngspice
from . import release
from . import test

ns = Collection()
ns.add_collection(Collection.from_module(anaconda))
ns.add_collection(Collection.from_module(clean))
ns.add_collection(Collection.from_module(doc))
ns.add_collection(Collection.from_module(git))
ns.add_collection(Collection.from_module(github))
ns.add_collection(Collection.from_module(ngspice))
ns.add_collection(Collection.from_module(release))
ns.add_collection(Collection.from_module(test))
