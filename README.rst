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

.. |PySpiceUrl| replace:: https://pyspice.fabrice-salvaire.fr

.. |PySpiceHomePage| replace:: PySpice Home Page
.. _PySpiceHomePage: https://pyspice.fabrice-salvaire.fr

.. .. |PySpice@readthedocs-badge| image:: https://readthedocs.org/projects/pyspice/badge/?version=latest
..   :target: http://pyspice.readthedocs.org/en/latest

.. |PySpice@github| replace:: https://github.com/FabriceSalvaire/PySpice
.. .. _PySpice@github: https://github.com/FabriceSalvaire/PySpice

.. |PySpice@pypi| replace:: https://pypi.python.org/pypi/PySpice
.. .. _PySpice@pypi: https://pypi.python.org/pypi/PySpice

.. |Pypi Version| image:: https://img.shields.io/pypi/v/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice last version

.. |Pypi License| image:: https://img.shields.io/pypi/l/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice license

.. |Pypi Python Version| image:: https://img.shields.io/pypi/pyversions/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice python version

.. |Build Status| image:: https://travis-ci.org/FabriceSalvaire/PySpice.svg?branch=master
   :target: https://travis-ci.org/FabriceSalvaire/PySpice
   :alt: PySpice build status @travis-ci.org

.. |ohloh| image:: https://www.openhub.net/accounts/230426/widgets/account_tiny.gif
   :target: https://www.openhub.net/accounts/fabricesalvaire
   :alt: Fabrice Salvaire's Ohloh profile
   :height: 15px
   :width:  80px

..  coverage test
..  https://img.shields.io/pypi/status/Django.svg
..  https://img.shields.io/github/stars/badges/shields.svg?style=social&label=Star

.. End
.. -*- Mode: rst -*-

.. _CFFI: http://cffi.readthedocs.org/en/latest/
.. _Circuit_macros: http://ece.uwaterloo.ca/~aplevich/Circuit_macros
.. _IPython: http://ipython.org
.. _Kicad: http://www.kicad-pcb.org
.. _Matplotlib: http://matplotlib.org
.. _Modelica: http://www.modelica.org
.. _Ngspice: http://ngspice.sourceforge.net
.. _Numpy: http://www.numpy.org
.. _PyPI: https://pypi.python.org/pypi
.. _Pyterate: https://github.com/FabriceSalvaire/Pyterate
.. _Python: http://python.org
.. _Sphinx: http://sphinx-doc.org
.. _Tikz: http://www.texample.net/tikz
.. _Xyce: https://xyce.sandia.gov

.. |CFFI| replace:: CFFI
.. |Circuit_macros| replace:: Circuit_macros
.. |IPython| replace:: IPython
.. |Kicad| replace:: Kicad
.. |Matplotlib| replace:: Matplotlib
.. |Modelica| replace:: Modelica
.. |Ngspice| replace:: Ngspice
.. |Numpy| replace:: Numpy
.. |PyPI| replace:: PyPI
.. |Pyterate| replace:: Pyterate
.. |Python| replace:: Python
.. |Sphinx| replace:: Sphinx
.. |Tikz| replace:: Tikz
.. |Xyce| replace:: Xyce

=====================================================================================
 PySpice : Simulate Electronic Circuit using Python and the Ngspice / Xyce Simulators
=====================================================================================

|Pypi License|
|Pypi Python Version|

|Pypi Version|

* Quick Link to `Production Branch <https://github.com/FabriceSalvaire/PySpice/tree/master>`_
* Quick Link to `Devel Branch <https://github.com/FabriceSalvaire/PySpice/tree/devel>`_

Overview
========

What is PySpice ?
-----------------

PySpice is a Python module which interface |Python|_ to the |Ngspice|_ and |Xyce|_ circuit
simulators.

Where is the Documentation ?
----------------------------

The documentation is available on the |PySpiceHomePage|_.

What are the main features ?
----------------------------

