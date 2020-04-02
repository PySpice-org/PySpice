####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Parser import SpiceParser

####################################################################################################

# source = """
# .title Test
# V1  vp GND dc 1.65 ac 0.5
# V2  vn GND dc 1.65 ac -0.5
# C2  Vout GND 4p
# C1  /3 Vout 6.9p
# M7  Vout /6 VDD VDD p_33 W=25.9u L=0.9u
# M6  Vout /3 GND GND n_33 W=92.04u L=1.4u
# M2  /3 vp /1 VDD p_33 W=51.78u L=0.9u
# M1  /2 vn /1 VDD p_33 W=51.78u L=0.9u
# M4  /3 /2 GND GND n_33 W=46.02u L=1.4u
# M3  /2 /2 GND GND n_33 W=46.02u L=1.4u
# M5  /1 /6 VDD VDD p_33 W=12.95u L=0.9u
# V0  VDD GND 3.3
# M8  /6 /6 VDD VDD p_33 W=1.3u L=0.9u
# I1  /6 GND 10u
#
#.lib CMOS_035_Spice_Model.lib tt
#
#.end
# """

source = """
.title Test
V1 vp GND dc 1.65 ac 0.5
M7 Vout /6 VDD VDD p_33 l=0.9u w=25.9u
M6 Vout /3 GND GND n_33 l=1.4u w=92.04u
M2 /3 vp /1 VDD p_33 l=0.9u w=51.78u
M1 /2 vn /1 VDD p_33 l=0.9u w=51.78u
M4 /3 /2 GND GND n_33 l=1.4u w=46.02u
M3 /2 /2 GND GND n_33 l=1.4u w=46.02u
M5 /1 /6 VDD VDD p_33 l=0.9u w=12.95u
V0 VDD GND 3.3
M8 /6 /6 VDD VDD p_33 l=0.9u w=1.3u
I1 /6 GND 10u
.lib CMOS_035_Spice_Model.lib tt
""".strip()

parser = SpiceParser(source=source)
circuit = parser.build_circuit()
source2 = str(circuit)
for line1, line2 in zip(source.splitlines(), source2.splitlines()):
    print('-'*100)
    print(line1 + '|')
    print(line2 + '|')
    assert(line1 == line2)
