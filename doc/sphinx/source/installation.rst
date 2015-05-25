.. -*- Mode: rst -*-

.. _installation-page:

.. include:: project-links.txt
.. include:: abbreviation.txt

==============
 Installation
==============

The installation of PySpice by itself is quite simple. However it will be easier to get the
dependencies on a Linux desktop.

Dependencies
------------

PySpice requires the following dependencies:

 * |Python|_ 3
 * |Numpy|_
 * |Matplotlib|_
 * |Ngspice|_
 * |CFFI|_ (only required for Ngspice shared)

Also it is recommanded to have these Python modules:

 * |IPython|_
 * pip
 * virtualenv

For development, you will need in addition:

 * |Sphinx|_
 * circuit_macros and a LaTeX environment

Ngspice Compilation
-------------------

Usually Ngspice is available as a package in the major Linux distributions. But I recommend to check
the compilation options before to use it extensively. For example the Fedora package enables too
many experimental codes that have side effects. The recommended way to compile Ngspice is given in
the manual and the ``INSTALLATION`` file. Ngspice is an example of complex software where we should
not enable everything without care.

.. :file:`INSTALLATION`

.. warning::

  For the following, the compilation option **--enable-ndev** is known to broke the server mode.

Installation from PyPi Repository
---------------------------------

PySpice is made available on the |Pypi|_ repository at |PySpice@pypi|

Run this command to install the last release:

.. code-block:: sh

  pip install PySpice

Installation from Source
------------------------

The PySpice source code is hosted at |PySpice@github|

To clone the Git repository, run this command in a terminal:

.. code-block:: sh

  git clone git@github.com:FabriceSalvaire/PySpice.git

Then to build and install PySpice run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install

.. End
