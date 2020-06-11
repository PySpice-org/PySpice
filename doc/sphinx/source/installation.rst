.. include:: project-links.txt
.. include:: abbreviation.txt

.. _installation-page:

==============
 Installation
==============

You must install a Python environment and the Ngspice/Xyce simulator to use PySpice on your
computer.  Since there are many ways to do this, we will only explain the easiest ones in details.

In Python, the standard way is to use a **Virtual Environment** and the **pip** tool, look at this
`guide <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments>`_ for
further information.

But if you are mainly doing data science, the **easiest solution** is probably to install the `Anaconda
Distribution <https://www.anaconda.com/products/individual>`_ which is specialised for this purpose.
You can also prefer its lightweight counterpart `Miniconda
<https://docs.conda.io/en/latest/miniconda.html>`_.

Anaconda has the advantage to provide a self consistent environment to the user, for example it
installs automatically Ngspice for you when you install PySpice.  But for this reason, especially on
Linux, an Anaconda distribution will require much more disk space than a virtual environment.

.. note:: **We recommend that you read the documentation in this order, first Windows to get the
	  novice story, then Linux to get the Unix OS story and finally OSX if you are concerned.**


PySpice Packages
----------------

**Note to Linux Packagers: Please do not create a PySpice package, PyPI and Anaconda do the job.**

PySpice is available as a `Anaconda <https://anaconda.org/condaforge/pyspice>`_ and `PyPI
<https://pypi.org/project/PySpice>`_ package.  For Anaconda there is two channels, the official one is
`conda-forge`, the second one `fabricesalvaire` **is only used for testing**.


Ngspice on conda-forge
----------------------

.. note:: If you decide to use the conda-forge package, you do not need to install Ngspice manually
          since it is provided as a dependency package: ngspice-lib.

However if you want the Ngspice executable on your system, then run this command:

.. code-block:: sh

  conda install -c conda-forge ngspice-exe  # install the ngspice executable

  conda install -c conda-forge ngspice      # install the master package
  conda install -c conda-forge ngspice-lib  # install the ngspice library


PySpice Continuous Integration
------------------------------

PySpice is tested on theses platforms:

* Travis CI :

  * Bionic Ubuntu Linux  (Ngspice is compiled manually)
  * macOS 10.14.4 Mojave  (use Brew)
  * Windows 10.0.17134  (use `Chocolatey <https://chocolatey.org>`_)

* Azure CI

* Fedora


On Windows
----------

The preferred solution for installing a Python environment on Windows is to install Anaconda or
Miniconda.

Once Anaconda is installed, open the `Anaconda Navigator
<https://docs.continuum.io/anaconda/navigator/>`_ and launch a **console** for your root environment.

Then the only thing to do to get PySpice on Anaconda is to run this command:

.. code-block:: sh

  conda install -c conda-forge pyspice

**The following steps are not required for the conda-forge package.**

As an alternative to conda, you can use the pip tool: ``pip install PySpice``

The easiest solution to install Ngspice on Windows is to use the PySpice tool to donwload and
install the Windows 64-bit DLL library for you:

.. code-block:: sh

    pyspice-post-installation --install-ngspice-dll


Then check your installation using the *multi-platform* command:

.. code-block:: sh

    pyspice-post-installation --check-install


On Linux
--------

You are free to install the packages of your Linux distribution.

Ngspice Installation
~~~~~~~~~~~~~~~~~~~~

If you do not want to use Anaconda, Ngspice and its shared library are available on many distributions:

* Fedora: **libngspice**  https://apps.fedoraproject.org/packages/libngspice
* Ubuntu: **libngspice0** https://packages.ubuntu.com/search?suite=default&section=all&arch=any&keywords=libngspice&searchon=names
* Debian: **libngspice0** https://packages.debian.org/search?keywords=libngspice0

.. warning:: However it is advisable to check how Ngspice is compiled, especially if the maintainer
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

Install the Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Linux, you have several possibilities to install the required Python environment:

#. if you are novice, the easiest solution is to install Anaconda or Miniconda
#. you can install Python packages from your distributions
#. if you are proficient with Python, you can manage a Virtual Environment for this purpose

Then you can install PySpice using the `conda` command if you are using Anaconda otherwise run the
`pip` command:

.. code-block:: sh

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
 * install from Brew: ``brew install python3``

To install PySpice, please read the Linux instructions.

The Ngspice shared library is also available from Brew:

.. code-block:: sh

  brew install libngspice

Brew links:

 * https://formulae.brew.sh/formula/ngspice
   https://github.com/Homebrew/homebrew-core/blob/master/Formula/ngspice.rb
 * https://formulae.brew.sh/formula/libngspice
   https://github.com/Homebrew/homebrew-core/blob/master/Formula/libngspice.rb


How to get the Examples
-----------------------

Short answer, you can simply run this command:

.. code-block:: sh

    pyspice-post-installation --download-example

Long answer, the examples are not installed by ``pip`` or ``setup.py``.  The installation process only install the
PySpice module on your Python environment.  You have to download the PySpice archive or clone the
Git repository to get the examples.  See "Installation from Source".


Install a more Recent Version from GitHub using pip
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


Tips to Set the Development Environment
---------------------------------------

**Set the PYTHONPATH on Windows:**

 * To set this variable from PowerShell, use: ``$env:PYTHONPATH=’list;of;paths’`` just before you launch Python.
 * To set this variable from the Command Prompt, use: ``set PYTHONPATH=list;of;paths``

**Fix CP1252 / Unicode errors on Windows:**

In some circumstance Windows uses the CP1252 encoding, to change this use: ``$env:PYTHONIOENCODING="utf_8"``.


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

Usually Ngspice is available as a package on the most popular Linux distributions. But we recommend
to **check the compilation options** before to use it for serious projects.

The procedure to compile Ngspice is explained in the manual and in the ``INSTALLATION`` file. Ngspice is
an example of complex software where we should not enable everything without care.

.. warning::

  The compilation option **--enable-ndev** is known to broke the server mode.

The recommended way to compile Ngspice on Linux is:

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

.. note:: PySpice source has invoke tasks to compile the Ngspice shared library on Unix, look at
	  *ngspice.* tasks using the command ``inv -l`` to list them.


How to get Xyce ?
-----------------

Despite Xyce is released under the therms of the GPLv3 licence, Sandia requires actually you create
a user account on this `sign-in page <https://xyce.sandia.gov/downloads/sign-in.html>`_ to get the
source or download an executable, i.e. you have to provide an email address to Sandia.

The building procedure is clearly explained in the `building guide
<https://xyce.sandia.gov/documentation/BuildingGuide.html>`_.

You can also find the sources for a Xyce RPM package in this `Git repository
<https://pagure.io/copr-xyce>`_.
