####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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
import re

####################################################################################################

from ..Tools.File import Directory
from .Parser import SpiceParser

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

    def __init__(self, root_path, recurse=False, section=None):

        self._directory = Directory(root_path).expand_vars_and_user()

        self._subcircuits = {}
        self._models = {}

        for path in self._directory.iter_file():
            extension = path.extension.lower()
            if extension in self.EXTENSIONS:
                self._logger.debug("Parse {}".format(path))
                try:
                    spice_parser = SpiceParser(path=path, recurse=recurse, section=section)
                    for lib in spice_parser.incl_libs:
                        self._subcircuits.update(lib._subcircuits)
                        self._models.update(lib._models)
                except Exception as e:
                    # Parse problem with this file, so skip it and keep going.
                    self._logger.warn("Problem parsing {path} - {e}".format(**locals()))
                    continue
                if spice_parser.is_only_subcircuit():
                    for subcircuit in spice_parser.subcircuits:
                        name = self._suffix_name(subcircuit.name, extension)
                        self._subcircuits[name] = path
                elif spice_parser.is_only_model():
                    for model in spice_parser.models:
                        name = self._suffix_name(model.name, extension)
                        self._models[name] = path

    ##############################################

    @staticmethod
    def _suffix_name(name, extension):

        if extension.endswith('@xyce'):
            name += '@xyce'

        return name

    ##############################################

    def __getitem__(self, name):

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
    def subcircuits(self):
        """ Dictionary of sub-circuits """
        return iter(self._subcircuits)

    @property
    def models(self):
        """ Dictionary of models """
        return iter(self._models)

    # ##############################################

    # def iter_on_subcircuits(self):
    #     return self._subcircuits.itervalues()

    # ##############################################

    # def iter_on_models(self):
    #     return self._models.itervalues()

    # ##############################################

    def search(self, s):
        """ Return dict of all models/subcircuits with names matching regex s. """
        matches = {}
        models_subcircuits = {**self._models, **self._subcircuits}
        for name, mdl_subckt in models_subcircuits.items():
            if re.search(s, name):
                matches[name] = mdl_subckt
        return matches
