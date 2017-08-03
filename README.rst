.. -*- Mode: rst -*-

.. -*- Mode: rst -*-

..
   |PySpiceUrl|
   |PySpiceHomePage|_
   |PySpiceDoc|_
   |PySpice@github|_
   |PySpice@readthedocs|_
   |PySpice@readthedocs-badge|
   |PySpice@pypi|_

.. |ohloh| image:: https://www.openhub.net/accounts/230426/widgets/account_tiny.gif
   :target: https://www.openhub.net/accounts/fabricesalvaire
   :alt: Fabrice Salvaire's Ohloh profile
   :height: 15px
   :width:  80px

.. |PySpiceUrl| replace:: https://pyspice.fabrice-salvaire.fr

.. |PySpiceHomePage| replace:: PySpice Home Page
.. _PySpiceHomePage: https://pyspice.fabrice-salvaire.fr

.. |PySpice@readthedocs-badge| image:: https://readthedocs.org/projects/pyspice/badge/?version=latest
   :target: http://pyspice.readthedocs.org/en/latest

.. |PySpice@github| replace:: https://github.com/FabriceSalvaire/PySpice
.. .. _PySpice@github: https://github.com/FabriceSalvaire/PySpice

.. |PySpice@pypi| replace:: https://pypi.python.org/pypi/PySpice
.. .. _PySpice@pypi: https://pypi.python.org/pypi/PySpice

.. |Build Status| image:: https://travis-ci.org/FabriceSalvaire/PySpice.svg?branch=master
   :target: https://travis-ci.org/FabriceSalvaire/PySpice
   :alt: PySpice build status @travis-ci.org

.. |Pypi Version| image:: https://img.shields.io/pypi/v/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice last version

.. |Pypi License| image:: https://img.shields.io/pypi/l/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice license

.. |Pypi Python Version| image:: https://img.shields.io/pypi/pyversions/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice python version

..  coverage test
..  https://img.shields.io/pypi/status/Django.svg
..  https://img.shields.io/github/stars/badges/shields.svg?style=social&label=Star

.. End
.. -*- Mode: rst -*-

.. |Ngspice| replace:: Ngspice
.. _Ngspice: http://ngspice.sourceforge.net

.. |Python| replace:: Python
.. _Python: http://python.org

.. |PyPI| replace:: PyPI
.. _PyPI: https://pypi.python.org/pypi

.. |Numpy| replace:: Numpy
.. _Numpy: http://www.numpy.org

.. |Matplotlib| replace:: Matplotlib
.. _Matplotlib: http://matplotlib.org

.. |CFFI| replace:: CFFI
.. _CFFI: http://cffi.readthedocs.org/en/latest/

.. |IPython| replace:: IPython
.. _IPython: http://ipython.org

.. |Sphinx| replace:: Sphinx
.. _Sphinx: http://sphinx-doc.org

.. |Modelica| replace:: Modelica
.. _Modelica: http://www.modelica.org

.. |Kicad| replace:: Kicad
.. _Kicad: http://www.kicad-pcb.org

.. |Circuit_macros| replace:: Circuit_macros
.. _Circuit_macros: http://ece.uwaterloo.ca/~aplevich/Circuit_macros

.. End

=========
 PySpice
=========

Developed by `Fabrice Salvaire <http://fabrice-salvaire.fr>`_.

The official PySpice Home Page is located at |PySpiceUrl|

`PyParis2017 / Circuit Simulation using Python, by Fabrice Salvaire
<https://www.slideshare.net/PoleSystematicParisRegion/pyparis2017-circuit-simulation-using-python-by-fabrice-salvaire>`_
: talk given at the `PyParis 2017 <http://pyparis.org/>`_ conference
(`PDF file <https://pyspice.fabrice-salvaire.fr/pyparis-2017-talk.pdf>`_)

|Pypi License|
|Pypi Python Version|

|Pypi Version|

-----

.. -*- Mode: rst -*-

V0.4.0
------

 * Git repository cleanup: filtered generated doc and useless files so as to shrink the repository size
 * Improved documentation generator: Implemented :code:`format` for RST content and Tikz figure.
 * Improved unit support: It implements now the International System of Units.
   And we can now use unit helper like :code:`u_mV` or compute the value of :code:`1.2@u_kΩ / 2@u_mA`.
   The relevant documentation is on this `page <api/PySpice/Unit.html>`_.
 * Added the Simulation instance to the Analysis class.
 * Refactored simulation parameters as classes.

