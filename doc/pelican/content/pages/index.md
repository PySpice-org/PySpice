Title: PySpice
Status: hidden
Template: index
Save_as: index.html

<h1 class="display-6">Simulate Electronic Circuit using Python and SPICE Simulators</h1>
<img src="images/figures/pyspice-architecture.svg" class="img-fluid mx-auto d-block w-75" alt="PySpice Architecture">

## Overview

PySpice is an open source [Python](https://www.python.org) library that interplay with the well
known SPICE family of electronic circuit simulators.  PySpice is licensed under
[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html) therms.

[SPICE ("Simulation Program with Integrated Circuit
Emphasis")](http://bwrcs.eecs.berkeley.edu/Classes/IcBook/SPICE/) is a general-purpose, open-source
analogue electronic circuit simulator that was developed at the Electronics Research Laboratory of
the University of California, Berkeley by Laurence Nagel.  The last released version of Berkeley
SPICE have been released in 1993 as SPICE 3f5.  Then the SPICE open source code was used as a base
and extended by several industrial and open source projects, like
[ngspice](http://ngspice.sourceforge.net).

### What are usually the limitation of the SPICE simulator integration in EDA suite ?

Usually the SPICE simulator is integrated in an EDA (Electronic Design Automation) software that
interfaces the schematic editor with a simulator.  Some these softwares are general purpose EDA or
only dedicated to simulation.  For example,
[LTspice](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
is a freeware provided by Analog Devices dedicated to simulation, and [KiCad](https://www.kicad.org)
is an open source EDA suite that interface with **ngspice**.

Originally, a circuit is defined in SPICE by an ASCII netlist, for example:

```
SIMPLE DIFFERENTIAL PAIR
VCC 7 0 12
VEE 8 0 -12
VIN 1 0 AC 1
RS1 1 2 1K
RS2 6 0 1K
Q1 3 2 4 MOD1
Q2 5 6 4 MOD1
RC1 7 3 10K
RC2 7 5 10K
RE 4 8 10K
.MODEL MOD1 NPN BF=50 VAF=50 IS=1.E-12 RB=100 CJC=.5PF TF=.6NS
.TF V(5) VIN
.AC DEC 10 1 100MEG
.END
```

In practice, we will have to sketch the circuit, give a name to each node and then translate in
SPICE each circuit element.  This work, which can be cumbersome, is greatly simplified with the
integration with a schematic editor.  In addition, it also permits to display a waveform like we
would do with a real scope probe.

But EDA suites have also counterparts, the schematic editor and the waveform viewer are not usually
scriptable.  It means you will not be able to easily change the circuit by a program, and you don't
have to power of a data analysis software like
[Matlab](https://www.mathworks.com/products/matlab.html).

Ngspice has a command line tool to perform powerful data analysis, but this tool is based on the
Tcl language which is an old technology.

## How PySpice can help you ?

PySpice implements a wrapper between the simulator and the Python language and its ecosystem which
is actually one of the most used language for engineering.

PySpice can handle several kinds of circuit input:

* PySpice can read a KiCad schematic `.kicad_sch` file and compute the netlist using
  [KiCad-RW](https://github.com/FabriceSalvaire/PySpic), and translate it to the netlist API.  We
  can alter the netlist using the API, for example replace elements or change values.
* PySpice permits to bypass directly raw SPICE netlist to the simulator.
* PySpice can parse a SPICE netlist and translate it to the netlist API.
* Netlists can be encoded using the netlist API in a more Pythonic way than a SPICE netlist.
* PySpice implements the [SKiDL](https://xess.com/skidl/docs/_site) efficient way to connect
  elements using Python.

PySpice supports actually two simulators and implements a simulation API:

* [ngspice](http://ngspice.sourceforge.net) (supports the shared library and raw files)
* [Xyce](https://xyce.sandia.gov) (preliminary support)

The simulation output is exported to [Numpy](https://numpy.org) arrays and can be
[pickled](https://docs.python.org/3/library/pickle.html) for caching or saved to a
[HDF5](https://www.hdfgroup.org/solutions/hdf5) file.

Waveforms can be analysed with Numpy and plotted using the [matplotlib](https://matplotlib.org)
library.

<!-- To complete our discussion, how PySpice can help you: -->
<!-- And to conclude, -->
<!-- PySpice is part of a full open source and format simulation ecosystem -->

Thus, by creating the interface between all these open source software components, PySpice makes
possible a fully open source and format simulation ecosystem, where the simulation is fully
scriptable and can be managed by a version control system like [Git](https://git-scm.com).

Concerning the language and its ecosystem, Python is a modern and well known language which can
replace Matlab, and outperforms the analysis features of an EDA.

Concretely, using PySpice you get a powerful framework to automatically simulate a circuit with
thousands of variations, and share a free, open and reproducible simulation environment.
