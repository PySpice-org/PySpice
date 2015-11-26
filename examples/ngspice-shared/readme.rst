This section shows how to use the NgSpice Shared Simulation Mode which permits to plug
voltage/current sources from Python to NgSpice and vice versa.

This NgSpice feature paves the way to advanced simulation use cases.  For example we can perform a
mixed level simulation of an analogic circuit connected to a microcontroller.  We just need to
implement an impedance model in Spice for input and output ports and implement the logic within
Python.  The NgSpice callbacks provide the interface to read and set current/voltage of the external
nodes.

See :mod:`PySpice.Spice.NgSpice.Shared` for more details.

.. end
