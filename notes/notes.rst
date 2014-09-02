* check examples
* add shared example
* implement units
* OpAmp / Transformer  ???
* implement waveform tools : cf. numpy, slice etc.
* implement basic simulator

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

------

circuit.R(name, np, nm, ...)
  wrapper(self, ...):
    element = R(name, np, nm, ...) <= pass circuit ref
      TwoPinElement
        pin = Pin(element, name, node) <- node is not a Node instance <= build/get Node
    circuit.add_element(element) <- element and circuit are linked here

we need a circuit instance to build/get a Node from its name.

----------------------------------------------------------------------------------------------------

* Fixme: i(vinput) -> analysis.vinput

  FIX casse : find node/element having name.lower() ...  <<FIXED>>

  v comes from V + input

  analysis.nodes.foo
  analysis.branches.foo

  analysis.v_foo but v_v_...
  analysis.i_foo

  analysis.v.foo
  analysis.i.foo

* analysis.in is invalid <<WARNED>>

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

link circuit and its simulation: simulation -of-> circuit
analysis.simulated_circuit()

----------------------------------------------------------------------------------------------------

* average: np.mean
* min/max: np.min/max
* peak to peak : max - min
* rms: integration ???

* integration : scipy
* derivative : cf. calculus
* FFT : scipy

WaveForm = (data, abscissa)
point = index -> (abscissa, value)

* measure time/voltage difference
  (point - point).value
  (point - point).abscissa

* locate rising/falling slopes in signal: derivative

* locate crossing points

* locate value according slope or crossing: interpolate

* locate the point when a signal is equal to a value or two signals are equal
  according to a slope/cross

* from to ???

----------------------------------------------------------------------------------------------------

