.. include:: project-links.txt
.. include:: abbreviation.txt

.. _installation-page:

==============
 Installation
==============

**Note to Packagers: Please don't create PySpice package (PiPY do the job)**

On Windows
----------

Firstly, you have to install Ngspice for Windows from this `page
<http://ngspice.sourceforge.net/download.html>`_.  Download the archive
:file:`ngspice-30_dll_64.zip` from thex `release page
<https://sourceforge.net/projects/ngspice/files/ng-spice-rework/28>`_ and unzip the files in
`C:\\Program Files\\Spice64_dll`.

Secondly, you have to install the `Anaconda Distribution <https://www.anaconda.com/download/>`_ or
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ so as to get a full featured Python 3
environment.

Then open the `Anaconda Navigator <https://docs.continuum.io/anaconda/navigator/>`_ and launch a console for your root environment.

You can now run *pip* to install PySpice in your root environment using this command:

.. code-block:: sh

  pip install PySpice

On Linux
--------

Firstly, you have to install Python 3 from your distribution.

The Ngspice shared library is actually not available on several distributions including Fedora and
Ubuntu. **I encourage you to report this issue on your distribution.**

On Fedora, I recommend to don't install the Fedora's *ngspice* package since it is **badly compiled
and maintained**.  To install the Ngspice shared library, you can use my `Ngspice Copr repository
<https://copr.fedorainfracloud.org/coprs/fabricesalvaire/ngspice>`_:

.. code-block:: sh

  dnf copr enable fabricesalvaire/ngspice
  dnf install libngspice

The RPM sources are available on `Pagure.io <https://pagure.io/copr-ngspice>`_

If you are not able to install the Ngspice shared library easily on your system, but you can install
the Ngspice program, then you can use the "subprocess" mode in replacement of the "shared" mode.  In
this case, you have to set globally the default simulator using the attribute
:attr:`PySpice.Spice.Simulation.CircuitSimulator.DEFAULT_SIMULATOR` to `ngspice-subprocess`.

Then you can install PySpice using *pip* or from source. See supra.

On OSX
------

There are several ways to get Python on OSX:

 * use the built in Python
 * install `Miniconda <https://conda.io/miniconda.html>`_
 * install the `Anaconda Distribution <https://www.anaconda.com/download/>`_.
 * install from Brew `brew install python3` **(reported to work)**

The Ngspice shared library is available from Brew:

.. code-block:: sh

  brew install libngspice

You can install PySpice using *pip* or from source. See supra.

How to get the Examples
-----------------------

Examples are not installed by ``pip`` or ``setup.pip``. The installation process only install
PySpice on your Python environment.

**You have to download the PySpice archive or clone the Git repository to get the examples.** See "Installation from Source".

Note: We could install examples with pip, but files would be more difficult to locate in the
environment directory.

Installation from PyPi Repository
---------------------------------

PySpice is available on the Python Packages |Pypi|_ repository at |PySpice@pypi|

Run this command in the console to install the latest release:

.. code-block:: sh

  pip install PySpice

Install a more recent version from Github
-----------------------------------------

If you want to install a version which is not yet released on Pypi, you can use one of theses
commands to install the stable or devel branch:

.. code-block:: sh

  pip install git+https://github.com/FabriceSalvaire/PySpice

  pip install git+https://github.com/FabriceSalvaire/PySpice@devel

Installation from Source
------------------------

The PySpice source code is hosted at |PySpice@github|

.. add link to pages ...

You have two solution to get the source code, the first one is to clone the repository, but if you
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

.. warning::

  Compilation option **--enable-ndev** is known to broke the server mode.

The recommended way to compile Ngspice on Fedora is:

.. code-block:: sh

  mkdir ngspice-27-build
  pushd ngspice-27-build

  /.../ngspice-27/configure \
    --prefix=/usr/local \
    --enable-xspice \
    --disable-debug \
    --enable-cider \
    --with-readline=yes \
    --enable-openmp \
    --with-ngshared

   make # -j4
   make install

How to get Xyce ?
-----------------

Despite Xyce is released under the therms of the GPLv3 licence, Sandia requires actually you create
a user account on this `sign-in page <https://xyce.sandia.gov/downloads/sign-in.html>`_ so as to get
the source or download an executable, i.e. you have to provide your email address to Sandia.

The building procedure is clearly explained in the `building guide
<https://xyce.sandia.gov/documentation/BuildingGuide.html>`_.

You can also find the sources for a Xyce RPM package in this `Git repository
<https://pagure.io/copr-xyce>`_.