* support Ngspice and Xyce circuit simulators
* support **Linux**, **Windows** and Mac **OS X** platforms
* licensed under **GPLv3** therms
* implement an **Ngspice shared library binding** using CFFI which support external sources
* implement (partial) **SPICE netlist parser**
* implement an **Oriented Object API** to define circuit
* export simulation output to |Numpy|_ arrays
* plot using |Matplotlib|_
* handle **units**
* work with **Kicad schematic editor**
* implement a **documentation generator**
* provides many **examples**

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

V1.4.0 (development release)
----------------------------

V1.3.2 (production release) 2019-03-11
--------------------------------------

 * support Ngspice 30 and Xyce 6.10
 * fixed NgSpice and Xyce support on Windows 10
 * bug fixes

V1.2.0 2018-06-07
-----------------

 * Initial support of the |Xyce|_ simulator.  Xyce is an open source, SPICE-compatible,
   high-performance analog circuit simulator, capable of solving extremely large circuit problems
   developed at Sandia National Laboratories.  Xyce will make PySpice suitable for industry and
   research use.
 * Fixed OSX support
 * Splitted G device
 * Implemented partially `A` XSPICE device
 * Implemented missing transmission line devices
 * Implemented high level current sources
   **Notice: Some classes were renamed !**
 * Implemented node kwarg e.g. :code:`circuit.Q(1, base=1, collector=2, emitter=3, model='npn')`
 * Implemented raw spice pass through (see `User FAQ </faq.html>`_)
 * Implemented access to internal parameters (cf. :code:`save @device[parameter]`)
 * Implemented check for missing ground node
 * Implemented a way to disable an element and clone netlist
 * Improved SPICE parser
 * Improved unit support:

   * Implemented unit prefix cast `U_μV(U_mV(1))` to easily convert values
   * Added `U_mV`, ... shortcuts
   * Added Numpy array support to unit, see `UnitValues` **Notice: this new feature could be buggy !!!**
   * Rebased `WaveForm` to `UnitValues`

 * Fixed node order so as to not confuse users **Now PySpice matches SPICE order for two ports elements !**
 * Fixed device shortcuts in `Netlist` class
 * Fixed model kwarg for BJT **Notice: it must be passed exclusively as kwarg !**
 * Fixed subcircuit nesting
 * Outsourced documentation generator to |Pyterate|_
 * Updated `setup.py` for wheel

.. :ref:`user-faq-page`

V1.1.0 2017-09-06
-----------------

 * Enhanced shared mode
 * Shared mode is now set as default on Linux

V1.0.0 2017-09-06
-----------------

 * Bump version to v1.0.0 since it just works!
 * Support Windows platform using Ngspice shared mode
 * Fixed shared mode
 * Fixed and completed Spice parser : tested on example's libraries

V0.4.2
------

 * Fixed Spice parser for lower case device prefix.

V0.4.0 2017-07-31
-----------------

 * Git repository cleanup: filtered generated doc and useless files so as to shrink the repository size.
 * Improved documentation generator: Implemented :code:`format` for RST content and Tikz figure.
 * Improved unit support: It implements now the International System of Units.
   And we can now use unit helper like :code:`u_mV` or compute the value of :code:`1.2@u_kΩ / 2@u_mA`.
   The relevant documentation is on this `page <api/PySpice/Unit.html>`_.
 * Added the Simulation instance to the Analysis class.
 * Refactored simulation parameters as classes.

V0.3.2 2017-02-22
-----------------

 * fixed CCCS and CCVS

V0.3.1 2017-02-22
-----------------

 * fixed ngspice shared

V0.3.0 2015-12-08
-----------------

 * Added an example to show how to use the NgSpice Shared Simulation Mode.
 * Completed the Spice netlist parser and added examples, we could now use a schematic editor
   to define the circuit.  The program *cir2py* translates a circuit file to Python.

V0 2014-03-21
-------------

Started project

.. End

.. End
