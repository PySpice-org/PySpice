
.. include:: /project-links.txt
.. include:: /abbreviation.txt

=================
 Voltage Divider
=================


.. getthecode:: voltage-divider.py
    :language: python


.. code-block:: python

    import PySpice.Logging.Logging as Logging
    logger = Logging.setup_logging()
    
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit.Units import *
    
    circuit = Circuit('Voltage Divider')
    
    circuit.V('input', 'in', circuit.gnd, '10V')
    circuit.R(1, 'in', 'out', kilo(9))
    circuit.R(2, 'out', circuit.gnd, kilo(1))
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    analysis = simulator.operating_point()
    for node in (analysis['in'], analysis.out): # .in is invalid !
        print('Node {}: {} V'.format(str(node), float(node)))
    
    analysis = simulator.dc_sensitivity('v(out)')
    for element in analysis.elements.values():
        print(element, float(element))

