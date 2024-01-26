####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

__all__ = ['expand_path', 'find', 'walk']

####################################################################################################

from typing import Iterator

import os
from pathlib import Path

####################################################################################################

def find(file_name: str, directories: list[str]) -> Path:
    # Fixme: bytes ???
    #  on Linux path are bytes, thus some files can be invalid utf8...
    # if isinstance(directories, bytes):
    #     directories = (directories,)
    for directory in directories:
        directory = Path(directory)
        # for directory_path, _, file_names in os.walk(directory):
        for directory_path, _, file_names in directory.walk():
            directory_path = Path(directory_path)
            if file_name in file_names:
                return directory_path.joinpath(file_name)
    raise NameError(f"File {file_name} not found in directories {directories}")

####################################################################################################

def expand_path(path: Path | str) -> Path:
    # Substrings of the form $name or ${name} are replaced by the value of environment variable name.
    # On Unix and Windows, return the argument with an initial component of ~ or ~user
    # replaced by that user’s home directory.
    _ = os.path.expandvars(path)
    return Path(_).expanduser().absolute()

####################################################################################################

def walk(path: Path | str, followlinks: bool = False) -> Iterator[Path]:
    for root, _, files in Path(path).walk(follow_symlinks=followlinks):
        for filename in files:
            yield Path(root).joinpath(filename)
