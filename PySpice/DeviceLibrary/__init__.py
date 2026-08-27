####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

class Manufacturer:

    ##############################################

    def __init__(
        self,
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

    def __init__(
        self,
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

    def __init__(
        self,
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