V0.3.2
------

 * fixed CCCS and CCVS

V0.3.1
------

 * fixed ngspice shared

V0.3.0
------

 * Added an example to show how to use the NgSpice Shared Simulation Mode.
 * Completed the Spice netlist parser and added examples, we could now use a schematic editor
   to define the circuit.  The program *cir2py* translates a circuit file to Python.

.. End

.. -*- Mode: rst -*-


PySpice is a |Python|_ 3 library which interplay with Berkeley SPICE, the industrial circuit
simulator reference.

SPICE (Simulation Program with Integrated Circuit Emphasis) was developed at the Electronics
Research Laboratory of the University of California, Berkeley in 1973 by Laurence Nagel with
direction from his research advisor, Prof. Donald Pederson. Then Spice emerged as an industrial
standard through its descendants and is still the reference 40 years later.

PySpice is born as a personal project to relearn electronics where circuit simulation is a part of
this goal. Since I use the Python language every day, I quickly feel the need to plug SPICE and Python.

The aim of PySpice is to address several needs:

 * SPICE language is fine to describe circuits, but it lacks a real language for circuit
   steering. By contrast Python is a powerful high level, oriented object and dynamic language which
   is perfectly suited for steering and reusing circuit. But it comes at the price its more general
   syntax is less fluent than SPICE for circuit description.

 * Ngspice provides some extension to Berkeley SPICE for data analysis, but its interactive
   environment or TCL module are now outdated. By contrast Python has scientific framework like
   |Numpy|_ and |Matplotlib|_ that compete with Matlab.

 * Ngspice source code is derived from Berkeley SPICE and thus has a very old basis. Moreover the
   sources are poorly documented. So it is really difficult to understand how it works and modify
   it. PySpice could serve to easily experiment extension.

As opposite to other SPICE derivatives, PySpice focus on programming and not on graphical user
interface. Thus it doesn't feature a schematic capture editor and we cannot pickup a node or an
element and plot the associated waveform.  Moreover we can notice the |Modelica|_ language treats
diagrams as annotations.  A choice which I consider judicious.  Thus we can imagine to follow the
same principle and extend PySpice later.

==========
 Features
==========

.. -*- Mode: rst -*-

The main features of PySpice are:

 * actually PySpice only supports |Ngspice|_
 * an oriented-object API to describe circuit in a way similar to SPICE
 * a library and model manager that index recursively a directory
 * an (experimental) SPICE netlist parser.  |Kicad|_ can be used as schematic editor to simplify the
   netlist writing.
 * a circuit can be simulated using a subprocess (aka server mode) or using the NgSpice shared library,
   NgSpice vectors are converted to Numpy array
 * the NgSpice shared library permits to plug voltage/current sources from Python to NgSpice and vice versa.
 * some data analysis add-ons

Since PySpice is born with a learning goal, many examples are provided with the sources.  These
examples could serve as learning materials. A tool to generate an HTML and PDF documentation is
included in the *tools* directory. This tool could be extended to generate IPython Notebook as well.

..
    * an incomplete SPICE parser (mainly used for the library and model indexer)

    * a circuit can be simulated using a subprocess (aka server mode) or using the NgSpice shared
      library, NgSpice vectors are converted to Numpy array the NgSpice shared library permits to interact
      with the simulator and provides Python callback for external voltage and current source

    * implement a SPICE to Python converted using the parser. It could be used for the following
      workflow: quick circuit sketching using  > SPICE netlist > spice2python > PySpice which
      could help for complex circuit.

.. end

==================
 Planned Features
==================

These features are planned in the future:

 * implement a basic simulator featuring passive element like resistor, capacitor and inductor.
 * implement a Modelica backend. |Modelica|_ is a very interesting solution for transient analysis.

================
 Advertisements
================

Users should be aware of these advertisements.

.. .. Warning:: The API is quite unstable until now. Some efforts is made to have a smooth API.

.. Warning:: Ngspice and PySpice are provided without any warranty. Thus you must use it with care
	     for real design. Best is to cross check the simulation using an industrial grade
	     simulator.

.. Warning:: Simulation is a design tool and not a perfect description of the real world.

.. End

.. -*- Mode: rst -*-

.. _installation-page:


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

.. End
