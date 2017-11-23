.. include:: abbreviation.txt
.. include:: project-links.txt

.. _overview-page:

==========
 Overview
==========

What is PySpice ?
-----------------

PySpice is an open source Python module which provides a |Python|_ interface to the |Ngspice|_ and
|Xyce|_ circuit simulators.

|Ngspice|_ is a fork of the famous `SPICE <https://en.wikipedia.org/wiki/SPICE>`_ circuit simulator,
while |Xyce|_ is a SPICE compatible simulator developed by the `Sandia National Laboratories
<http://www.sandia.gov>`_.

It permits:

 * definition of a circuit, through a netlist,
 * simulation using |Ngspice|_ and |Xyce|_,
 * analysis of the output using |Numpy|_ and |Matplotlib|_.

How is PySpice licensed ?
-------------------------

PySpice is licensed under the `GPLv3 <https://www.gnu.org/licenses/quick-guide-gplv3.en.html>`_.

Are there some papers or talks about PySpice ?
----------------------------------------------

You can watch `Circuit Simulation using Python
<https://www.slideshare.net/PoleSystematicParisRegion/pyparis2017-circuit-simulation-using-python-by-fabrice-salvaire>`_
given at the `PyParis 2017 <http://pyparis.org/>`_ conference (`PDF file
<https://pyspice.fabrice-salvaire.fr/pyparis-2017-talk.pdf>`_)

Going further with PySpice
--------------------------

The best way to know what you can do with PySpice, and to learn it, is to look at the examples:

 * :ref:`Examples <examples-page>`
 * :ref:`PySpice Reference Manual <reference-manual-page>`
 * :ref:`Bibliography <bibliography-page>`

How can PySpice be used for learning ?
--------------------------------------

 * PySpice comes with many examples covering several topics.

.. * PySpice features a documentation generator which generates HTML or PDF documentation
..
..  | cf. supra for the documentation generator features

Which platforms are supported by PySpice ?
------------------------------------------

PySpice runs on Linux, Windows 64-bit and Mac OS X.

How to install PySpice ?
------------------------

The procedure to install PySpice is described in the :ref:`Installation Manual <installation-page>`.

How does PySpice differ from simulator like LTspice ?
-----------------------------------------------------

 * PySpice, Ngspice and Xyce are `Free Software <https://en.wikipedia.org/wiki/Free_software>`_ and thus open source,
 * PySpice doesn't feature a schematic editor (*) or GUI, but,
 * It has the power of Python for data analysis,
 * And thus provide modern data analysis tools.
 * Moreover PySpice is feature unlocked due to its open design.

(*) However you can export netlist from Kicad to PySpice.

How can a non-GUI simulator be helpful ?
----------------------------------------

It is often not easy to write a netlist, and a tool like a schematic editor can help to
visualise the circuit.  Tools like Circuit_macros and Tikz are complex and
need some practices.  However, the learning curve is no worse than for a musical instrument.

Another question is to discuss the possibility to simulate a real design, i.e. to integrate the
simulation in the Electronic Design Automation (EDA) process, from the schematic to the PCB.  Often, it does not make
sense to simulate a real design, and we only simulate parts or models of a design to ensure the
real design is right.

In fact each tool has advantages and drawbacks which are often orthogonal.

Having discussed the main drawbacks, we will now look at the advantages:

 * Since it is code, you can describe completely your simulation project.  There are no actions that
   require to use a mouse to interact with the GUI.
 * It can be easily versioned using a tool like Git.
 * If you work with an editor and a console in parallel, then you can easily and quickly change
   things, and rerun the simulation, e.g. comment out a diode or a capacitor to see what happen.  Using a
   GUI, this task would require many actions.
 * Thanks to the tool |Pyterate|_, you can enrich your simulation with text,
   formulae and figures.

Is is possible to use both approaches all together ? The technical answer is, 'yes we
can'. For example the Modelica language uses a concept of annotations to describe the schema.  A
schematic editor like Kicad could be updated to interact closely with PySpice.

What are the benefits of PySpice over Ngspice / Xyce ?
------------------------------------------------------

 * You can steer your netlist and simulation using Python.

  | Which supersede Spice *parameters* and *expressions*.
  | Which make Monte Carlo simulation easier for example.

 * You can analyse the output using scientific packages for Python.

  | Which supersede tools like TclSpice.

How is PySpice interfaced with Ngspice ?
----------------------------------------

 * PySpice can parse a Spice netlist and generate the equivalent Python code, or instantiate it directly.
 * PySpice can generate a Spice netlist.
 * PySpice can send a simulation to Ngspice and read back the output using either the *server* or *shared* mode.

  | By default, PySpice uses the server mode. Shared mode is only required when you need advanced features.

When using *shared* mode

 * PySpice permits defining the external voltage and current source in Python (or even in C).
 * PySpice permits getting and sending data to the simulator during the simulation process.
 * |CFFI|_ is used to interface C to Python.

How is PySpice interfaced with Xyce ?
-------------------------------------

Actually, PySpice run Xyce as a subprocess and read the raw output.

How is the netlist defined ?
----------------------------

 * The netlist is defined using an object-oriented API
 * PySpice can also work with Spice netlist and import netlist from a schematic editor like |Kicad|_.

Can I run Ngspice using interpreter commands ?
----------------------------------------------

Thanks to the Ngspice shared library binding, you are not tied to the object-oriented API of
PySpice.  You can run Ngspice as you did before and just upload the simulation output as Numpy
arrays.  For an example, look at the Ngspice shared examples.

How are Spice libraries handled ?
---------------------------------

 * PySpice features a library manager that scan a path for library files.
 * Libraries can be included as is using the *include* directive.
 * Subcircuits can be defined as Python classes.

How are units handled ?
-----------------------

 * PySpice features a unit module that support the SI Units.
 * Value units can be defined using function shortcuts or a special syntax: e.g. :code:`kilo(1.2)`, :code:`1.2@u_kV`, :code:`1.2@u_mΩ`.

Which version of Python is required ?
-------------------------------------

PySpice requires Python 3 and the version 3.5 is recommended so as to benefit from the new *@* syntax
for units.

Which version of Ngspice is required ?
--------------------------------------

You should use the latest version of Ngspice and take care it was compiled according to the Ngspice
manual, i.e. you should check somebody didn't enable experimental features which could break
PySpice, generate a wrong simulation, or produce bugs.

*Note that Ngspice is not distributed with PySpice !*

Which version of Xyce is required ?
-----------------------------------

You should use the latest version provided by Sandia.

Which flavours of SPICE are supported ?
---------------------------------------

Up to now PySpice only support Ngspice and Xyce.

But PySpice could support easily any simulator providing an API similar to Ngspice.

What else should you be aware of ?
----------------------------------

Users should be aware of these disclaimers:

 * Ngspice and PySpice are provided without any warranty.

  | Thus you must use it with care for real design.
  | Best is to cross-check the simulation using an industrial grade simulator.

 * Ngspice is not compliant with industrial quality assurance processes.

 * Simulation is a design tool and not a perfect description of the real world.
