# KiCadTools — A Python Module to work with KiCad files

**keywords:** kicad, 6, python, schema

**KiCadTools** is a Python module to read the KiCad version 6 schema
file format (`.kicad_sch` file extension) and to compute the netlist
which is not actually stored by KiCad.  This module is standalone and
independent of the KiCad Python API, thus it don't require KiCad to
work.

**Note**: This proof of concept could become a standalone project and
be further extended.

Examples of use cases:

* perform checks on circuit
* export a BOM
* generate a customised SPICE netlist, see [PySpice](https://github.com/FabriceSalvaire/PySpice)
* generate a [LaTeX/Tikz](https://ctan.org/pkg/pgf?lang=en) graphic **TO BE IMPLEMENTED**
* generate a draft for [Circuit_macros](https://ece.uwaterloo.ca/~aplevich/Circuit_macros),
  a tool for drawing electric high quality circuits, see `CircuitMacrosDumper`
* etc.

## Related Projects

* https://github.com/dvc94ch/pykicad — Library for working with KiCAD file formats **supports .kicad_pcb**

## Comprehensive List of KiCad Tools

* https://github.com/xesscorp/kicad-3rd-party-tools — Tools made by others to augment the KiCad PCB EDA suite.

## KiCad EDA Links

* http://www.kicad-pcb.org
* https://github.com/KiCad
* https://dev-docs.kicad.org/en/file-formats
* https://docs.kicad.org/doxygen-python

* https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Libraries_Files_Format

## KiCon

* [Talk "The Python Whisperer Guide" - Maciej 'Orson' Suminski (KiCon 2019)](https://www.youtube.com/watch?v=_zVJ96SdYrs)
  and [PDF Slides](https://2019.kicad-kicon.com/wp-content/uploads/2019/05/Maciej-Suminski-kicon_python.pdf)

## Some Repositories

* https://github.com/INTI-CMNB/KiAuto — A bunch of scripts to automate KiCad processes
* https://github.com/pointhi/kicad-python — KiCad Python abstraction layer, last commit on 15 Mar 2019
* https://github.com/KiCad/kicad-python — Development of a new Python scripting API for KiCad, last on on 1 Feb 2016

## Other EDA 

* https://github.com/vadmium/python-altium — Altium schematic format documentation, SVG converter and TK viewer
