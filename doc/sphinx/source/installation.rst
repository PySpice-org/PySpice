.. include:: project-links.txt
.. include:: abbreviation.txt

.. _installation-page:

==============
 Installation
==============

On Windows
----------

Firstly, you have to install Ngspice for Windows from this `page
<http://ngspice.sourceforge.net/download.html>`_.  Download this archive `ngspice 64 bit devel
<http://ngspice.sourceforge.net/experimental/ngspice-26plus-scope-inpcom-6-64.7z>`_ and unzip the
files in **C:\\Program Files\\Spice64**.

Secondly, you have to install the `Anaconda Distribution <https://www.anaconda.com/download/>`_.

Then open the `Anaconda Navigator <https://docs.continuum.io/anaconda/navigator/>`_ and launch a console for your root environment.

You can now run *pip* to install PySpice in your root environment using this command:

.. code-block:: sh

  pip install PySpice

On Linux
--------

Firstly, you have to install Ngspice and Python from your distribution. Then you can install Python using *pip* or from source. See supra.

How to get the Examples
-----------------------

Examples are not installed by ``pip`` or ``setup.pip``. The installation process only install
PySpice on your Python environment.

**You have to download the PySpice archive or clone the Git repository to get the examples.** See "Installation from Source".

Installation from PyPi Repository
---------------------------------

PySpice is available on the Python Packages |Pypi|_ repository at |PySpice@pypi|

Run this command in the console to install the latest release:

.. code-block:: sh

  pip install PySpice

Installation from Source
------------------------

The PySpice source code is hosted at |PySpice@github|

.. add link to pages ...

You have to solution to get the source code, the first one is to clone the repository, but if you
are not familiar with Git then you can simply download an archive either from the PySpice Pypi page
(at the bottom) or the GitHub page (see clone or download button).

To clone the Git repository, run this command in a console:

.. code-block:: sh

  git clone https://github.com/FabriceSalvaire/PySpice.git

Then to build and install PySpice run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install

Dependencies
------------

PySpice requires the following dependencies:

 * |Python|_ 3
 * |Numpy|_
 * |Matplotlib|_
 * |Ngspice|_
 * |CFFI|_ (only required for Ngspice shared)

Also it is recommanded to have these Python modules:

 * |IPython|_

.. * pip
.. * virtualenv

To generate the documentation, you will need in addition:

 * |Sphinx|_
 * circuit_macros and a LaTeX environment

Ngspice Compilation
-------------------

Usually Ngspice is available as a package on the most popular Linux distributions. But I recommend
to **check the compilation options** before to use it extensively. For example the Fedora package
enables too many experimental codes that have side effects. The recommended way to compile Ngspice
is given in the manual and in the ``INSTALLATION`` file. Ngspice is an example of complex software
where we should not enable everything without care.

.. :file:`INSTALLATION`

.. warning::

  Compilation option **--enable-ndev** is known to broke the server mode.
