OpenSPICE is a lightweight, Python-native circuit simulator. It is bundled with
PySpice. As a result, to use OpenSPICE, replace any usage of PySpice.Spice.NgSpice.Shared
with PySpice.Spice.OpenSPICE.Shared in your PySpice code. Also, if you call
the simulator method in the Circuit class, be sure to provide "OpenSPICE" and not
"NgSpice" as the simulator argument. Other than that, pretty much all of your
PySpice code should work the same.

One last detail: OpenSPICE does NOT support variable timestepping. Thus, be sure
to use a sufficiently small timestep value for accurate results.
