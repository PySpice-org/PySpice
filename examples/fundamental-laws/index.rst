This section discusses the fundamental laws of electronics.

Kirchhoff's circuit laws
------------------------

Kirchhoff's circuit laws are two equalities that constrain the current and voltage in electrical
circuits under some approximations.

Kirchhoff's current law (KCL) says at any node in an electrical circuit, the sum of currents flowing
into that node is equal to the sum of currents flowing out of that node:

.. math::

  \sum_{k=1}^n {I}_k = 0

This law is in fact a general principle of flux conservation.

Kirchhoff's voltage law (KVL) says that the sum of the branch's voltage along a closed path in the
network is null:

.. math::

  \sum_{k=1}^n {V}_k = 0

Kirchhoff's circuit laws are used by Spice to evaluate the voltages and currents in a circuit.

To go further on theses equalities, you can read online the section `22-3 of the Feynman Lectures on
Physics, Volume II <http://www.feynmanlectures.caltech.edu/II_22.html#Ch22-S3>`_.

.. http://en.wikipedia.org/wiki/Kirchhoff%27s_circuit_laws

Ohm's Law
---------

The Ohm's law is a simple model of a resistor which say that the current I flowing through a
resistor is proportional to the voltage U applied across it, this constant is called the resistance
(R).

.. math::

   U = R I

You will observe the same phenomenon with a pipe filled with water, the water's flow is proportional
to the declination of the pipe, more you incline the pipe, more you pressure the water within the
pipe.  Electron act as water and voltage as pressure.

In reality, the resistance depends of the temperature of the material, like many device parameters.
It is why we always simulate a circuit at a given temperature.

This law is important in circuit analysis, because it is a first approximation of any dipole for a
particular current and voltage.  Indeed we can approximate any curve locally by a linear relation.
If we know the current and voltage of a dipole under some conditions then we can approximate the
rate of change under a small variation of the current or voltage.  Spice uses this principle to
evalute a circuit at different times.

.. http://en.wikipedia.org/wiki/Ohm%27s_law

.. capacitor and inductor
.. superposition theorem

.. end
