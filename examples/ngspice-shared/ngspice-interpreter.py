####################################################################################################

#r#
#r# =====================
#r#  NgSpice Interpreter
#r# =====================
#r#
#r# This example explains how to use the NgSpice binding.
#r#

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.NgSpice.Shared import NgSpiceShared

####################################################################################################

ngspice = NgSpiceShared.new_instance()

print(ngspice.exec_command('version -f'))
print(ngspice.exec_command('print all'))
print(ngspice.exec_command('devhelp'))
print(ngspice.exec_command('devhelp resistor'))

circuit = '''
.title Voltage Multiplier

.SUBCKT 1N4148 1 2
*
R1 1 2 5.827E+9
D1 1 2 1N4148
*
.MODEL 1N4148 D
+ IS = 4.352E-9
+ N = 1.906
+ BV = 110
+ IBV = 0.0001
+ RS = 0.6458
+ CJO = 7.048E-13
+ VJ = 0.869
+ M = 0.03
+ FC = 0.5
+ TT = 3.48E-9
.ENDS

Vinput in 0 DC 0V AC SIN(0V 10V 50Hz 0s 0Hz)
C0 in 1 1mF
X0 1 0 1N4148
C1 0 2 1mF
X1 2 1 1N4148
C2 1 3 1mF
X2 3 2 1N4148
C3 2 4 1mF
X3 4 3 1N4148
C4 3 5 1mF
X4 5 4 1N4148
R1 5 6 1MegOhm
.options TEMP = 25°C
.options TNOM = 25°C
.options filetype = binary
.options NOINIT
.ic
.tran 0.0001s 0.4s 0s
.end
'''

ngspice.load_circuit(circuit)

print(ngspice.show('c3'))
print(ngspice.showmod('c3'))

ngspice.run()
print('Plots:', ngspice.plot_names)

print(ngspice.ressource_usage())
print(ngspice.status())

plot = ngspice.plot(simulation=None, plot_name=ngspice.last_plot)
print(plot)

# ngspice.quit()
