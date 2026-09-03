####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = []

####################################################################################################

import logging
from typing import TYPE_CHECKING

from . import BasicElement, HighLevelElement
from .Element import Element, ElementParameterMetaClass
from .Netlist import Netlist

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def _get_elements(module: ModuleType) -> list[type[Element]]:
    return [
        _
        for _ in module.__dict__.values()
        if type(_) is ElementParameterMetaClass and _.PREFIX is not None
    ]

####################################################################################################

def _init() -> None:
    """Add a method to create elements to the Netlist class.

    .. code-block::

        circuit.R(*args, **kwargs)
        # =>
        R(circuit, *args, **kwargs)

    """

    spice_elements = _get_elements(BasicElement)
    high_level_elements = _get_elements(HighLevelElement)

    for element_class in spice_elements + high_level_elements:

        def make_wrapper(element_class: type[Element]) -> Callable:
            def function(self, *args, **kwargs):
                return element_class(self, *args, **kwargs)
            # Preserve docstrings for element shortcuts
            # Fixme: But Sphinx redumps it...
            function.__doc__ = element_class.__doc__
            function.ELEMENT_CLASS = element_class  # ty: ignore[unresolved-attribute]
            return function

        wrapper = make_wrapper(element_class)

        def register(name: str) -> None:
            # _module_logger.debug("Add device shortcut {} for class {}".format(name, element_class))
            setattr(Netlist, name, wrapper)  # ruff: ignore[function-uses-loop-variable]

        register(element_class.__name__)
        if element_class in spice_elements:
            if hasattr(element_class, 'ALIAS'):
                register(element_class.ALIAS)  # ty: ignore[invalid-argument-type]
            if hasattr(element_class, 'LONG_ALIAS'):
                register(element_class.LONG_ALIAS)  # ty: ignore[invalid-argument-type]

_init()
