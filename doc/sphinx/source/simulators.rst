.. _simulators-page:

.. include:: abbreviation.txt

============
 Simulators
============

This page presents the main open source circuit simulators which are actually available.

You can get an overview of what is going on FOSS circuit simulation in the `FOSDEM'17 Electronic
Design Automation Track
<https://archive.fosdem.org/2017/schedule/track/electronic_design_automation_eda>`_

Ngspice
-------

|Ngspice|_ is a mixed-level/mixed-signal circuit simulator, based on three open source software
packages: Spice3f5, Cider1b1 and Xspice.

*Spice3f5* is the last Berkeley’s release of Spice3 simulator family.

*Cider* couples Spice3f5 circuit level simulator to DSIM device simulator to provide greater
simulation accuracy of critical devices. DSIM devices are described in terms of their structures and
materials.

*Xspice* is an extension to Ngspice that provides code modeling support and simulation of digital
components through an embedded event driven algorithm.

.. is an update of
   It includes some extension like XSPICE and CIDER.  XSPICE allows to add event-driven simulation
   capabilities, and CIDER implements a mixed-level circuit and device simulator.

The main drawback of Ngspice is to inherit the old C code base of Berkeley SPICE.

To read more on Ngspice, look at the `Ngspice documentation page <http://ngspice.sourceforge.net/docs.html>`_.

Xyce
----

|Xyce|_ is an open source, SPICE-compatible, high-performance analog circuit simulator, capable of
solving extremely large circuit problems developed at `Sandia National Laboratories
<http://www.sandia.gov>`_.

Sandia is an US laboratory involved in the national nuclear weapons program. Its French counterpart
is the Alternative Energies and Atomic Energy Commission or CEA.

Sandia has released several open source porgrams, you can find a list on its `Wikipedia page
<https://en.wikipedia.org/wiki/Sandia_National_Laboratories>`_.

Xyce was developed from scratch at Sandia in order to meet special needs like the simulation of
chips under radiations.  Xyce is developed in C++.

Gnucap
------

The initial version of Gnucap was developed by Albert Davis in 1983, then it was released as a GNU project in 2001.

Like Xyce, Gnucap was developed from scratch in C++.

In 2015, a fork `Gnucap-uf <http://www.em.informatik.uni-frankfurt.de/gnucap>`_ targeted at research
and experiments was released by the University of Frankfurt in Germany.

Actually Felix Salfelder is performing an unforking and adding new extensions.  Look at its `talk
<https://archive.fosdem.org/2017/schedule/event/gnucap>`_ at FOSDEM'17 for further information.

Qucs
----

`QUCS <http://qucs.sourceforge.net>`_ (Quite Universal Circuit Simulator) was an attempt to develop
a circuit simulator featuring an IDE similar to LtSpice by Michael Margraf, Stefan Jahn et al.

QUCS is actually slowly maintained, a Qt4 port from Qt3 is on going since several years. 

You can find an update of the project on the `Guilherme Brondani Torri Talk
<https://archive.fosdem.org/2017/schedule/event/qucs>`_ at FOSDEM'17.
