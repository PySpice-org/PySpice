.. -*- Mode: rst -*-

.. _faq-page:

.. include:: project-links.txt
.. include:: abbreviation.txt

==========
 User FAQ
==========

How to typeset :code:`u_kΩ` or :code:`u_μV` in Python code ?
    There is three solutions if you don't have these Unicode characters available on your
    keyboard. The first one, is to use the ASCII alternative: :code:`u_kOhm` or :code:`u_uV.`.  The
    second one, is to define macros on your favourite editor.  The last one, is to customise your
    keyboard settings (If your on Linux look at https://www.x.org/wiki/XKB/).

How to set the Ngspice library path ?
    If the setting doesn't match your environment, then you have to set manually the attribute
    :attr:`PySpice.Spice.NgSpice.Shared.NgSpiceShared.LIBRARY_PATH`. Note you have to place a brace
    pair just before the extension, for example "C:\...\ngspice{}.dll".  You can also fix the value
    of :attr:`PySpice.Spice.NgSpice.Shared.NgSpiceShared.NGSPICE_PATH`.

How to set the Ngspice path ?
    If the setting doesn't match your environment, then you have to set manually the attribute
    :attr:`PySpice.Spice.Server.SpiceServer.SPICE_COMMAND`. This value can be passed as argument as
    well, see API documentation.

.. End
