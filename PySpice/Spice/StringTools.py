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

__all__ = [
    'join_dict',
    'join_lines',
    'join_list',
    'prefix_lines',
    'remove_multi_space',
]

####################################################################################################

from typing import Any, Iterable
import os

from .unit import str_spice

####################################################################################################

NEWLINE = os.linesep

####################################################################################################

def prefix_lines(items: Iterable[Any], prefix: str = '') -> list[str]:
    return [
        prefix + str(item)
        for item in items
        if item is not None
    ]   # Fixme: and item

####################################################################################################

def join_lines(items: Iterable[Any], prefix: str = '') -> str:
    return NEWLINE.join(prefix_lines(items, prefix))

####################################################################################################

def join_list(items: Iterable[Any]) -> str:
    # return ' '.join([str_spice(item)
    #                  for item in items
    #                  if item is not None and str_spice(item)])
    values = []
    for item in items:
        if item is not None:
            str_value = str_spice(item)
            if str_value:
                values.append(str_value)
    return ' '.join(values)

####################################################################################################

####################################################################################################
#
# Note:
#   PR #136 has non understood changes
#     https://github.com/FabriceSalvaire/PySpice/pull/136/files
#
####################################################################################################

def join_dict(d: dict[str, Any]) -> str:
    # Fixme: remove trailing _ to key ???
    return ' '.join([
        f'{key}={str_spice(value)}'
        for key, value in sorted(d.items())
        if value is not None
    ])

####################################################################################################

def remove_multi_space(txt: str) -> str:
    """Remove multi-space"""
    # Fixme: tab ???
    new_txt = ''
    last_c = None
    for c in txt:
        if c == ' ' and last_c == ' ':
            continue
        new_txt += c
        last_c = c
    return new_txt
