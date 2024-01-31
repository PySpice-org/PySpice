####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 jmgc / Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

from pathlib import Path
import shutil
import unittest

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.EBNFSpiceParser import SpiceParser
import os

data = """* Data test
*More notes

.MODEL 2N2222 NPN
Q2N2222 Nc Nb Ne 2N2222

BG1 IOUTp IOUTm I={TABLE {V(VCp,VCm)} =
+(0, 12.09e-6)
+(26.6667, 0.0002474)
+(53.3333, 0.00029078)
+(71.1111, 0.0003197)
+(72, 0.00032115)
+(73.7778, 0.00032404)
+(75.5556, 0.00032693)
+(77.3333, 0.00032982)
+(79.1111, 0.00033272)
+(80, 0.00275)}

G1N 21 98 (6,15) 26E-6

E23 21 98 (6,15) 26E-6

BG2 IOUT- IOUT+ I={IF( (V(VC+,VC-)<=0),0,GAIN*V(VC+,VC-) )}

FB    7 99 POLY(5) VB VC VE VLP VLN 0 147.3E6 -100E6 100E6 100E6 -100E6

R 1 2 600000 MDR	
.MODEL MDR R TC1=0 TC2=0

.SUBCKT AND2 A B Y
BEINT YINT 0 V = {IF(V(A) > 0.5 & V(B) > 0.5, 1, 0)}
RINT YINT Y 1
CINT Y 0 1n
.ENDS AND2

E1 3 0 5 0 10

G2N 21 3 POLY(1) 1 3 0 1.57E-6 -0.97e-7

.MODEL DI_HBS410 D  ( IS=130.2n RS=6.366m BV=1.229k IBV=1m
+ CJO=69.01p  M=0.295 N=2.075 TT=4.32µ)

.MODEL npnct NPN

.PARAM t3 = {True?1:0}
.PARAM f3 = {False?1:0}
.PARAM a = {a + b}
.PARAM b = {a - b}
.PARAM c = {(a + b)}
.PARAM d = {(a - b)}
.PARAM a = {a * b}
.PARAM b = {a / b}
.PARAM c = {(a * b)}
.PARAM d = {(a / b)}
.PARAM d = {(a / b) * c}
.PARAM t3 = {if(1<2,1,0)}
.PARAM t3 = {if((1<2),(1),(0))}
.PARAM f3 = {2<=1?1:0}
.PARAM c = {a + (b + c)}
.PARAM d = {(a + b) + c}
.PARAM d = 1
.PARAM d = {1}
.PARAM d = {1+2}
.PARAM d = {(1+2)}
.PARAM d = {(1+2) + 3}
.PARAM d = {(1+2) * 3}
.PARAM d = {(1+2) * (3 + 7)}
.PARAM d = {(1+2) * -(3 + 7)}
.PARAM d = {(1+a) * -(b + 7)}
.PARAM d = {(1+sin(3.14)) * -(3 + 7)}
.PARAM d = {(1+v(a)) * -(3 + 7)}
.PARAM d = {atan2(asin(b), ln(c))}
.PARAM d = {atan2(asin(b) - 7, ln(c) + 5)}
.PARAM d = {ddx(asin, ln(c) + 5)}
.PARAM d = {if(True, 1, 2)}
.PARAM d = {if(2 < 3, 1, 2)}
.PARAM d = {if((2 < 3) | False , 1, 2)}
.PARAM d = {(2 < 3) | False ? True ? 3: 4: 2}
.PARAM d = {(2 < 3) | False ? True ? 3: sin(4): 2}
.PARAM d = {(2 < 3) | False ? (True ? 3: sin(4)): 2}
.PARAM d = {(2 < 3) & ( False | True) ? (True ? 3: sin(4)): 2}
.PARAM d = {~(2 < 3) & ~( False | True) ? (True ? 3: sin(4)): 2}
.PARAM d = {limit(3, 2, a)}
.PARAM d = {limit(3, 2, a)}
E_ABM12         N145529 0 VALUE={ if((V(CTRL_LIMIT)<0.3) ,1,0)    }

Q1 col base eb QPWR 0.1

.MODEL QPWR NPN

*Another note
Q2 10 2 9 PNP1

Q8 Coll Base Emit VBIC13MODEL3 temp=0
Q9 Coll Base Emit [Subst] DT VBIC13MODEL4
Q10 Coll Base Emit [Subst] DT HICUMMMODEL1

.MODEL NPN2 NPN
.MODEL VBIC13MODEL2 NPN
.MODEL LAXPNP PNP
.MODEL PNP1 PNP

Q12 14 2 0 1 NPN2 2.0
Q6 VC 4 11 [SUB] LAXPNP
Q7 Coll Base Emit DT VBIC13MODEL2


M1 42 43 17 17 NOUT L=3U W=700U

.MODEL NOUT NMOS

BG3 IOUT- IOUT+ I={IF( (V(VC+,VC-) <= 0) , 0 , 1 )}
BG55 IOUT- IOUT+ I={IF( (V(VC+,VC-)<=0),0,GAIN*V(VC+,VC-) )}

.SUBCKT VCCS_LIM_CLAW+_0_OPA350  VCp VCm IOUTp IOUTm
BG4 IOUTp IOUTm I={TABLE {V(VCp,VCm)} =
+(0, 12.09e-6)
+(26.6667, 0.0002474)
+(53.3333, 0.00029078)
+(71.1111, 0.0003197)
+(72, 0.00032115)
+(73.7778, 0.00032404)
+(75.5556, 0.00032693)
+(77.3333, 0.00032982)
+(79.1111, 0.00033272)
+(80, 0.00275)}
.ENDS


.PARAM GAIN = 1E-3
Sw 14 2 12 11 SMOD

.MODEL SMOD SWITCH
.MODEL JFAST PJF
.MODEL JNOM NJF

JIN 100 1 0 JFAST
J13 22 14 23
+ JNOM 2.0 ; check

.lib models.lib nom

J1 1 2 0 2N5114

.MODEL 2n5114 NJF

* Library file res.lib
.lib low
.param rval=2
r3  2  0  9
.endl low

* Library file res.lib
.lib high
.param rval=2
r3  2  0  9
.Model		ZXTN619MA	NPN	;	## Description ##	## Effect ##
                            ;	## DC Forward Parameters ##
+		IS =	5.8032E-13	;	transport saturation current

.SUBCKT PLRD IN1 IN2 IN3 OUT1
+ PARAMS: MNTYMXDELY=0 IO_LEVEL=1
*
.ENDS

.endl

.LIB 'models.lib'  low
.LIB "models.lib"  low
.LIB "path/models.lib"  high

.lib nom
.param rval=3
r3  2  0  8
.endl nom

.PARAM KG ={1e-4/(2-VTH1)**2} ; rnom/(VON-VTH1)^2

.SUBCKT FILTER1 INPUT OUTPUT PARAMS: CENTER=200kHz,
+ BANDWIDTH=20kHz
*
.ENDS

XFELT 1 2 FILTER1 PARAMS: CENTER=200kHz

.MODEL Rmod1 RES (TC1=6e-3 )


.SUBCKT MYGND 25 28 7 MYPWR
.ENDS

.SUBCKT UNITAMP 1 2
.ENDS


X12 100 101 200 201 DIFFAMP
XBUFF 13 15 UNITAMP
XFOLLOW IN OUT VCC VEE OUT OPAMP
XNANDI 25 28 7 MYPWR MYGND PARAMS: IO_LEVEL=2

.SUBCKT OPAMP 10 12 111 112 13
*
.ENDS

.SUBCKT diffamp 1 2 3 4
.ENDS


B4 5 0 V={Table {V(5)}=(0,0) (1.0,2.0) (2.0,3.0) (3.0,10.0)}

B1 2 0 V={sqrt(V(1))}
B2 4 0 V={V(1)*TIME}
B3 4 2 I={I(V1) + V(4,2)/100}
B5 6 0 V=tablefile("file.dat")
B6 7 0 I=tablefile("file.dat")
Bcomplicated 1 0 V={TABLE {V(5)-V(3)/4+I(V6)*Res1} = (0, 0) (1, 2) (2, 4) (3, 6)}

.data check r3 r4 5 6 9 23 .enddata

.SUBCKT FILTER1 INPUT OUTPUT PARAMS: CENTER=200kHz,
+ BANDWIDTH=20kHz
XFOLLOW IN OUT VCC VEE OUT OPAMP

.SUBCKT OPAMP 10 12 111 112 13
*
.ENDS
*
.ENDS

.SUBCKT 74LS01 A B Y
+ PARAMS: MNTYMXDELY=0 IO_LEVEL=1
*
.ENDS

IPWL1 1 0 PWL 0S 0A 2S 3A 3S 2A 4S 2A 4.01S 5A r=2s td=1
IPWL2 2 0 PWL FILE "unit-test/SpiceParser/ipwl.txt"
VPWL3 3 0 PWL file "unit-test/SpiceParser/vpwl.csv"
VPWL4 4 0 PWL FILE unit-test/SpiceParser/vpwl.csv

ISLOW 1 22 SIN(0.5 1.0ma 1KHz 1ms)
IPULSE 1 3 PULSE(-1 1 2ns 2ns 2ns 50ns 100ns)
IPAT 2 4 PAT(5 0 0 1n 2n 5n b0101 1)
IPAT2 2 4 PAT(5 0 0 1n 2n 5n b0101)

M5 4 12 3 0 PNOM L=20u W=10u
M3 5 13 10 0 PSTRONG
M6 7 13 10 0 PSTRONG M=2 IC=1, 3 , 2
M8 10 12 100 100 NWEAK L=30u W=20u
+ AD=288p AS=288p PD=60u PS=60u NRD=14 NRS=24

.MODEL PNOM PMOS
.MODEL NWEAK NMOS
.MODEL PSTRONG PMOS

L1 1 5 3.718e-08
LM 7 8 L=5e-3 M=2
LLOAD 3 6 4.540mH IC=2mA
Lmodded 3 6 indmod 4.540mH
.model indmod L (L=.5 TC1=0.010 TC2=0.0094)


.MODEL VBIC13MODEL3 NPN
.MODEL VBIC13MODEL4 PNP
.MODEL HICUMMMODEL1 NPN


.MODEL sw Switch
*Pending adding the nonlinear element
*S3 1 2 SW OFF CONTROL={if(time>0.001,1,0)}

*.MODEL swi Switch
*.MODEL swv Switch

*S1 1 2 SWI OFF CONTROL={I(VMON)}
*SW2 1 2 SWV OFF CONTROL={V(3)-V(4)}

RM 4 5 R=4e3 M=2

r1 2 1 {r1 * rand( ;
+ )} TEMP=27
r2 2 1 {r2} ; check
r3 2 1 {r3}
r4 0 1 {r4}

vin 1 0 10
Vcntrl1 cathode 0 .23mV
Vcintrl2 anode cathode 5
Vsense 4 0 7mil
V5 3 0 0.

EBUFFER 1 2 10 11 5.0
ESQROOT 5 0 VALUE = {5V*SQRT(V(3,2))}
ET2 2 0 TABLE {V(ANODE,CATHODE)} = (0,0) (30,1)
EP1 5 1 POLY(2) 3 0 4 0 0 .5 .5

r13 13 0 1

r15 100 101 23k ; f load

r16 100 0 2

RLOAD 3 6 RTCMOD 4.540 TEMP=85

.MODEL RTCMOD R (TC1=.01 TC2=-.001)
*Pending managing this model
*RSEMICOND 2 0 RMOD L=1000u W=1u
*.MODEL RMOD R (RSH=1)

.model switch d

CM12 2 4 5.288e-13
CLOAD 1 0 4.540pF IC=1.5V
CFEEDBACK 2 0 CMOD 1.0pF
*Pending managing this model.
*CAGED 2 3 4.0uF D=0.0233 AGE=86200
CSOLDEP 3 0 C={ca*(c0+c1*tanh((V(3,0)-v0)/v1))}
*Pending managing this model.
*CSOLDEPQ 3 0 Q={ca*(c1*v1*ln(cosh((v(3,0)-v0)/v1))+c0*v(3,0))}

.MODEL CMOD CAP

FSENSE 1 2 VSENSE 10.0
FAMP 13 0 POLY(1) VIN 0 500
FNONLIN 100 101 POLY(2) VCNTRL1 VCINTRL2 0.0 13.6 0.2 0.005

.model dmod d

DCLAMP 1 0 DMOD

D2 13 100 SWITCH 1.5

GBUFFER 1 2 10 11 5.0
GPSK 11 6 VALUE = {5MA*SIN(6.28*10kHz*TIME+V(3))}
GA2 2 0 TABLE {V(5)} = (0,0) (1,5) (10,5) (11,0)

.param r1 = 1 r2= 2 r3 =3 r4 = {4mil}

HSENSE 1 2 VSENSE 10.0
HAMP 13 0 POLY(1) VIN 0 500
HNONLIN 100 101 POLY(2) VCNTRL1 VCINTRL2 0.0 13.6 0.2 0.005

.data check r3 r4 5 6 .enddata
.data recheck r3 r4 5 6 ;recheck
.enddata

.ac LIN 1 3 5
.ac DEC 4 3 7
.ac data=check
.data test
+ r1 r2
+ 8 4mil
+ 9 4.000J
+ 0.5 0+3.0J
+ .6+.7J 4.3e6
*For test purposes
.enddata

.dc LIN VCNTRL1 0 10 1
.dc VCINTRL2 0 10 2
+ r1 3 10 1
.dc r1 LIST 9 10 2
.dc DEC r3 1 3 9
.dc LIN r1 3. 4 5
+ DEC r2 7 8 9
.IC V(1) = 1
.DCVOLT V(1) = {2 * 5
+                > 3 ? abs  ;
+ ( ;another
+ sin(12) ; change of line
+ + 18) : atan2((45 - 3), 43)}
.IC 1 {
+ r1
+ } 2 3

*.EMBEDDEDSAMPLING
*+ param=R1
*+ type=NORMAL
*+ means=3k
*+ std_deviations = 1k

.end
"""

