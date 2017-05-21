from PySpice.Pipe import SpiceServer

spice_server = SpiceServer()

ngspice_input_template = """
.title Simple Rectifier
.subckt 1N4148 1 2
R1 1 2 5.827E+9
D1 1 2 1N4148
.model 1N4148 D IS = 4.352E-9 N = 1.906 BV = 110 IBV = 0.0001 RS = 0.6458 CJO = 7.048E-13 VJ = 0.869 M = 0.03 FC = 0.5 TT = 3.48E-9
.ends
Vinput in 0 DC 0V SIN(0V {line_peak_voltage}V {frequence}Hz)
xD in out 1N4148
Cload out 0 100uF
Rload out 0 1k
*
.options TEMP=25
.options TNOM=25
*.options NODE
.options NOINIT
.options filetype = binary
.save V(in) V(out)
.tran {step_time} {end_time}
.end
"""

frequence = 50
perdiod = 1. / frequence

ngspice_input = ngspice_input_template.format(line_peak_voltage=10,
                                              frequence=frequence,
                                              step_time=perdiod/200,
                                              end_time=perdiod*10
                                              )

raw_file = spice_server(ngspice_input)

print(raw_file.data.dtype.fields)
print(raw_file.data)
