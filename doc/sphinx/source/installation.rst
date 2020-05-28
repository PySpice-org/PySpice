.. include:: project-links.txt
.. include:: abbreviation.txt

.. _installation-page:

==============
 Installation
==============

**Note to Linux Packagers: Please do not create a PySpice package, PyPI and Anaconda do the job.**

You must install a Python environment and the NgSpice/Xyce simulator to use PySpice on your
computer.

If you are mainly doing data science, the easiest solution is probably to install the `Anaconda
Distribution <https://www.anaconda.com/products/individual>`_ which is specialised for this purpose.
You can also prefer its lightweight counterpart `Miniconda
<https://docs.conda.io/en/latest/miniconda.html>`_.

PySpice is available as a `conda <https://anaconda.org/condaforge/pyspice>`_ and `PyPI
<https://pypi.org/project/PySpice>`_ package.  For Anaconda there is two channels, the official one is
`conda-forge`, the second one `fabricesalvaire` **is only used for testing**.

**We recommend that you read the documentation in this order, first Windows to get the novice story,
then Linux to get the Unix OS story and finally OSX if you are concerned.**


On Windows
----------

The preferred solution for installing a Python environment on Windows is to install Anaconda or
Miniconda.

Once Anaconda is installed, open the `Anaconda Navigator
<https://docs.continuum.io/anaconda/navigator/>`_ and launch a **console** for your root environment.

You can now install PySpice using the `conda` or `pip` command:

.. code-block:: sh

  conda install -c conda-forge pyspice

  # or

  pip install PySpice

The easiest solution to install NgSpice on Windows is to use the PySpice tool to donwload and
install the DLL library for you.

.. code-block:: sh

    pyspice-post-installation --install-ngspice-dll

    pyspice-post-installation --check-install

On Linux
--------

On Linux, you can use the packages of your distribution.

NgSpice Installation
~~~~~~~~~~~~~~~~~~~~

If you do not want to use the Anaconda NgSpice package, NgSpice and its shared library are available on many distributions:

* Fedora: **libngspice**  https://apps.fedoraproject.org/packages/libngspice
* Ubuntu: **libngspice0** https://packages.ubuntu.com/search?suite=default&section=all&arch=any&keywords=libngspice&searchon=names
* Debian: **libngspice0** https://packages.debian.org/search?keywords=libngspice0

.. warning:: However it is advisable to check how NgSpice is compiled, especially if the maintainer
             has enabled experimental features !

For RPM distributions, such Fedora, RHEL and Centos, you can use this Copr repository
https://copr.fedorainfracloud.org/coprs/fabricesalvaire/ngspice

.. code-block:: sh

  dnf copr enable fabricesalvaire/ngspice
  dnf install libngspice

.. The RPM sources are available on `Pagure.io <https://pagure.io/copr-ngspice>`_

If you are not able to easily install the Ngspice shared library on your system, but you can install
the Ngspice program, then you can use the "subprocess" mode instead of the "shared" mode.  In this
case, you must define the default simulator globally using the attribute
``PySpice.Spice.Simulation.CircuitSimulator.DEFAULT_SIMULATOR = 'ngspice-subprocess'``.

Install the Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Linux, you have several possibilities to install the required Python environment:

#. if you are novice, the easiest solution is to install Anaconda or Miniconda
#. you can install Python packages from your distributions
#. if you are proficient with Python, you can manage a Virtual Environment for this purpose

Then you can install PySpice using the `conda` command if you are using Anaconda otherwise run the
`pip` command:

.. code-block:: sh

  conda install -c conda-forge ngspice-lib # optional
  conda install -c conda-forge pyspice

  # or

  pip install PySpice

  # and eventually

  pyspice-post-installation --check-install

On OSX
------

There are several ways to get Python on OSX:

 * use the built in Python (but check the version)
 * install `Miniconda <https://conda.io/miniconda.html>`_
 * install a full `Anaconda Distribution <https://www.anaconda.com/download/>`_.
 * install from Brew: ``brew install python3`` **(reported to work)**

To install PySpice, please read the Linux instructions.

The Ngspice shared library is also available from Brew:

.. code-block:: sh

  brew install libngspice


How to get the Examples
-----------------------

The examples are not installed by ``pip`` or ``setup.py``. The installation process only install
the PySpice module on your Python environment.

**You have to download the PySpice archive or clone the Git repository to get the examples.** See "Installation from Source".

Or you can simply run this command:

.. code-block:: sh

    pyspice-post-installation --download-example


Install a more recent version from GitHub using pip
---------------------------------------------------

If you want to install a version that is not yet released on Pypi, you can use one of theses
commands to install the stable or devel branch:

.. code-block:: sh

  pip install git+https://github.com/FabriceSalvaire/PySpice

  pip install git+https://github.com/FabriceSalvaire/PySpice@devel


Installation from Source
------------------------

PySpice source code is hosted at |PySpice@github|

You have two solution to get the source code, the first is to clone the repository, but if you are
not familiar with Git, you can simply download an archive from the GitHub page (using the download
button) or from the PySpice Pypi page.

To clone the Git repository, run this command:

.. code-block:: sh

  git clone https://github.com/FabriceSalvaire/PySpice.git

Then to build and install PySpice run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install


Dependencies
------------

PySpice dependencies are listed in:

* https://github.com/FabriceSalvaire/PySpice/blob/master/requirements.txt
* https://github.com/FabriceSalvaire/PySpice/blob/master/requirements-dev.txt (for devel only)


How to Generate the Documentation
---------------------------------

To generate the documentation, you will need basically in addition theses Python modules (see
``requirements-dev.txt``):

* `invoke <http://www.pyinvoke.org>`_
* |Sphinx|_
* `Pyterate <https://github.com/FabriceSalvaire/Pyterate>`_

and also these dependencies (harder to install) to generate some figures:

* `ImageMagick <https://imagemagick.org/script/index.php>`_ (to convert SVG to PNG for Notebooks)
* `circuit_macros <https://ece.uwaterloo.ca/~aplevich/Circuit_macros>`_ and a LaTeX environment
* `mutool <https://mupdf.com/docs/manual-mutool-convert.html>`_ (to convert circuit_macros PDF to PNG)

Then the procedure is basically to run these commands:

.. code-block:: sh

    inv doc.make-examples
    inv doc.make-api


Ngspice Compilation
-------------------

Usually Ngspice is available as a package on the most popular Linux distributions. But I recommend
to **check the compilation options** before to use it for serious projects.

The recommended way to compile Ngspice is given in the manual and in the ``INSTALLATION``
file. Ngspice is an example of complex software where we should not enable everything without care.

.. warning::

  The compilation option **--enable-ndev** is known to broke the server mode.

The recommended way to compile Ngspice on Fedora is:

.. code-block:: sh

  mkdir ngspice-32-build
  pushd ngspice-32-build

  /.../ngspice-32/configure \
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
a user account on this `sign-in page <https://xyce.sandia.gov/downloads/sign-in.html>`_ to get the
source or download an executable, i.e. you have to provide an email address to Sandia.

The building procedure is clearly explained in the `building guide
<https://xyce.sandia.gov/documentation/BuildingGuide.html>`_.

You can also find the sources for a Xyce RPM package in this `Git repository
<https://pagure.io/copr-xyce>`_.
