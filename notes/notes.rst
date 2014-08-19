----------------------------------------------------------------------------------------------------

Netlist

  a circuit has elements and nodes
  element has pins
  a pin is connected to a node
  a node is connected to pins (else the node is dangling)
  
  a node is a vertex of the circuit graph
  a two-pins element is an edge/branch
  more than two-pins element is a subcircuit
  
  we add a current probe to a pin/branch

----------------------------------------------------------------------------------------------------

* Fixme: i(vinput) -> analysis.vinput

  v comes from V + input

  analysis.nodes.foo
  analysis.branches.foo

  analysis.v_foo but v_v_...
  analysis.i_foo

  analysis.v.foo
  analysis.i.foo

* analysis.in is invalid

  in is a keyword !

  import keyword
  keyword.iskeyword(s)
 
----------------------------------------------------------------------------------------------------

* plot scale mA

ticks = your_plot.get_xticks()*10**9
your_plot.set_xticklabels(ticks)

ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x*scale))
ax.xaxis.set_major_formatter(ticks)

----------------------------------------------------------------------------------------------------

* element ddp, pin voltage/current : cf. Modelica

  simulation output is voltage node and source branch current

  simulated element wraps the element and the simulation output together
  simulated circuit : map element to simulated element

  simulated_R1 = circuit.R1.simulated(analysis)
  simulated_R1.v = analysis[self._element.plus] - analysis[self._element.minus]
  simulated_R1.i = self.v / float(self._element.resistance)
  simulated_R1.plus = analysis[self._element.plus]

----------------------------------------------------------------------------------------------------

* fix copyright and license

* units
* OpAmp / Transformer 
* waveform slice : cf. numpy

----------------------------------------------------------------------------------------------------

Old

* define netlist
* expand variables
* current probes? voltage source Vxxx#branch  *--Vxxx--...--*
* flatten spice desk using netlist and libraries
* add simulation instructions
* expand variables ?
* run ngspice
* read output
* analyse or save data

----------------------------------------------------------------------------------------------------
