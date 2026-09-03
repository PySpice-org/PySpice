####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['TextBuffer']

####################################################################################################

import os
from collections.abc import Iterable
from typing import Self

####################################################################################################

class TextBuffer:

    # Note: object.__str__() call object.__repr__()

    ##############################################

    def __init__(self) -> None:
        self._lines: list[str] = []

    ##############################################

    def _append_line(self, line: str | object | None) -> None:
        if line is not None:
            _ = str(line)
            if _:
                self._lines.append(_)

    ##############################################

    def __iadd__(self, obj: tuple | list | str | object | None) -> Self:
        match obj:
            case tuple() | list():  # str is an Iterable
                for _ in obj:
                    self._append_line(_)
            case _:
                self._append_line(obj)
        return self

    ##############################################

    def __str__(self) -> str:
        return os.linesep.join(self._lines)
