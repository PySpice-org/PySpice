.. _related-projects-page:

==================
 Related Projects
==================

Schematic Editor
================

`KiCad <https://kicad-pcb.org>`_ is an open source software suite for Electronic Design Automation
(EDA). The programs handle Schematic Capture, and PCB Layout with Gerber output. The suite runs on
Windows, Linux and macOS and is licensed under GNU GPL v3.

Netlist Tools
=============

SKIDL
-----

`SKiDL <https://xesscorp.github.io/skidl/docs/_site>`_ is a module that allows you to
compactly describe the interconnection of electronic circuits and components using Python.  The
resulting Python program performs electrical rules checking for common mistakes and outputs a
netlist that serves as input to a PCB layout tool (e.g. Kicad).

SKiDL can generate a circuit using the PySpice API, see this full example
https://github.com/xesscorp/skidl/blob/master/examples/spice-sim-intro/spice-sim-intro.ipynb

Circuit Simulator
=================

Ahkab
-----

`Ahkab <https://ahkab.github.io/ahkab>`_ is a SPICE-like electronic circuit simulator written in Python.

Lcapy
-----

`Lcapy <http://lcapy.elec.canterbury.ac.nz>`_ is a Python package for linear circuit analysis. Lcapy
uses `SymPy <http://www.sympy.org>`_ for symbolic analysis.  Lcapy can semi-automate the drawing of
schematics from a netlist using Circuitikz.  Lcapy sources are available at
https://github.com/mph-/lcapy

Other Projects
--------------

 * `eispice <http://www.thedigitalmachine.net/eispice.html>`_
 * `SPICE OPUS <http://www.spiceopus.si>`_ and `PyOPUS <http://fides.fe.uni-lj.si/pyopus>`_
 * `A Python interface for SPICE-based simulations <http://ieeexplore.ieee.org/xpl/login.jsp?tp=&arnumber=5595224&url=http%3A%2F%2Fieeexplore.ieee.org%2Fxpls%2Fabs_all.jsp%3Farnumber%3D5595224>`_

CPU Simulator
=============

PyCpuSimulator
--------------

`PyCpuSimulator <https://github.com/FabriceSalvaire/PyCpuSimulator>`_ is CPU simulator written in Python featuring:

* Micro-Code Language to describe instruction
* Opcode Decoder using Decision Tree
* Read HEX firmware format
* AVR Core CPU simulation (not completed)
