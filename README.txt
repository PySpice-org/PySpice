.. -*- Mode: rst -*-

.. include:: project-links.txt
.. include:: abbreviation.txt

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
* `conda-forge/pyspice <https://anaconda.org/conda-forge/pyspice>`_
* `ngspice@conda-forge <https://github.com/conda-forge/ngspice-feedstock>`_
* `Ngspice <http://ngspice.sourceforge.net>`_
* `Ngspice Bug Tracker <https://sourceforge.net/p/ngspice/bugs>`_
* `Xyce of Sandia National Laboratories <https://xyce.sandia.gov>`_

2024 Update
===========

**Disclaimer: PySpice is developed on my free time actually, so I could be busy with other tasks and less reactive.**

The free Discourse forum was closed some time ago due to a lack of activity.
A HTML backup is stored in the directory `pyspice-discourse-backup`.

**On Devel HEAD**
* fixed the ngspice library loading for recent cffi
* fixed simulation aborting due to a message from newer ngspice
* fixes for Spice parser
* added support for Pint unit library
* implemented SpiceLibrary
* code cleanup but must check for typo...

..
    Brief Notes
    ===========

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

Look at the `installation <https://pyspice.fabrice-salvaire.fr/releases/latest/installation.html>`_ section in the documentation.

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

.. include:: news.txt

.. End
