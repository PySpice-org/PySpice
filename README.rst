.. -*- Mode: rst -*-

.. -*- Mode: rst -*-

.. |PySpiceUrl| replace:: https://pyspice.fabrice-salvaire.fr

.. |PySpiceHomePage| replace:: PySpice Home Page
.. _PySpiceHomePage: https://pyspice.fabrice-salvaire.fr


.. |PySpice@github| replace:: https://github.com/FabriceSalvaire/PySpice


.. |PySpice@pypi| replace:: https://pypi.python.org/pypi/PySpice


.. |PySpice@anaconda| replace:: https://anaconda.org/conda-forge/pyspice

.. |PySpice@fs-anaconda| replace:: https://anaconda.org/fabricesalvaire/pyspice

.. |Anaconda Version| image:: https://anaconda.org/conda-forge/pyspice/badges/version.svg
   :target: https://anaconda.org/conda-forge/pyspice/badges/version.svg
   :alt: Anaconda last version

.. |Anaconda Downloads| image:: https://anaconda.org/conda-forge/pyspice/badges/downloads.svg
   :target: https://anaconda.org/conda-forge/pyspice/badges/downloads.svg
   :alt: Anaconda donwloads


.. |Pypi Version| image:: https://img.shields.io/pypi/v/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice last version

.. |Pypi License| image:: https://img.shields.io/pypi/l/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice license

.. |Pypi Python Version| image:: https://img.shields.io/pypi/pyversions/PySpice.svg
   :target: https://pypi.python.org/pypi/PySpice
   :alt: PySpice python version


.. |Tavis CI master| image:: https://travis-ci.com/FabriceSalvaire/PySpice.svg?branch=master
   :target: https://travis-ci.com/FabriceSalvaire/PySpice
   :alt: PySpice build status @travis-ci.org
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

|Anaconda Version|
|Anaconda Downloads|

|Tavis CI master|

**Quick Links**

* `Production Branch <https://github.com/FabriceSalvaire/PySpice/tree/master>`_
* `Devel Branch <https://github.com/FabriceSalvaire/PySpice/tree/devel>`_
* `Travis CI <https://travis-ci.com/github/FabriceSalvaire/PySpice>`_
* `pyspice@conda-forge <https://github.com/conda-forge/pyspice-feedstock>`_
* `ngspice@conda-forge <https://github.com/conda-forge/ngspice-feedstock>`_
* `Ngspice <http://ngspice.sourceforge.net>`_
* `Ngspice Bug Tracker <https://sourceforge.net/p/ngspice/bugs>`_
* `Xyce of Sandia National Laboratories <https://xyce.sandia.gov>`_

Brief Notes
===========

Thanks to `Discourse <https://www.discourse.org>`_, PySpice now has a **Forum** hosted at https://pyspice.discourse.group

**Disclaimer: PySpice is developed on my free time actually, so I could be busy with other tasks and less reactive.**

An issue was found with NgSpice Shared, we must `setlocale(LC_NUMERIC, "C");` see https://sourceforge.net/p/ngspice/bugs/490/

Overview
========

What is PySpice ?
-----------------

PySpice is a Python module which interface |Python|_ to the |Ngspice|_ and |Xyce|_ circuit simulators.

Where is the Documentation ?
----------------------------

The documentation is available on the |PySpiceHomePage|_.

*Note: This site is hosted on my own infrastructure, if the site seems done, please create an issue to notify me.*

Where to get help or talk about PySpice ?
-----------------------------------------

Thanks to `Discourse <https://www.discourse.org>`_, PySpice now has a **Forum** hosted at https://pyspice.discourse.group

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

Pull Request Recommendation
===========================

To make it easier to merge your pull request, you should divide your PR into smaller and easier-to-verify units.

Please do not make a pull requests with a lot of modifications which are difficult to check.  **If I merge
pull requests blindly then there is a high risk this software will become a mess quickly for everybody.**

Credits
=======

Authors: `Fabrice Salvaire <http://fabrice-salvaire.fr>`_ and `contributors <https://github.com/FabriceSalvaire/PySpice/blob/master/CONTRIBUTORS.md>`_

News
====

.. -*- Mode: rst -*-


.. no title here

V1.5.0 (development release)
----------------------------

V1.4.? (production release) 2020-0?-??
--------------------------------------

A huge effort, thanks to @stuarteberg Stuart Berg, has been made to make Ngspice and PySpice
available on Anaconda (conda-forge) for the Window, OSX and Linux platforms.  Thanks to the
conda-forge continuous integration platform, we can now run unit tests and the examples on theses
platforms automatically.  Hope this will make the software more robust and easier to run !

* PySpice is now available on Anaconda(conda-forge) as well as a wheel on PyPI
* Added a post installation tool to download the Ngspice DLL on Windows and to check the installation.
  It should now simplify considerably the PySpice installation on Windows.
* This tool can also download the examples and the Ngspice PDF manual.
* On Linux and OSX, a Ngspice package is now available on Anaconda(conda-forge).
  Note that theses two platforms do not download a binary from Ngspice since a compiler can easily be installed on theses platforms.
* Updated installation documentation for Linux, the main distributions now provide a ngspice shared package.

* Added a front-end web site so as to keep older releases documentation available on the web.
* fixed and rebuilt all examples (but mistakes could happen ...)
* examples are now available as Python files and Jupyter notebooks
  (but some issues must be fixed, e.g. due to the way Jupyter handles Matplotlib plots)

* support NgSpice 32 API (no change)
* removed @substitution@ in PySpice/__init__.py, beacause it breaks pip install from git
* fixed some logging spams
* fixed NonLinearVoltageSource
* fixed Unicode issue with °C (° is Extended ASCII)
* fixed ffi_string_utf8 for UnicodeDecodeError
* fixed logging formater for OSX (removed ANSI codes)
* reworded "Invalid plot name" exception
* removed diacritics in example filenames
* cir2py has been converted to an entry point so as to work on all platforms
* updated Matplotlib subplots in examples
* added a unit example
* added a NMOS example (thanks to cyber-g) cf. #221

V1.4.0 2020-05-05
-----------------

This release is yanked due to broken Windows support.

* fixed nasty issue with NgSpice shared for `setlocale(LC_NUMERIC, "C");` cf. #172
* fixed `AC AC_MAG AC_PASAE SIN` for new NgSpice syntax
* fixed `initial_state` for `VoltageControlledSwitch`
* fixed `LosslessTransmissionLine` #169
* fixed docstrings for element shortcut methods (thanks to Kyle Dunn) #178
* fixed parser for leading whitespace (thanks to Matt Huszagh) #182
* fix for PyYAML newer API
* support NgSpice 31 API (no change)
* added check for `CoupledInductor` #157
* added `check-installation` tool to help to fix broken installation
* added pole-zero, noise, distorsion, transfer-function analyses (thanks to Peter Garrone) #191
* added `.measure` support (thanks to ceprio) #160
* added `log_desk` parameter to `CircuitSimulator`
* added `listing` command method to `NgSpiceShared`
* added Xyce Mosfet nfin #177

V1.3.2  2019-03-11
------------------

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
