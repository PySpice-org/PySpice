####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['DeviceModel']

####################################################################################################

from collections.abc import KeysView
from typing import Self

from .StringTools import join_dict

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

    def __init__(self, name: str, modele_type: str, **parameters: str) -> None:
        # Fixme: parameters as UnitValueShorcut ?
        self._name = str(name)
        self._model_type = str(modele_type)

        self._parameters = {}
        for key, value in parameters.items():
            if key.endswith('_'):
                key = key[:-1]
            self._parameters[key] = value

    ##############################################

    def clone(self) -> Self:
        # Fixme: clone parameters ???
        return self.__class__(self._name, self._model_type, self._parameters)

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def model_type(self) -> str:
        return self._model_type

    @property
    def parameters(self) -> KeysView:
        return self._parameters.keys()

    ##############################################

    def __getitem__(self, name: str) -> str:
        return self._parameters[name]

    ##############################################

    def __getattr__(self, name: str) -> str:
        try:
            return self._parameters[name]
        except KeyError as exception:
            if name.endswith('_'):
                return self._parameters[name[:-1]]
            raise exception

    ##############################################

    def __repr__(self) -> str:
        return str(self.__class__) + ' ' + self.name

    ##############################################

    def __str__(self) -> str:
        parameters = join_dict(self._parameters)
        return f".model {self._name} {self._model_type} ({parameters})"