path = Path(__file__).parent

with open(path.joinpath('hsop77.cir')) as fh:
    hsop77 = fh.read()

with open(path.joinpath('hsada4077.cir')) as fh:
    hsada4077 = fh.read()

####################################################################################################

def circuit_gft(prb):
    parser = SpiceParser.parse(source=prb[0])
    circuit = parser.build()
    circuit.parameter('prb', str(prb[1]))
    # Fixme: simulate with Xyce, CI !!!
    simulator = circuit.simulator(simulator='xyce-serial')
    simulator.save('all')
    return simulator

####################################################################################################

class TestSpiceParser(unittest.TestCase):
    @staticmethod
    def _getdir(pathname):
        import os
        curdir = os.path.abspath(os.curdir)
        if curdir.endswith(pathname):
            return curdir
        else:
            return os.path.abspath('unit-test/SpiceParser')

    ##############################################

    #@unittest.skip('')
    def test_parser(self):
        # SpiceParser._regenerate()
        results = list(map(circuit_gft, [(data, -1), (data, 1)]))
        self.assertEqual(len(results), 2)
        values = str(results[0])
        self.assertNotRegex(values, r'(\.ic)')
        circuit_gft(values)
        self.assertNotRegex(values, r'([Nn][Oo][Nn][Ee])')

    def test_libraryRaw(self):
        from PySpice.Spice.Library import SpiceLibrary
        spice_library = SpiceLibrary()
        spice_library.insert("""
.subckt test1 1 2 3
xt 1 2 3 check
.ends

.subckt check 5 6 7
.ends
""")
        circuit_source = """.title Lib test
Xtest 1 2 3 test1
.end
"""
        circuit = SpiceParser.parse(source=circuit_source, library=spice_library)
        expected = """.title Lib test

.subckt check 5 6 7

.ends check

.subckt test1 1 2 3
xt 1 2 3 check
.ends test1

xtest 1 2 3 test1
"""
        result = str(circuit.build())
        self.assertEqual(expected, result)

    def test_library(self):
        from PySpice.Spice.Library import SpiceLibrary
        libraries_path = self._getdir('unit-test/SpiceParser')
        spice_library = SpiceLibrary(libraries_path)
        circuit = Circuit('MOS Driver')
        circuit.include(spice_library)
        x_mos = circuit.X('driver',
                          'mosdriver',
                          'hb',
                          'hi',
                          'ho',
                          'hs',
                          'li',
                          'lo',
                          'vdd',
                          'vss')
        circuit.R('hb', 'hb', 0, 1e12)
        circuit.R('hi', 'hi', 0, 1e12)
        circuit.R('ho', 'ho', 0, 1e12)
        circuit.R('hs', 'hs', 0, 1e12)
        circuit.R('li', 'li', 0, 1e12)
        circuit.R('lo', 'lo', 0, 1e12)
        circuit.R('test_temp', 'vss', 0, 10, tc=(4, 5))
        circuit.B('test_tc', 'vdd', 0, v=5, tc=(7, 8))
        simulator = circuit.simulator(simulator='xyce-serial',
                                      temperature=25,
                                      nominal_temperature=25,
                                      working_directory='.')
        simulator.options('device smoothbsrc=1')
        if shutil.which('xyce'):
            simulator.transient(1e-9, 1e-3)

    def test_library_direct(self):
        from PySpice.Spice.Library import SpiceLibrary

        library = SpiceLibrary()
        library.insert("""
* ADA4077 SPICE DMod model Typical values
* Description: Amplifier
* Generic Desc: 30V, BIP, OP, Low Noise, Low THD, 2X
* Developed by: RM ADSJ
* Revision History: 1.0 03/31/2015 - Updated to new header style
* 0.0 (11/2012)
* Copyright 2008, 2012,2015 by Analog Devices
*
* Refer to "README.DOC" file for License Statement.  Use of this
* model indicates your acceptance of the terms and provisions in
* the License Statement.
*
* Node Assignments
*		        noninverting input
*	            	|	inverting input
*		        |	|	positive supply
*		        |	|	|	negative supply
*		        |	|	|	|	output
*		        |	|	|	|	|
*		        |	|	|	|	|
.SUBCKT ADA4077 1	2	99	50	45
*
*INPUT STAGE
**4input sacled poly
Q1   15 7 60 NIX
Q2   6 2 61 NIX
IOS  1 2 1.75E-10
I1  5 50 77e-6
EOS  7  1 POLY(4) (14,98) (73,98) (81,98) (70,98)  10E-6 1 1 1 1
RC1  11 15 2.6E4
RC2  11 6 2.6E4
RE1 60 5 0.896E2
RE2 61 5 0.896E2
C1   15 6 4.25E-13
D1  50 9 DX
V1  5  9 DC 1.8
D10 99 10 DX
V6 10 11 1.3
*
* CMRR
*
ECM   13 98 POLY(2) (1,98) (2,98) 0 7.192E-4 7.192E-4
RCM1  13 14 2.15E2
RCM2  14 98 5.31E-3
CCM1  13 14 1E-6
*
* PSRR
*
EPSY 72 98 POLY(1) (99,50) -1.683 0.056
CPS3 72 73 1E-6
RPS3 72 73 7.9577E+1
RPS4 73 98 6.5915E-4
*
* EXTRA POLE AND ZERO
*
G1 21 98 (6,15) 26E-6
R1 21 98 9.8E4
R2 21 22 9E6
C2 22 98 1.7614E-12
D3 21 99 DX
D4 50 21 DX
*
* VOLTAGE NOISE
*
VN1 80 98 0
RN1 80 98 16.45E-3
HN  81 98 VN1 6
RN2 81 98 1
*
* FLICKER NOISE
*
D5 69 98 DNOISE
VSN 69 98 DC .60551
H1 70 98 VSN 30.85
RN 70 98 1
*
* INTERNAL VOLTAGE REFERENCE
*
EREF 98  0 POLY(2) (99,0) (50,0) 0 .5 .5
GSY  99 50 POLY(1) (99,50) 130E-6 1.7495E-10
*
* GAIN STAGE
*
G2  98 25 (21,98) 1E-6
R5  25 98 9.9E7
CF  45 25 2.69E-12
V4 25 33 5.3
D7 51 33 DX
EVN 51 98 (50,99) 0.5
V3 32 25 5.3
D6 32 97 DX
EVP 97 98 (99,50) 0.5
*
* OUTPUT STAGE
*
Q3   45 41 99 POUT
Q4   45 43 50 NOUT
RB1  40 41 9.25E-4
RB2  42 43 9.25E-4
EB1  99 40 POLY(1) (98,25) 0.7153  1
EB2  42 50 POLY(1) (25,98) 0.7153  1
*
* MODELS
*
.MODEL NIX NPN (BF=71429,IS=1E-16)
.MODEL POUT PNP (BF=200,VAF=50,BR=70,IS=1E-15,RC=71.25)
.MODEL NOUT NPN (BF=200,VAF=50,BR=22,IS=1E-15,RC=29.2)
.MODEL DX D(IS=1E-16, RS=5, KF=1E-15)
.MODEL DNOISE D(IS=1E-16,RS=0,KF=1.095E-14)
.ENDS ADA4077
*$

.MODEL DI_1N5819 D  ( IS=390n RS=0.115 BV=40.0 IBV=1.00m
+ CJO=203p  M=0.333 N=1.70 TT=4.32u )
""")
        self.assertEqual(len(list(library.subcircuits)), 1)
        self.assertEqual(len(list(library.models)), 1)

        netlist = SpiceParser.parse(source="""
XU5A np nn ncc nss nsee ADA4077
Dup no ncc DI_1N5819
Ddown 0 no DI_1N5819
""", library=library)
        circuit = netlist.build()

    def test_library_str(self):
        from PySpice.Spice.Library import SpiceLibrary
        libraries_path = self._getdir('unit-test/SpiceParser')
        spice_library = SpiceLibrary()
        spice_library.insert("""
.subckt mosdriver hb hi ho hs li lo vdd vss

.subckt source vh vl hi lo
vhl vh vl 1
vhilo hi lo 2
.ends

xhigh hb vss hi vss source
xlow ho vss hs vss source
rloi li lo 1

.model diode d

.ENDS mosdriver
""")
        circuit = Circuit('MOS Driver')
        circuit.include(spice_library)
        circuit.X('driver',
                  'mosdriver',
                  'hb',
                  'hi',
                  'ho',
                  'hs',
                  'li',
                  'lo',
                  'vdd',
                  'vss')
        circuit.R('hb', 'hb', 0, 1e12)
        circuit.R('hi', 'hi', 0, 1e12)
        circuit.R('ho', 'ho', 0, 1e12)
        circuit.R('hs', 'hs', 0, 1e12)
        circuit.R('li', 'li', 0, 1e12)
        circuit.R('lo', 'lo', 0, 1e12)
        circuit.R('test_temp', 'vss', 0, 10, tc=(4, 5))
        circuit.B('test_tc', 'vdd', 0, v=5, tc=(7, 8))
        simulator = circuit.simulator(simulator='xyce-serial',
                                      temperature=25,
                                      nominal_temperature=25,
                                      working_directory='.')
        simulator.options('device smoothbsrc=1')
        if shutil.which('xyce'):
            simulator.transient(1e-25, 1e-20)

    def test_working_dir(self):
        from PySpice.Spice.Xyce.RawFile import RawFile
        circuit = Circuit('Test working directory')
        circuit.PulseVoltageSource('hlp',
                                   1,
                                   0,
                                   initial_value=0,
                                   pulse_value=1,
                                   delay_time=0,
                                   rise_time=0.1,
                                   fall_time=0.1,
                                   pulse_width=1,
                                   period=2)
        circuit.Resistor('load', 1, 0, 1e3)
        simulator = circuit.simulator(simulator='xyce-serial',
                                      temperature=25,
                                      nominal_temperature=25)
        simulator.options('device smoothbsrc=1')
        if shutil.which('xyce'):
            result = simulator.transient(1e-2, 10)
        simulator = circuit.simulator(simulator='xyce-serial',
                                      temperature=25,
                                      nominal_temperature=25,
                                      working_directory='.')
        simulator.options('device smoothbsrc=1')
        if shutil.which('xyce'):
            result = simulator.transient(1e-2, 10)
            self.assertTrue(os.path.exists('input.cir') and os.path.isfile('input.cir'))
            self.assertTrue(os.path.exists('output.raw') and os.path.isfile('output.raw'))
            data = RawFile(filename="output.raw")
            print(data.nodes())

    def test_transient(self):
        transient = SpiceParser.parse(source="""
VEXP 2 0 EXP(1 2 3)
VPAT 3 4 PAT(3 0 2 1 2 3 b0101 1)
IPULSE 2 3 PULSE(1 4)
IPWL1 1 0 PWL(0S 0A 2S 3A 3S 2A 4S 2A 4.01S 5A r=2s td=1)
VSFFM 1 0 SFFM (0 1 2)
ISIN 4 3 AC 1 SIN 0 5 3 1
""")
        circuit = transient.build()

        expected = """.title

vexp 2 0 exp(1v 2v 3s)
vpat 3 4 pat(3v 0v 2s 1s 2s 3s b0101 1)
ipulse 2 3 pulse(1a 4a 0s 0s 0s)
ipwl1 1 0 pwl(0s 0a 2s 3a 3s 2a 4s 2a 4.01s 5a r=2s td=1s)
vsffm 1 0 sffm(0v 1v 2hz)
isin 4 3 dc 0a ac 1a sin(0a 5a 3hz 1s 0hz)
"""
        result = str(circuit)
        self.assertEqual(expected, result)

    def test_subcircuits(self):
        subckt = SpiceParser.parse(source="""

.param a = 23
.param b = 24

.subckt test1 1 2 3
.ends

Xtest1 4 5 6 test1

.subckt test2 1 3 4 params: t=3
.ends

Xtest21 8 7 3 test2
Xtest22 9 5 6 test2 params: t = 5

.subckt test3 2 3
.param h = 25
.ends

Xtest3 9 10 test3

.subckt test4 5 6 params: j = {a+b}
.param d = {j + 32}
.ends

Xtest41 10 12 test4
Xtest42 12 10 test4 params: j = 23
""")
        circuit = subckt.build()
        print(circuit)
        expected = """.title

.param a=23
.param b=24
.subckt test1 1 2 3

.ends test1

.subckt test2 1 3 4 params: t=3

.ends test2

.subckt test3 2 3
.param h=25

.ends test3

.subckt test4 5 6 params: j={a + b}
.param d={j + 32}

.ends test4

xtest1 4 5 6 test1
xtest21 8 7 3 test2
xtest22 9 5 6 test2 params: t=5
xtest3 9 10 test3
xtest41 10 12 test4
xtest42 12 10 test4 params: j=23
"""
        result = str(circuit)
        self.assertEqual(expected, result)

    def test_sources(self):
        sources = SpiceParser.parse(source="""
Iinj 0 probe 0 AC {0.5*prb*(prb+1)}
Vinj probe Ninplp 0 AC {0.5*prb*(prb-1)}
Vprobe probe Noutlp 0

""")
        circuit = sources.build()
        expected = """.title

iinj 0 probe dc 0a ac {0.5 * (prb * (prb + 1))}
vinj probe ninplp dc 0v ac {0.5 * (prb * (prb - 1))}
vprobe probe noutlp dc 0v
"""
        result = str(circuit)
        self.assertEqual(expected, result)
    def test_boolean(self):
        and2 = SpiceParser.parse(source = """
BEAND YINT 0 V = {IF(V(A) > 0.5 & V(B) > 0.5, 1, 0)}
BEOR YINT 0 V = {IF(V(A) > 0.5 | V(B) > 0.5, 1, 0)}
BEXOR YINT 0 V = {IF(V(A) > 0.5 ^ V(B) > 0.5, 1, 0)}
""")
        circuit = and2.build()
        expected = """.title

beand yint 0 v={if((v(a) > 0.5) & (v(b) > 0.5), 1, 0)}
beor yint 0 v={if((v(a) > 0.5) | (v(b) > 0.5), 1, 0)}
bexor yint 0 v={if((v(a) > 0.5) ^ (v(b) > 0.5), 1, 0)}
"""
        result = str(circuit)
        self.assertEqual(expected, result)

    def test_subcircuit(self):
        print(os.getcwd())
        circuit = Circuit('MOS Driver\nSimple check')
        circuit.spice_sim = 'xyce'
        circuit.include(self._getdir('unit-test/SpiceParser') + '/mosdriver.lib')
        circuit.X('test', 'mosdriver', '0', '1', '2', '3', '4', '5', '6', '7')
        circuit.BehavioralSource('test', '1', '0', voltage_expression='{if(True, 0, 1)}', smoothbsrc=1)
        expected = """.title MOS Driver
* Simple check

.model diode D (is=1.038e-15 n=1 tt=2e-08 cjo=5e-12 rs=0.5 bv=130)
.subckt source vh vl hi lo
bhigh vh vl v={if(v(hi, lo) > 0.5, 5, 0)} smoothbsrc=1
.ends source

.subckt mosdriver hb hi ho hs li lo vdd vss
xhigh hoi hs hi vss source
rhoi hoi ho 1ohm
choi ho hs 1e-09
xlow loi vss li vss source
rloi loi lo 1ohm
cloi lo vss 1e-09
dhb vdd hb diode
.ends mosdriver

xtest 0 1 2 3 4 5 6 7 mosdriver
btest 1 0 v={if(true, 0, 1)} smoothbsrc=1
"""
        result = str(circuit)
        self.assertEqual(expected, result)

    def test_title(self):
        title = """.title Howland Current Source
"""
        sources = SpiceParser.parse(source=title)
        circuit = sources.build()
        result = str(circuit)
        self.assertEqual(title + os.linesep + os.linesep, result)

    def test_model(self):
        models = """
.MODEL NOUT NPN (BF=200,VAF=50,BR=22,IS=1E-15,RC=29.2)
.MODEL DX D(IS=1E-16, RS=5, KF=1E-15)
Q1 1 2 3 NOUT
D2 1 2 DX
"""

        expected = """.title

.model nout NPN (bf=200 vaf=50 br=22 is=1e-15 rc=29.2)
.model dx D (is=1e-16 rs=5 kf=1e-15)
q1 1 2 3 nout
d2 1 2 dx
"""

        model = SpiceParser.parse(source=models)
        circuit = model.build()
        result = str(circuit)
        self.assertEqual(expected, result)

    def test_source(self):
        source = """
HN  81 98 VN1 6
Vp5 Np5 0 5
Vm5 Nm5 0 -5
"""

        expected = """.title

bhn 81 98 v={i(vn1) * 6}
vp5 np5 0 dc 5v
vm5 nm5 0 dc -5v
"""

        model = SpiceParser.parse(source=source)
        circuit = model.build()
        result = str(circuit)
        self.assertEqual(expected, result)

    def test_pulsed_source(self):
        source = """
vpulsed1 1 0 pulse(0v {high} 1s 0.1s 0.1s 5s 10s)
"""

        expected = """.title

vpulsed1 1 0 pulse(0v {high} 1s 0.1s 0.1s 5s 10s)
"""

        model = SpiceParser.parse(source=source)
        circuit = model.build()
        result = str(circuit)
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
