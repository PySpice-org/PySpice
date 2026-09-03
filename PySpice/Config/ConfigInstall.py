####################################################################################################

import sys
from pathlib import Path as plPath  # Fixme: due to Path

from PySpice.Tools import PathTools

####################################################################################################

class OsFactory:

    ##############################################

    def __init__(self) -> None:
        _ = sys.platform
        if _.startswith('linux'):
            self._name = 'linux'
        elif _.startswith('win'):
            self._name = 'windows'
        elif _.startswith('darwin'):
            self._name = 'osx'

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def on_linux(self) -> bool:
        return self._name == 'linux'

    @property
    def on_windows(self) -> bool:
        return self._name == 'windows'

    @property
    def on_osx(self) -> bool:
        return self._name == 'osx'

OS = OsFactory()

####################################################################################################

_this_file = plPath(__file__).absolute()

class Path:
    pyspice_module_directory = _this_file.parents[1]
    config_directory = _this_file.parent

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file: str) -> plPath:
        return PathTools.find(config_file, Logging.directories)
