
=============
 Transformer
=============


.. code-block:: python

    
    import os
    
    from matplotlib import pylab
    
    
    import PySpice.Logging.Logging as Logging
    logger = Logging.setup_logging()
    
    
    from PySpice.Probe.Plot import plot
    from PySpice.Spice.Library import SpiceLibrary
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit.Units import *
    
    
    from Transformer import Transformer
    
    
    circuit = Circuit('Transformer')
    
    ac_line = circuit.AcLine('input', 'input', circuit.gnd, rms_voltage=230, frequency=50)
    circuit.subcircuit(Transformer(turn_ratio=10))
    circuit.X('transformer', 'Transformer', 'input', circuit.gnd, 'output', circuit.gnd)
    circuit.R('load', 'output', circuit.gnd, kilo(1))
    
    print str(circuit)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=ac_line.period/200, end_time=ac_line.period*3,
                                   probes=('V(input)', 'V(output)'))
    
    plot(analysis.input)
    plot(analysis.output)
    pylab.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
    pylab.grid()
    pylab.xlabel('t [s]')
    pylab.ylabel('[V]')
    pylab.show()

