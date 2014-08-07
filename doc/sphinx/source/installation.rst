.. -*- Mode: rst -*-

.. _installation-page:

==============
 Installation
==============

The PySpice project is hosted at github http://github.com/FabriceSalvaire/PySpice

Ngspice Compilation
-------------------

Usually Ngspice is available as a package in the major Linux distributions. But I recommend to check
the compilation options before to use it extensively. For example the Fedora package enables too
many experimental codes that have side effects. The recommended way to compile Ngspice is given in
the manual and the :file:`INSTALLATION` file. Ngspice is an example of complex software where we
should not enable everything without care.

.. warning::

  For the following, the compilation option **--enable-ndev** is known to broke the server mode.

.. End
