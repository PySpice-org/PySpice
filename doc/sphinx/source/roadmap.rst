.. _roadmap-page:

.. include:: abbreviation.txt
.. include:: project-links.txt

=========
 Roadmap
=========

V1.2
----

* Support `Xyce <https://xyce.sandia.gov>`_ simulator.  Xyce is an open source, SPICE-compatible,
  high-performance analog circuit simulator, capable of solving extremely large circuit problems
  developed at Sandia National Laboratories.  Xyce will make PySpice suitable for industry a
  research use.
* Improve unit : rebase unit to Numpy array (ongoing)

.. What are the planned features ?

Some ideas for the future
-------------------------

These features are planned in the future:

* Improve the analyse experience
* Complete Spice expression parser
* Complete missing devices and simulations
* Jupyter notebook examples

Some other ideas are:

* Implement a Modelica backend. |Modelica|_ is a very interesting solution for transient analysis.

The implementation of a simulator in Python is not planned since it would be too challenging to
release a full featured and proved simulator. However you could look at the project `Ahkab
<https://ahkab.github.io/ahkab>`_ which aims to implement such Python based simulator.  Notice any
of the projects like Ngspice or Ahkab are compliant with industrial quality assurance processes.
