####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from ..Tools.File import Directory
from .Parser import SpiceParser

####################################################################################################

class SpiceLibrary(object):

    """ This class implements a Spice sub-circuits and models library.

    A library is a directory which is recursively scanned for '.lib' file and parsed for sub-circuit
    and models definitions.

    Example of usage::

        spice_library = SpiceLibrary('/some/path/')

    If the directory hierarchy contains a file that define a 1N4148 sub-circuit then we can retrieve
    the file path using::

        spice_library['1N4148']

    """

    ##############################################

    def __init__(self, root_path):

        self._directory = Directory(root_path).expand_vars_and_user()

        self._subcircuits = {}
        self._models = {}

        for path in self._directory.iter_file():
            if path.extension == '.lib':
                spice_parser = SpiceParser(path)
                if spice_parser.is_only_subcircuit():
                    for subcircuit in spice_parser.subcircuits:
                        self._subcircuits[subcircuit.name] = path
                elif spice_parser.is_only_model():
                    for model in spice_parser.models:
                        self._models[model.name] = path

    ##############################################

    def __getitem__(self, name):

        if name in self._subcircuits:
            return self._subcircuits[name]
        elif name in self._models:
            return self._models[name]
        else:
            raise KeyError(name)

    ##############################################

    @property
    def subcircuits(self):
        """ Dictionary of sub-circuits """
        return self._subcircuits

    @property
    def models(self):
        """ Dictionary of models """
        return self._models

    # ##############################################

    # def iter_on_subcircuits(self):
    #     return self._subcircuits.itervalues()

    # ##############################################

    # def iter_on_models(self):
    #     return self._models.itervalues()

####################################################################################################
# 
# End
# 
####################################################################################################
