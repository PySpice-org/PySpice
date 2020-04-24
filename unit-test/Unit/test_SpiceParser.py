import unittest
from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Parser import SpiceParser
from multiprocessing import Pool, cpu_count
import os

hsop77 = """
.title HSOP77case

* OP77 SPICE Macro-model
* Description: Amplifier
* Generic Desc: 6/30V, BIP, OP, Low Vos, Precision, 1X
* Developed by: JCB / PMI
* Revision History: 08/10/2012 - Updated to new header style
* 2.0 (12/1990) - Re-ordered subcircuit call out nodes to put the output node last.
*          - Changed Ios from 0.3E-9 to 0.15E-9
*      - Added F1 and F2 to fix short circuit current limit.
* Copyright 1990, 2012 by Analog Devices, Inc.
*
* Refer to http://www.analog.com/Analog_Root/static/techSupport/designTools/spiceModels/license/spice_general.html for License Statement. Use of this model
* indicates your acceptance with the terms and provisions in the License Statement.
*
* BEGIN Notes:
*
* Not Modeled:
*
* Parameters modeled include:
*
* END Notes
*
* Node assignments
*              non-inverting input
*              | inverting input
*              | | positive supply
*              | | |  negative supply
*              | | |  |  output
*              | | |  |  |
.SUBCKT OP77   1 2 99 50 39
*#ASSOC Category="Op-amps" symbol=opamp
*
* INPUT STAGE & POLE AT 6 MHZ
*
R1   2   3    5E11
R2   1   3    5E11
R3   5  97    0.0606
R4   6  97    0.0606
CIN  1   2    4E-12
C2   5   6    218.9E-9
I1   4  51    1
IOS  1   2    0.15E-9
EOS  9  10    POLY(1)  30 33  10E-6  1
Q1   5  2  7  QX
Q2   6  9  8  QX
R5   7   4    0.009
R6   8   4    0.009
D1   2   1    DX
D2   1   2    DX
EN   10  1    12  0  1
GN1  0   2    15  0  1
GN2  0   1    18  0  1
*
EREF  98 0    33  0  1
EPLUS 97 0    99  0  1
ENEG  51 0    50  0  1
*
* VOLTAGE NOISE SOURCE WITH FLICKER NOISE
*
DN1  11  12   DEN
DN2  12  13   DEN
VN1  11   0   DC 2
VN2  0   13   DC 2
*
* CURRENT NOISE SOURCE WITH FLICKER NOISE
*
DN3  14  15   DIN
DN4  15  16   DIN
VN3  14   0   DC 2
VN4  0   16   DC 2
*
* SECOND CURRENT NOISE SOURCE
*
DN5  17  18   DIN
DN6  18  19   DIN
VN5  17   0   DC 2
VN6  0   19   DC 2
*
* FIRST GAIN STAGE
*
R7   20 98     1
G1   98 20     5  6  59.91
D3   20 21     DX
D4   22 20     DX
E1   97 21     POLY(1) 97 33 -2.4 1
E2   22 51     POLY(1) 33 51 -2.4 1
*
* GAIN STAGE & DOMINANT POLE AT 0.053 HZ
*
R8   23 98     6.01E9
C3   23 98     500E-12
G2   98 23     20 33  33.3E-6
V1   97 24     1.3
V2   25 51     1.3
D5   23 24     DX
D6   25 23     DX
*
* NEGATIVE ZERO AT -4MHZ
*
R9   26 27     1
C4   26 27     -39.75E-9
R10  27 98     1E-6
E3   26 98     23 33  1E6
*
* COMMON-MODE GAIN NETWORK WITH ZERO AT 20 HZ
*
R13  30 31     1
L2   31 98     7.96E-3
G4   98 30     3  33  1.0E-7
D7   30 97     DX
D8   51 30     DX
*
* POLE AT 2 MHZ
*
R14  32 98     1
C5   32 98     79.5E-9
G5   98 32     27 33  1
*
* OUTPUT STAGE
*
R15  33 97     1
R16  33 51     1
GSY  99 50     POLY(1) 99 50 0.325E-3 0.0425E-3
F1   34  0     V3  1
F2   0  34     V4  1
R17  34 99     400
R18  34 50     400
L3   34 39     2E-7
G6   37 50     32 34  2.5E-3
G7   38 50     34 32  2.5E-3
G8   34 99     99 32  2.5E-3
G9   50 34     32 50  2.5E-3
V3   35 34     6.8
V4   34 36     4.4
D9   32 35     DX
D10  36 32     DX
D11  99 37     DX
D12  99 38     DX
D13  50 37     DY
D14  50 38     DY
*
* MODELS USED
*
.MODEL QX NPN(BF=417E6)
.MODEL DX   D(IS=1E-15)
.MODEL DY   D(IS=1E-15 BV=50)
.MODEL DEN  D(IS=1E-12, RS=12.08K, KF=1E-17, AF=1)
.MODEL DIN  D(IS=1E-12, RS=7.55E-6, KF=1.55E-15, AF=1)
.ENDS OP77

Iinj 0 probe 0 AC {0.5*prb*(prb+1)}
Vinj probe Ninplp 0 AC {0.5*prb*(prb-1)}
Vprobe probe Noutlp 0

.model 2N2222 NPN(IS=1E-14 VAF=100
+   BF=200 IKF=0.3 XTB=1.5 BR=3
+   CJC=8E-12 CJE=25E-12 TR=100E-9 TF=400E-12
+   ITF=1 VTF=2 XTF=3 RB=10 RC=.3 RE=.2)

XU1 Ninp Ninn Np15 Nm15 Ninplp OP77
XU2 No Nre Np15 Nm15 Nrep OP77
R1 Ninnm 0 {r_1}
R2 Ne Ninnm {r_2}
C2 Ne Ninnm {c_2}
VU1offset Ninn Ninnm {v_1offset}
R3 Nin Ninp {r_3}
VU2offset Nre Nrep {v_2offset}
R4 Nrep Ninp {r_4}
C4 Nrep Ninp {c_4}
R5 Ne No {r_o}
Vi Nin 0 {vin} AC {1-prb*prb}
V2p15 Np15 0 15
Vm15 Nm15 0 -15
Q1 Nc Nb Ne 2N2222
R6 Np15 Nc 50
R7 Noutlp Nb 10
D1 Ngl No YELLOW
Vl Ngl 0 0
.model YELLOW D(IS=93.1P RS=42M N=4.61 BV=2 IBV=10U
+ CJO=2.97P VJ=.75 M=.333 TT=4.32U)

.model NPN NPN
.model PNP PNP
.param prb=0
.param vin=2.5
.param r_1=1k
.param r_2=1k
.param r_3=1k
.param r_4=1k
.param r_o=200
.param c_2=20p
.param c_4=20p
.param v_1offset=0
.param v_2offset=0

.end
"""

