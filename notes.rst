* fix copyright and license

* plot scale mA
* units
* Fixme: i(vinput) -> analysis.vinput
* element ddp, node voltage, current : cf. Modelica
    (analysis['in'] - analysis.out) / float(circuit['R1'].resistance
* OpAmp / Transformer 
* waveform slice : cf. numpy
* analysis.in is invalid

----

* define netlist
* expand variables
* current probes? voltage source Vxxx#branch  *--Vxxx--...--*
* flatten spice desk using netlist and libraries
* add simulation instructions
* expand variables ?
* run ngspice
* read output
* analyse or save data
