####################################################################################################

import os

####################################################################################################

import PySpice.Tools.Path as PathTools # Fixme: why ?

####################################################################################################

_this_file = PathTools.to_absolute_path(__file__)

class Path:

    pyspice_module_directory = PathTools.parent_directory_of(_this_file, step=2)
    config_directory = os.path.dirname(_this_file)

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file):

        return PathTools.find(config_file, Logging.directories)
