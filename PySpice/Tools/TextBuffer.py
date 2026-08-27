####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'TextBuffer',
]

####################################################################################################

import os

####################################################################################################

class TextBuffer:

    ##############################################

    def __init__(self):
        self._lines = []

    ##############################################

    def _append_line(self, line):
        if line is not None:
            _ = str(line)
            if _:
                self._lines.append(_)

    ##############################################

    def __iadd__(self, obj):
        if isinstance(obj, (list, tuple)):
            for _ in obj:
                self._append_line(_)
        else:
            self._append_line(obj)
        return self

    ##############################################

    def __str__(self):
        return os.linesep.join(self._lines)
