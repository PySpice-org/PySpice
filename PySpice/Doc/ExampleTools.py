####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['find_libraries', 'LIBRARY_PATH']

####################################################################################################

from pathlib import Path
import logging
import os
import sys

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

LIBRARY_PATH = 'spice-library'

def find_libraries(root: str='examples') -> Path:
    try:
        library_path = os.environ['PySpiceLibraryPath']
    except KeyError:
        examples_root = Path(sys.argv[0]).resolve()   # path of the Python file
        while True:
            examples_root = examples_root.parents[1]
            if examples_root.name == root:
                break
        library_path = examples_root.joinpath(LIBRARY_PATH)
    _module_logger.info(f'SPICE library path is {library_path}')
    return library_path
