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

.. |Tikz| replace:: Tikz
.. _Tikz: http://www.texample.net/tikz

.. End

=============================================================================
 PySpice : Simulate Electronic Circuit using Python and the Ngspice Simulator
=============================================================================

|Pypi License|
|Pypi Python Version|

|Pypi Version|

Overview
========

What is PySpice ?
-----------------

PySpice is a Python module which interface |Python|_ and the |Ngspice|_ circuit
simulator.

What are the main features ?
----------------------------

* licensed under **GPLv3** therms
* support **Linux**, **Windows** and Mac **OS X** platforms
* implement an **Ngspice shared library binding** using CFFI which support external sources
* implement (partial) **SPICE netlist parser**
* implement an **Oriented Object API** to define circuit
* export simulation output to |Numpy|_ arrays
* plot using |Matplotlib|_
* handle **units**
* work with **Kicad schematic editor**
* implement a **documentation generator**
* provides many **examples**

Where is the Documentation ?
----------------------------

The documentation is available on the |PySpiceHomePage|_.

How to install it ?
-------------------

Look at the `installation <https://pyspice.fabrice-salvaire.fr/installation.html>`_ section in the documentation.

Credits
=======

Authors: `Fabrice Salvaire <http://fabrice-salvaire.fr>`_

News
====

.. -*- Mode: rst -*-

.. no title here

V1.1.0
------

 * Enhanced shared mode
 * Shared mode is now set as default on Linux

V1.0.0
------

 * Bump version to v1.0.0 since it just works!
 * Support Windows platform using Ngspice shared mode
 * Fixed shared mode
 * Fixed and completed Spice parser : tested on example's libraries

V0.4.2
------

 * Fixed Spice parser for lower case device prefix.

V0.4.0
------

 * Git repository cleanup: filtered generated doc and useless files so as to shrink the repository size.
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

.. End
