.. include:: abbreviation.txt
.. include:: project-links.txt

.. raw:: html

    <style>
        .small-text {font-size: smaller}

	.spacer {height: 30px}

        .reduced-width {
	    max-width: 800px
        }

        .row {clear: both}

        @media only screen and (min-width: 1000px),
               only screen and (min-width: 500px) and (max-width: 768px){

            .column {
                padding-left: 5px;
                padding-right: 5px;
                float: left;
            }

            .column2  {
                width: 50%;
            }

            .column3  {
                width: 33.3%;
            }
        }
    </style>

###################################################################
 Simulate Electronic Circuit using Python and the Ngspice Simulator
###################################################################

.. image:: /_static/logo.png
   :alt: PySpice logo
   :width: 800

.. raw:: html

   <div class="reduced-width">

********
Overview
********

PySpice is a free and open source (*) Python module which interface |Python|_ and the |Ngspice|_ circuit
simulator, a clone of the famous `SPICE <https://en.wikipedia.org/wiki/SPICE>`_ circuit
simulator.

.. rst-class:: small-text

    (*) PySpice is licensed under GPLv3 therms.

PySpice implements a Ngspice binding and provides an oriented object API on top of SPICE, the
simulation output is converted to |Numpy|_ arrays for convenience.

PySpice requires Python 3 and works on Linux, Windows and OS X.

:ref:`To read more on PySpice <overview-page>`

.. raw:: html

   <div class="spacer"></div>

.. rst-class:: clearfix row

.. rst-class:: column column2

:ref:`news-page`
================

What's changed in versions

.. rst-class:: column column2

:ref:`Installation-page`
========================

How to install PySpice on your system

.. rst-class:: column column2

:ref:`user-faq-page`
====================

Answers to frequent questions

.. rst-class:: column column2

:ref:`examples-page`
====================

Many examples to learn how to use PySpice.  To learn more on how to run theses examples, read the
:ref:`introduction to the examples <example-introduction-page>`.

.. rst-class:: column column2

:ref:`development-page`
=======================

How to contribute to the project

.. rst-class:: column column2

:ref:`reference-manual-page`
============================

Technical reference material, for classes, methods, APIs, commands.

.. raw:: html

   </div>

.. why here ???

.. rst-class:: clearfix row

.. raw:: html

   <div class="spacer"></div>

*******************
 Table of Contents
*******************

.. toctree::
  :maxdepth: 3
  :numbered:

  overview.rst
  news.rst
  roadmap.rst
  installation.rst
  faq.rst
  example-introduction.rst
  examples/index.rst
  example-whish-list.rst
  design-notes.rst
  reference-manual.rst
  development.rst
  related-projects.rst
  bibliography.rst

.. End
