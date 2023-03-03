####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

class Manufacturer:

    ##############################################

    def __init__(self,
                 name,
                 url=None,
    ):

        self._name = name
        self._url = url

    ##############################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

####################################################################################################

class Footprint:

    ##############################################

    def __init__(self,
                 name,
    ):

        self._name = name

    ##############################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

####################################################################################################

class Device:

    ##############################################

    def __init__(self,
                 name,
                 manufacturer,
                 datasheet_url=None,
                 model_url=None
    ):

        # part
        # part_number
        # footprint
        # description
        # device_category x/y
        # pins
        # features / parameters

        self._name = name

    ##############################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
