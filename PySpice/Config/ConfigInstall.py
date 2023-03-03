####################################################################################################

import os
import sys

####################################################################################################

import PySpice.Tools.Path as PathTools # Fixme: why ?

####################################################################################################

class OsFactory:

    ##############################################

    def __init__(self):

        if sys.platform.startswith('linux'):
            self._name = 'linux'
        elif sys.platform.startswith('win'):
            self._name = 'windows'
        elif sys.platform.startswith('darwin'):
            self._name = 'osx'

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def on_linux(self):
        return self._name == 'linux'

    @property
    def on_windows(self):
        return self._name == 'windows'

    @property
    def on_osx(self):
        return self._name == 'osx'

OS = OsFactory()

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
