####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
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

__all__ = ['DeviceModel']

####################################################################################################

from PySpice.Tools.StringTools import join_dict

####################################################################################################

class DeviceModel:

    """This class implements a device model.

    Ngspice model types:

    +------+-------------------------------+
    | Code + Model Type                    |
    +------+-------------------------------+
    | R    + Semiconductor resistor model  |
    +------+-------------------------------+
    | C    + Semiconductor capacitor model |
    +------+-------------------------------+
    | L    + Inductor model                |
    +------+-------------------------------+
    | SW   + Voltage controlled switch     |
    +------+-------------------------------+
    | CSW  + Current controlled switch     |
    +------+-------------------------------+
    | URC  + Uniform distributed RC model  |
    +------+-------------------------------+
    | LTRA + Lossy transmission line model |
    +------+-------------------------------+
    | D    + Diode model                   |
    +------+-------------------------------+
    | NPN  + NPN BJT model                 |
    +------+-------------------------------+
    | PNP  + PNP BJT model                 |
    +------+-------------------------------+
    | NJF  + N-channel JFET model          |
    +------+-------------------------------+
    | PJF  + P-channel JFET model          |
    +------+-------------------------------+
    | NMOS + N-channel MOSFET model        |
    +------+-------------------------------+
    | PMOS + P-channel MOSFET model        |
    +------+-------------------------------+
    | NMF  + N-channel MESFET model        |
    +------+-------------------------------+
    | PMF  + P-channel MESFET model        |
    +------+-------------------------------+

    """

    ##############################################

    def __init__(self, name, modele_type, **parameters):

        self._name = str(name)
        self._model_type = str(modele_type)

        self._parameters = {}
        for key, value in parameters.items():
            if key.endswith('_'):
                key = key[:-1]
            self._parameters[key] = value

    ##############################################

    def clone(self):
        # Fixme: clone parameters ???
        return self.__class__(self._name, self._model_type, self._parameters)

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def model_type(self):
        return self._model_type

    @property
    def parameters(self):
        return self._parameters.keys()

    ##############################################

    def __getitem__(self, name):
        return self._parameters[name]

    ##############################################

    def __getattr__(self, name):
        try:
            return self._parameters[name]
        except KeyError as exception:
            if name.endswith('_'):
                return self._parameters[name[:-1]]
            raise exception

    ##############################################

    def __repr__(self):
        return str(self.__class__) + ' ' + self.name

    ##############################################

    def __str__(self):
        parameters = join_dict(self._parameters)
        return f".model {self._name} {self._model_type} ({parameters})"
