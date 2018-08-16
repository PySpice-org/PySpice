.. include:: project-links.txt
.. include:: abbreviation.txt

.. _user-faq-page:

==========
 User FAQ
==========

How to get help or report an issue ?
------------------------------------

.. There is no mailing list or forum actually, so you can either contact me or fill an issue on Github.

If you want to **discuss or ask questions on PySpice**, you can subscribe and post messages on the
**PySpice User** mailing list.

There is actually three lists running on Google Groups (*):

`User List <https://groups.google.com/forum/#!forum/pyspice-user>`_
  List for PySpice users
`Announce List <https://groups.google.com/forum/#!forum/pyspice-announce>`_
  List for announcements regarding PySpice releases and development
`Devel List <https://groups.google.com/forum/#!forum/pyspice-devel>`_
  List for developers of PySpice

**If you encounter an issue, please fill an issue** on the `Issue Tracker <https://github.com/FabriceSalvaire/PySpice/issues>`_.

(*) Despite Google Groups has many drawbacks, I don't have actually enough resources to run GNU Mailman or
Discourse on my own IT infrastructure.

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

How to set the Ngspice library path ?
-------------------------------------

If the setting doesn't match your environment, then you have to set manually the attribute
:attr:`PySpice.Spice.NgSpice.Shared.NgSpiceShared.LIBRARY_PATH`. Note you have to place a brace pair
just before the extension, for example "C:\...\ngspice{}.dll".  You can also fix the value of
:attr:`PySpice.Spice.NgSpice.Shared.NgSpiceShared.NGSPICE_PATH`.

How to set the Ngspice path ?
-----------------------------

If the setting doesn't match your environment, then you have to set manually the attribute
:attr:`PySpice.Spice.Server.SpiceServer.SPICE_COMMAND`. This value can be passed as argument as
well, see API documentation.

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

Is Xyce 100% compatible with SPICE ?
------------------------------------

**No**, you have to read the user guide and reference manual to learn what are the actual differences!

In particular, the device models provided by vendors could need to be adapted for Xyce.

Notice, you can add the suffix **@xyce** to a *.lib* or *.mod* file in order to have a special
version for Xyce, for example *BAV21.lib@xyce*.  The PySpice Library Manager will include this
special version if it found one that correspond to the simulator used for the current simulation.

PySpice will try to incrementally provide a generic interface in the future.
