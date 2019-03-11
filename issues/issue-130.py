####################################################################################################

from PySpice.Spice import Parser

####################################################################################################

source = """
.title test
Xld_D0 gnd:F12992 vdd:F3152 DNWPS AREA=16.072 PJ=20.54
Xld_D0 gnd:F12992 vdd:F3152
Xld_D0 gnd:F12992 vdd:F3152 DNWPS
Xld_D0 gnd:F12992 vdd:F3152 AREA=16.072 PJ=20.54
"""

parser = Parser.SpiceParser(source=source)
for statement in parser._statements:
    print(statement)