hsada4077 = """
.title ADA4077-2case

* ADA4077-2 SPICE DMod model Typical values
* Description: Amplifier
* Generic Desc: 30V, BIP, OP, Low Noise, Low THD, 2X
* Developed by: RM ADSJ
* Revision History: 02/11/2012 - Updated to new header style
* 0.0 (11/2012)
* Copyright 2008, 2012 by Analog Devices
*
* Refer to "README.DOC" file for License Statement.  Use of this
* model indicates your acceptance of the terms and provisions in
* the License Statement.
*
* Node Assignments
*              noninverting input
*                  |   inverting input
*              |   |   positive supply
*              |   |   |   negative supply
*              |   |   |   |   output
*              |   |   |   |   |
*              |   |   |   |   |
.SUBCKT ADA4077-2   1   2   99   50   45
*#ASSOC Category="Op-amps" symbol=opamp
*
*INPUT STAGE
*
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
RB1  40 41 9.25E4
RB2  42 43 9.25E4
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
.ENDS ADA4077-2
*$

Iinj 0 probe 0 AC {0.5*prb*(prb+1)}
Vinj probe Ninplp 0 AC {0.5*prb*(prb-1)}
Vprobe probe Noutlp 0

.model 2N2222 NPN(IS=1E-14 VAF=100
+   BF=200 IKF=0.3 XTB=1.5 BR=3
+   CJC=8E-12 CJE=25E-12 TR=100E-9 TF=400E-12
+   ITF=1 VTF=2 XTF=3 RB=10 RC=.3 RE=.2)

XU1 Ninp Ninn Np15 Nm15 Ninplp ADA4077-2
XU2 No Nre Np15 Nm15 Nrep ADA4077-2
R1 Ninnm 0 {r_1}
R2 Ne Ninnm {r_2}
C2 Ne Ninnm {c_2}
VU1offset Ninn Ninnm {v_1offset}
R3 Nin Ninp {r_3}
VU2offset Nre Nrep {v_2offset}
R4 Nrep Ninp {r_4}
C4 Nrep Ninp {c_4}
R5 Ne No {r_o}
Vi Nin 0 {vin} AC {1-prb*prb}
V2p15 Np15 0 15
Vm15 Nm15 0 -15
Q1 Nc Nb Ne 2N2222
R6 Np15 Nc 50
R7 Noutlp Nb 10
D1 Ngl No YELLOW
Vl Ngl 0 0
.model YELLOW D(IS=93.1P RS=42M N=4.61 BV=2 IBV=10U
+ CJO=2.97P VJ=.75 M=.333 TT=4.32U)

.model NPN NPN
.model PNP PNP
.param prb=0
.param vin=2.5
.param r_1=1k
.param r_2=1k
.param r_3=1k
.param r_4=1k
.param r_o=200
.param c_2=20p
.param c_4=20p
.param v_1offset=0
.param v_2offset=0

.end
"""

def circuit_gft(prb):
    circuit_file = SpiceParser(source=prb[0])
    circuit = circuit_file.build_circuit()
    circuit.parameter('prb', str(prb[1]))
    simulator = circuit.simulator(simulator='xyce-serial')
    simulator.save(['all'])
    return simulator

class TestSpiceParser(unittest.TestCase):
    def test_parser(self):
        for source in (hsop77, hsada4077):
            results = list(map(circuit_gft, [(source, -1), (source, 1)]))
            self.assertEqual(len(results), 2)
            values = str(results[0])
            self.assertNotRegex(values, r'(\.ic)')

    def test_subcircuit(self):
        print(os.getcwd())
        circuit = Circuit('Diode Characteristic Curve')
        circuit.include(os.path.join(os.getcwd(), 'mosdriver.lib'))
        circuit.X('test', 'mosdriver', '0', '1', '2', '3', '4', '5')
        circuit.BehavioralSource('test', '1', '0', voltage_expression='if(0, 0, 1)', smoothbsrc=1)
        print(circuit)
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
