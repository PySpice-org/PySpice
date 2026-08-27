####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
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

from typing import Any
from collections.abc import Iterable
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
