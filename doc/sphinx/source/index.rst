.. include:: abbreviation.txt
.. include:: project-links.txt

.. hack to move down the next note block
.. raw:: html

   <br/>

######################################################
 Simulate Electronic Circuit using Python and Ngspice
######################################################

==========
 Overview
==========

What is PySpice ?
-----------------

In short PySpice is an open source Python module which interface |Python|_ and the famous `Spice
<https://en.wikipedia.org/wiki/SPICE>`_ circuit simulator.

Mainly it permits:

 * to define a circuit, so called netlist,
 * to perform a simulation using |Ngspice|_,
 * to analyse the output using |Numpy|_, |Matplotlib|_, ...

Is there some papers or talks about PySpice ?
---------------------------------------------

You can look this talk `Circuit Simulation using Python
<https://www.slideshare.net/PoleSystematicParisRegion/pyparis2017-circuit-simulation-using-python-by-fabrice-salvaire>`_
given at the `PyParis 2017 <http://pyparis.org/>`_ conference (`PDF file
<https://pyspice.fabrice-salvaire.fr/pyparis-2017-talk.pdf>`_)

How to go further with PySpice ?
--------------------------------

The best way to know what you can do with PySpice and to learn it, is to look at the examples.

 * :ref:`Examples <examples-page>`
 * :ref:`PySpice Reference Manual <reference-manual-page>`
 * :ref:`Bibliography <bibliography-page>`

How PySpice can be used for learning ?
--------------------------------------

 * PySpice comes with many examples covering several topics.
 * PySpice features a documentation generator which permits to generate an HTML or PDF documentation

  | cf. supra for the documentation generator features

How to install PySpice ?
------------------------

The procedure to install PySpice is described in the :ref:`Installation Manual <installation-page>`.

How PySpice differs from simulator like LTspice ?
-------------------------------------------------

 * PySpice and Ngspice are `Free Software <https://en.wikipedia.org/wiki/Free_software>`_ and thus open source,
 * PySpice don't feature a schematic editor (*) or GUI,
 * But it has the power of Python for data analysis,
 * And thus provide modern data analysis tools.
 * Moreover PySpice is feature unlocked due to its open design.

(*) However you can export netlist form Kicad to PySpice.

What is the benefits of PySpice over Ngspice ?
----------------------------------------------

 * You can steer your netlist and simulation using Python.

  | Which supersede Spice *parameters* and *expressions*.
  | Which make Monte Carlo simulation easier for example.

 * You can analyse the output using the Python Scientific packages.

  | Which supersede tools like TclSpice.

How PySpice is interfaced to Ngspice ?
--------------------------------------

 * PySpice can parse a Spice netlist and generate the equivalent Python code or instanciate it.
 * PySpice can generate a Spice netlist.
 * PySpice can send a simulation and read back the output using either the *server* or *shared* mode.

  | By default, PySpice use the server mode. Shared mode is only required when you need advanced features.

When using *shared* mode

 * PySpice permits to define external voltage and current source in Python (or even in C).
 * PySpice permits to get and send data during the simulation process.
 * |CFFI|_ is used to interface C to Python.

How is defined netlist ?
------------------------

 * Netlist is defined using an oriented object API,
 * But PySpice can also work with Spice netlist and import netlist from a schematic editor like |Kicad|_.

How are handled Spice libraries ?
---------------------------------

 * PySpice features a libraries manager that scan a path for library files.
 * Libraries can be included as is using the *include* directive.
 * Subcircuit can be defined as Python class.

How are handled units ?
-----------------------

 * PySpice features a unit module that support the International System of Units.
 * Unit value can be defined using function shortcuts or a special syntax: e.g. :code:`kilo(1.2)`, :code:`1.2@u_kV`, :code:`1.2@u_mΩ`.

Which version of Python is required ?
-------------------------------------

PySpice requires Python 3 and the version 3.5 is recommended so as to benefits of the new *@* syntax
for units.

Which version of Ngspice is required ?
--------------------------------------

You should use the last version of Ngspice and take care it was compiled according to the Ngspice
manual, i.e. you should check somebody don't enabled experimental features which could break
PySpice, generate a wrong simulation, or produce bugs.

*Notice that Ngspice is not distributed with PySpice !*

Which flavour of Spice are supported ?
--------------------------------------

Up to now PySpice only support Ngspice. But PySpice could support easily any simulator providing an
API similar to Ngspice shared.

What should you aware of ?
--------------------------

Users should be aware of these advertisements:

 * Ngspice and PySpice are provided without any warranty.

  | Thus you must use it with care for real design.
  | Best is to cross check the simulation using an industrial grade simulator.

 * Ngspice is not compliant with industrial quality assurance processes.
 * Simulation is a design tool and not a perfect description of the real world.

How is coded PySpice ?
----------------------

PySpice is not the crappy code you can found on Github, but is rather coded carefully and use
advanced Python features like metaclass.

What are the features of the documentation generator ?
------------------------------------------------------

The documentation generator features:

 * intermixing of codes, texts, `LaTeX formulae <https://www.mathjax.org>`_, figures and plots
 * use the `reStructuredText <https://en.wikipedia.org/wiki/ReStructuredText>`_ syntax for text
 * use the |Sphinx|_ generator
 * embed computations in the text content
 * generation of circuit schematics using |Circuit_macros|_
 * generation of figures using |Tikz|_
 * generation of plots using |Matplotlib|_

Somehow, it is similar to an `Jupyter notebook <https://ipython.org/notebook.html>`_, but it works
differently and provides specific features.

What are the planned features ?
-------------------------------

These features are planned in the future:

* Improve the analyse experience.

Some other ideas are:

* Implement a Modelica backend. |Modelica|_ is a very interesting solution for transient analysis.

The implementation of a simulator in Python is not planned since it would be too challenging to
release a full featured and proved simulator. However you could look at the project `Ahkab
<https://ahkab.github.io/ahkab>`_ which aims to implement such Python based simulator.  Notice any
of the projects like Ngspice or Ahkab are compliant with industrial quality assurance processes.

======
 News
======

.. include:: news.txt

===================
 Table of Contents
===================

.. toctree::
  :maxdepth: 3
  :numbered:

  installation.rst
  faq.rst
  example-introduction.rst
  examples/index.rst
  example-whish-list.rst
  reference-manual.rst
  bibliography.rst

.. End
