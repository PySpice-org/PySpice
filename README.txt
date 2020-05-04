.. -*- Mode: rst -*-

.. include:: project-links.txt
.. include:: abbreviation.txt

=====================================================================================
 PySpice : Simulate Electronic Circuit using Python and the Ngspice / Xyce Simulators
=====================================================================================

Thanks to `Discourse <https://www.discourse.org>`_, PySpice now has a **Forum** hosted at https://pyspice.discourse.group

**Disclaimer: PySpice is developed on my free time actually, so I could be busy with other tasks and less reactive.**

|Pypi License|
|Pypi Python Version|

|Pypi Version|

* Quick Link to `Production Branch <https://github.com/FabriceSalvaire/PySpice/tree/master>`_
* Quick Link to `Devel Branch <https://github.com/FabriceSalvaire/PySpice/tree/devel>`_

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

Authors: `Fabrice Salvaire <http://fabrice-salvaire.fr>`_ and contributors

News
====

.. include:: news.txt

.. End
