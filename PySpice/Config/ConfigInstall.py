####################################################################################################

from pathlib import Path

import sys

####################################################################################################

from PySpice.Tools import PathTools

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

_this_file = Path(__file__).absolute()

class Path:

    pyspice_module_directory = _this_file.parents[1]
    config_directory = _this_file.parent

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file):
        return PathTools.find(config_file, Logging.directories)
