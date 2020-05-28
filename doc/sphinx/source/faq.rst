.. include:: project-links.txt
.. include:: abbreviation.txt

.. _user-faq-page:

==========
 User FAQ
==========

PySpice FAQ
===========

How to get help or report an issue ?
------------------------------------

PySpice has a **Forum** hosted at https://pyspice.discourse.group

**If you encounter an issue, please fill an issue** on the `Issue Tracker <https://github.com/FabriceSalvaire/PySpice/issues>`_.


How to typeset :code:`u_kΩ` or :code:`u_μV` in Python code ?
------------------------------------------------------------

There is three solutions if you don't have these Unicode characters available on your keyboard. The
first one, is to use the ASCII alternative: :code:`u_kOhm` or :code:`u_uV.`.  The second one, is to
define macros on your favourite editor.  The last one, is to customise your keyboard settings (on Linux look at https://www.x.org/wiki/XKB/).


How to perform division with units ?
------------------------------------

According to the Python `operator precedence
<https://docs.python.org/3/reference/expressions.html#operator-precedence>`_, division operators
have a higher priority than the matrix multiplication operator.  In consequence you must had
parenthesis to perform something like :code:`(10@u_s) / (2@_us)`.

**It is currently an issue ...**


Is unit API well tested ?
-------------------------

**Unit API is an ongoing work.  You must use it with caution since it can be buggy or incomplete.**


Is ground node required ?
-------------------------

**Yes**, according to Ngspice manual, each circuit has to have a ground node (gnd or 0)!


How to deal with SPICE parameters that clash with Python keywords ?
-------------------------------------------------------------------

For such cases, PySpice accepts keyword arguments with a trailing underscore, for example:

.. code-block:: py3

    model = circuit.model('Diode', 'D', is_=1)
    model.is_ = 1
    model['is'] = 1

We can also use uppercase letters since SPICE is case insensitive.


How to pass raw SPICE command ?
-------------------------------

If the API don't yet implement a SPICE command, then you can pass raw SPICE commands using:

.. code-block:: py3

    circuit.raw_spice  = '...'
    circuit.raw_spice += '...'

and raw parameters using:

.. code-block:: py3

    r1 = circuit.R('1', 1, 0, raw_spice='...')
    r1.raw_spice  = '...'
    r1.raw_spice += '...'

.. warning:: However the API must be aware of the nodes in order to retrieve data from the simulation output.


How to set the simulator ?
--------------------------

You can set globally the default simulator using the attribute :attr:`PySpice.Spice.Simulation.CircuitSimulator.DEFAULT_SIMULATOR`.

Else you can set the simulator per simulation using the `simulator` option:

.. code:: py

   simulator = circuit.simulator(simulator='...')

Actually, theses simulators are available:

 * `ngspice-subprocess`
 * `ngspice-shared`
 * `xyce-serial`
 * `xyce-parallel`


Ngspice FAQ
===========

How to get the Ngspice manual ?
-------------------------------

Either download it from http://ngspice.sourceforge.net or use the command:

.. code-block:: sh

    pyspice-post-installation --download-ngspice-manual


How to set the Ngspice library path ?
-------------------------------------

If the default setting doesn't match your environment, then you have to fix globally the attribute
:attr:`PySpice.Spice.NgSpice.Shared.NgSpiceShared.LIBRARY_PATH`. Note you have to place a brace pair
just before the extension, for example :file:`C:\\...\\ngspice{}.dll`.

You can also fix the value of :attr:`PySpice.Spice.NgSpice.Shared.NgSpiceShared.NGSPICE_PATH`.


How to set the Ngspice executable path ?
----------------------------------------

If the default setting doesn't match your environment, then you can fix globally the Ngspice executable
path using the attribute :attr:`PySpice.Spice.NgSpice.Server.SpiceServer.SPICE_COMMAND`, you can also
pass the executable path to the simulator using::

   simulator = circuit.simulator(spice_command='...')


Xyce FAQ
========

How to set the Xyce path ?
--------------------------

If the default setting doesn't match your environment, then you can fix globally the Xyce executable
path using the attribute :attr:`PySpice.Spice.Xyce.Server.XyceServer.XYCE_COMMAND`, you can also
pass the executable path to the simulator using::

   simulator = circuit.simulator(xyce_command='...')


Is Xyce 100% compatible with SPICE ?
------------------------------------

**No**, you have to read the user guide and reference manual to learn what are the actual differences!

In particular, the device models provided by vendors could need to be adapted for Xyce.

Notice, you can add the suffix **@xyce** to a *.lib* or *.mod* file in order to have a special
version for Xyce, for example *BAV21.lib@xyce*.  The PySpice Library Manager will include this
special version if it found one that correspond to the simulator used for the current simulation.

PySpice will try to incrementally provide a generic interface in the future.
