.. -*- Mode: rst -*-

.. _installation-page:

.. include:: project-links.txt
.. include:: abbreviation.txt

==============
 Installation
==============

The installation of PySpice by itself is quite simple. However it will be easier to get the
dependencies on Linux.

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

.. * pip
.. * virtualenv

To generate the documentation, you will need in addition:

 * |Sphinx|_
 * circuit_macros and a LaTeX environment

Ngspice Compilation
-------------------

Usually Ngspice is available as a package on the most popular Linux distributions. But I recommend
to **check the compilation options** before to use it extensively. For example the Fedora package
enables too many experimental codes that have side effects. The recommended way to compile Ngspice
is given in the manual and in the ``INSTALLATION`` file. Ngspice is an example of complex software
where we should not enable everything without care.

.. :file:`INSTALLATION`

.. warning::

  Compilation option **--enable-ndev** is known to broke the server mode.

Installation from PyPi Repository
---------------------------------

PySpice is available on the Python Packages |Pypi|_ repository at |PySpice@pypi|

Run this command in the console to install the latest release:

.. code-block:: sh

  pip install PySpice

How to get the Examples
-----------------------

Examples are not installed by ``pip`` or ``setup.pip``. The installation process only install
PySpice on your Python environment.

**You have to download the PySpice archive or clone the Git repository to get the examples.** See "Installation from Source".

Installation from Source
------------------------

The PySpice source code is hosted at |PySpice@github|

.. add link to pages ...

You have to solution to get the source code, the first one is to clone the repository, but if you
are not familiar with Git then you can simply download an archive either from the PySpice Pypi page
(at the bottom) or the GitHub page (see clone or download button).

To clone the Git repository, run this command in a console:

.. code-block:: sh

  git clone git@github.com:FabriceSalvaire/PySpice.git

Then to build and install PySpice run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install

.. End
