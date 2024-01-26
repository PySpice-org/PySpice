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
