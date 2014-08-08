.. -*- Mode: rst -*-

.. -*- Mode: rst -*-

.. |ohloh| image:: https://www.ohloh.net/accounts/230426/widgets/account_tiny.gif
   :target: https://www.openhub.net/accounts/fabricesalvaire
   :alt: Fabrice Salvaire's Ohloh profile
   :height: 15px
   :width:  80px

.. |Ngspice| replace:: Ngspice
.. _Ngspice: http://ngspice.sourceforge.net

.. |Python| replace:: Python
.. _Python: http://python.org

.. |PyPI| replace:: PyPI
.. _PyPI: https://pypi.python.org/pypi

.. |Numpy| replace:: Numpy
.. _Numpy: http://www.numpy.org

.. |Matplotlib| replace:: Matplotlib
.. _Matplotlib: http://matplotlib.org

.. |IPython| replace:: IPython
.. _IPython: http://ipython.org

.. |Sphinx| replace:: Sphinx
.. _Sphinx: http://sphinx-doc.org

.. End

==============
PySpice V0.1.0
==============

The user and API documentation is hosted on the project `homepage <http://fabricesalvaire.github.io/PySpice>`_.

Written by `Fabrice Salvaire <http://fabrice-salvaire.pagesperso-orange.fr>`_.

==========
 Overview
==========

.. -*- Mode: rst -*-


==============
 Introduction
==============

PySpice is a |Python|_ library which interplay with Berkeley SPICE, the
industrial circuit simulator reference.

SPICE (Simulation Program with Integrated Circuit Emphasis) was developed at the Electronics
Research Laboratory of the University of California, Berkeley in 1973 by Laurence Nagel with
direction from his research advisor, Prof. Donald Pederson. Then Spice emerged as an industrial
standard through its descendant and is still the reference 40 years later.

The aim of PySpice is to address several needs:

 * SPICE language is fine to describe a circuit, but it lacks a real language for circuit
   steering. By contrast Python is a powerful high level, oriented object and dynamic language which
   is perfectly suited for steering and reusing circuit. But it comes at the price its more general
   syntax is less fluent than SPICE for circuit description.

 * Ngspice provides some extension to Berkeley SPICE for data analysis, but its interactive
   environment or TCL module are now outdated. By contrast Python has scientific framework like
   |Numpy|_ and |Matplotlib|_ that compete with Matlab.

 * Ngspice source code is derived from Berkeley SPICE and thus has a very old basis. Moreover the
   sources are poorly documented. So it is really difficult to understand how it works and modify
   it. PySpice could serve to easily experiment extension.

As opposite to other SPICE derivatives, PySpice focus on programming and not on graphical user
interface. Thus it doesn't feature a schematic capture editor and we cannot pickup a node or an
element and plot the associated waveform.

The main features of PySpice are:

 * actually PySpice only supports the |Ngspice|_ flavour
 * an oriented-object API to describe circuit in a way similar to SPICE
 * a library and model manager that index recursively a directory
 * an incomplete SPICE parser (mainly used for the library and model indexer)
 * a SPICE server to run the simulator and to get back the result as Numpy array
 * some data analysis add-on

.. Warning:: The API is quite unstable. Some efforts is made to have a smooth API.

.. Warning:: Ngspice is provided without any warranty. Thus use it with care for real design. Best
	     is to cross check the simulation using others simulators.

.. Warning:: Simultation is a tool and not a perfect view of the real world.

.. End

.. -*- Mode: rst -*-

.. _installation-page:


==============
 Installation
==============

The installation of PySpice by itself is quite simple. However it will be easier to get the
dependencies on a Linux desktop.

Dependencies
------------

PySpice requires the following dependencies:

 * |Python|_
 * |Numpy|_
 * |Matplotlib|_
 * |Ngspice|_

Also it is recommanded to have these Python modules:

 * |IPython|_
 * pip
 * virtualenv

For development, you will need in addition:

 * |Sphinx|_
 * circuit_macros and a LaTeX environment

Ngspice Compilation
-------------------

Usually Ngspice is available as a package in the major Linux distributions. But I recommend to check
the compilation options before to use it extensively. For example the Fedora package enables too
many experimental codes that have side effects. The recommended way to compile Ngspice is given in
the manual and the ``INSTALLATION`` file. Ngspice is an example of complex software where we should
not enable everything without care.

.. :file:`INSTALLATION`

.. warning::

  For the following, the compilation option **--enable-ndev** is known to broke the server mode.

Installation from PyPi Repository
---------------------------------

PySpice is made available on the |PyPi|_ repository. Run this command to install the last release:

.. code-block:: sh

  pip install PySpice

Installation from Source
------------------------

The PySpice source code is hosted at `github <http://github.com/FabriceSalvaire/PySpice>`_.

To clone the Git repository, run this command in a terminal:

.. code-block:: sh

  git clone git@github.com:FabriceSalvaire/PySpice.git

Then to build and install PySpice run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install

.. End

.. End
