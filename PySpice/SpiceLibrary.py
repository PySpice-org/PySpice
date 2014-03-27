####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

from PySpice.File import Directory
from PySpice.SpiceParser import SpiceParser

####################################################################################################

class SpiceLibrary(object):

    ##############################################

    def __init__(self, root_path):

        self._directory = Directory(root_path)

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
        return self._subcircuits

    @property
    def models(self):
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
