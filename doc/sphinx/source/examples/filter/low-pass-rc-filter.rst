
====================
 Low Pass Rc Filter
====================


.. raw:: html

  <div class="getthecode">
    <div class="getthecode-header">
      <span class="getthecode-filename">RingModulator.py</span>
      <a href="../../_downloads/RingModulator.py"><span>RingModulator.py</span></a>
    </div>
  </div>

.. code-block:: python

    
    import numpy as np
    from matplotlib import pylab
    
    
    import PySpice.Logging.Logging as Logging
    logger = Logging.setup_logging()
    
    
    from PySpice.Plot.BodeDiagram import bode_diagram
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit.Units import *
    
    
    circuit = Circuit('Low-Pass RC Filter')
    
    circuit.Sinusoidal('input', 'in', circuit.gnd, amplitude=1)
    circuit.R('f', 'in', 'out', kilo(1))
    circuit.C('f', 'out', circuit.gnd, micro(1))
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.ac(start_frequency=1, stop_frequency=mega(1), number_of_points=10,  variation='dec')
    
    print(analysis.out)
    
    figure = pylab.figure()
    pylab.title("Bode Diagram of a Low-Pass RC Filter")
    bode_diagram(axes=(pylab.subplot(211), pylab.subplot(212)),
                 frequency=analysis.frequency,
                 gain=20*np.log10(np.absolute(analysis.out)),
                 phase=np.angle(analysis.out, deg=False),
                 marker='.',
                 color='blue',
                 linestyle='-',
             )
    pylab.tight_layout()
    pylab.show()

