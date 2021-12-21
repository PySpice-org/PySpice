####################################################################################################
#
# Examples extracted from  ngspice-manuals-git/build_html/manual.html
#
####################################################################################################

"""Ngspice Examples

Conventions string identifier is of the form [sEF]sha_digest

* s  means not classified
* E  means example
* SE means skipped example
* F  means general form

Skipped line are prefixed by :code:`*s* `.

Usage::

    for cls in ManualExamples.Examples.subclasses():
        for key, value in cls.iter_on_examples(label='E'):
            ...

"""

####################################################################################################

from typing import Iterator, Generator

class Examples:

    _subclasses = []

    ##############################################

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._subclasses.append(cls)

    ##############################################

    @classmethod
    def subclasses(cls):   # -> Iterator[Examples]:
        return iter(cls._subclasses)

    ##############################################

    @classmethod
    def iter_on_examples(cls, label: str=None) -> Generator[tuple[str, str], None, None]:
        if label is None:
            # Fixme:
            for key, value in cls.__dict__.items():
                yield key, value
        else:
            for key, value in cls.__dict__.items():
                if key.startswith(label):
                    yield key, value

####################################################################################################
#
# Ngspice User's Manual
#
# Version 35 plus
#

####################################################################################################
#
# Chapter 2 Circuit Description
#

class CircuitDescription(Examples):

############################################################
#
# 2.3 Basic lines
#

##################################################
# @2961

    SE83cc = """
POWER AMPLIFIER CIRCUIT
* additional lines following
*...

Test of CAM cell
* additional lines following
*...
"""

##################################################
# @2978

    E8c35 = """
******************************
* additional lines following
*...
.TITLE Test of CAM cell
* additional lines following
*...
"""

##################################################
# @2992

    SEc9bf = """
Test of CAM cell
* additional lines following
*...
*TITLE Test of CAM cell
* additional lines following
*...
"""

##################################################
# @3005

    E019e = """
.end
"""

##################################################
# @3014

    F0598 = """
* <any comment>
"""

##################################################
# @3019

    Ef965 = """
* RF=1K Gain should be 100
* Check open-loop gain and phase margin
"""

##################################################
# @3029

    F17fd = """
<any command> $ <any comment>
<any command> ; <any comment>
"""

##################################################
# @3035

# Fixme: valid syntax ???

    SE4a14 = """
RF2=1K $ Gain should be 100
C1=10p ; Check open-loop gain and phase margin
.param n1=1 //new value
"""

##################################################
# @3046

    Fed75 = """
<any command>
+ <continuation of any command> ; some comment
+ <further continuation of any command>
"""

############################################################
#
# 2.4
# .MODEL Device Models
#

##################################################
# @3056

    F6e5c = """
.model mname type(pname1=pval1 pname2=pval2 ... )
"""

##################################################
# @3061

    E6b43 = """
.model MOD1 npn (bf=50 is=1e-13 vbf=50)
"""

############################################################
#
# 2.5
# .SUBCKT Subcircuits
#

##################################################
# @3200

    Ee7e0 = """
* The following is the instance card:
*
xdiv1 10 7 0 vdivide

* The following are the subcircuit definition cards:
*
.subckt vdivide 1 2 3
r1 1 2 10K
r2 2 3 5K
.ends
"""

##################################################
# @3225

    Fa42c = """
.SUBCKT subnam N1 <N2 N3 ...>
"""

##################################################
# @3230

    E8ea2 = """
.SUBCKT OPAMP 1 2 3 4
"""

##################################################
# @3240

    Fd3bb = """
.ENDS <SUBNAM>
"""

##################################################
# @3245

    E7556 = """
.ENDS OPAMP
"""

##################################################
# @3255

    F5c09 = """
XYYYYYYY N1 <N2 N3 ...> SUBNAM
"""

##################################################
# @3260

    E75ce = """
X1 2 4 17 3 1 MULTI
"""

############################################################
#
# 2.6
# .GLOBAL
#

##################################################
# @3270

    F3b88 = """
.GLOBAL nodename
"""

##################################################
# @3275

    E77a6 = """
.GLOBAL gnd vcc
"""

############################################################
#
# 2.7
# .INCLUDE
#

##################################################
# @3285

    F272e = """
.INCLUDE filename
"""

##################################################
# @3290

    Edcfc = """
.INCLUDE /users/spice/common/bsim3-param.mod
"""

############################################################
#
# 2.8
# .LIB
#

##################################################
# @3302

    F3c28 = """
.LIB filename libname
"""

##################################################
# @3307

    E470f = """
.LIB /users/spice/common/mosfets.lib mos1
"""

############################################################
#
# 2.9
# .PARAM Parametric netlists
#

##################################################
# @3322

    F71e6 = """
.param <ident> = <expr>  <ident> = <expr> ...
"""

##################################################
# @3327

    E6389 = """
.param pippo=5
.param po=6 pp=7.8 pap={AGAUSS(pippo, 1, 1.67)}
.param pippp={pippo + pp}
.param p={pp}
.param pop='pp+p'
"""

##################################################
# @3343

    E2d29 = """
* .param a = 123 * 3    b = sqrt(9) $ doesn't work, a <= 123
.param a = '123 * 3'  b = sqrt(9) $ ok.
* .param c = a + 123   $ won't work
.param c = 'a + 123' $ ok.
.param c = a+123     $ ok.
"""

##################################################
# @3354

    F1ed5 = """
{ <expr> }
"""

##################################################
# @3365

    F97f2 = """
.subckt <identn> node node ...  <ident>=<value> <ident>=<value> ...
"""

##################################################
# @3370

    E8c7a = """
.subckt myfilter in out rval=100k cval=100nF
"""

##################################################
# @3381

    Fadb7 = """
X<name> node node ... <identn> <ident>=<value> <ident>=<value> ...
"""

##################################################
# @3386

    Ebbae = """
X1 input output myfilter rval=1k cval=1n
"""

##################################################
# @3397

    Eea1f = """
* Param-example
.param amplitude= 1V
*
.subckt myfilter in out rval=100k  cval=100nF
Ra in p1   {2*rval}
Rb p1 out  {2*rval}
C1 p1 0    {2*cval}
Ca in p2   {cval}
Cb p2 out  {cval}
R1 p2 0    {rval}
.ends myfilter
*
X1 input output myfilter rval=1k cval=1n
V1 input 0 AC {amplitude}
.end
"""

##################################################
# @3424

    F7e03 = """
<atom> where <atom> is either a spice number or an identifier
<unary-operator> <atom>
<function-name> ( <expr> [ , <expr> ...] )
<atom> <binary-operator> <expr>
( <expr> )
"""

##################################################
# @3673

    Ea8f3 = """
* Logical operators

v1or   1 0  {1 || 0}
v1and  2 0  {1 && 0}
v1not  3 0  {! 1}
v1mod  4 0  {5 % 3}
v1div  5 0  {5 \ 3}
v0not  6 0  {! 0}

.control
op
print allv
.endc

.end
"""

############################################################
#
# 2.10
# .FUNC
#

##################################################
# @3927

    Fb185 = """
.func <ident> { <expr> }
.func <ident> = { <expr> }
"""

##################################################
# @3933

    E1ebd = """
.func icos(x) {cos(x) - 1}
.func f(x,y) {x*y}
.func foo(a,b) = {a + b}
"""

############################################################
#
# 2.11
# .CSPARAM
#

##################################################
# @3947

    F1efb = """
.csparam <ident> = <expr>
"""

##################################################
# @3952

    E8751 = """
.param pippo=5
.param pp=6
.csparam pippp={pippo + pp}
.param p={pp}
.csparam pap='pp+p'
"""

############################################################
#
# 2.12
# .TEMP
#

##################################################
# @3980

    F18a6 = """
.temp value
"""

##################################################
# @3985

    Edfe8 = """
.temp 27
"""

############################################################
#
# 2.13
# .IF Condition-Controlled Netlist
#

##################################################
# @3997

    Ff6a7 = """
.if(boolean expression)
...
.elseif(boolean expression)
...
.else
...
.endif
"""

##################################################
# @4008

    E4079 = """
* device instance in IF-ELSE block
.param ok=0 ok2=1

v1 1 0 1
R1 1 0 2

.if (ok && ok2)
R11 1 0 2
.else
R11 1 0 0.5   $ <-- selected
.endif
"""

##################################################
# @4023

    Ed7ae = """
* .model in IF-ELSE block
.param m0=0 m1=1

M1 1 2 3 4 N1 W=1 L=0.5

.if(m0==1)
.model N1 NMOS level=49 Version=3.1
.elseif(m1==1)
.model N1 NMOS level=49 Version=3.2.4  $ <-- selected
.else
.model N1 NMOS level=49 Version=3.3.0
.endif
"""

############################################################
#
# 2.14
# Parameters, functions, expressions, and command scripts
#

####################################################################################################
#
# Chapter 3
# Circuit Elements and Models
#

class CircuitElementsModels(Examples):

############################################################
#
# 3.1 About netlists, device instances, models and model parameters
#

##################################################
# @4062

    E4e35 = """
bipolar amplifier

R3 vcc intc 10k
R1 vcc intb 68k
R2 intb 0 10k
Cout out intc 10u
Cin intb in 10u
RLoad out 0 100k
Q1 intc intb 0 BC546B

VCC vcc 0 5
Vin in 0 dc 0 ac 1 sin(0 1m 500)

.model BC546B npn ( IS=7.59E-15 VAF=73.4 BF=480 IKF=0.0962 NE=1.2665
+ ISE=3.278E-15 IKR=0.03 ISC=2.00E-13 NC=1.2 NR=1 BR=5 RC=0.25 CJC=6.33E-12
+ FC=0.5 MJC=0.33 VJC=0.65 CJE=1.25E-11 MJE=0.55 VJE=0.65 TF=4.26E-10
+ ITF=0.6 VTF=3 XTF=20 RB=100 IRB=0.0001 RBM=10 RE=0.5 TR=1.50E-07)
.end
"""

##################################################
# @4092

    E3dbd = """
Q1 intc intb 0 defaultmod
.model defaultmod npn
"""

############################################################
#
# 3.2 General options
#

##################################################
# @4107

    Edb1a = """
d1 2 0 mydiode m=10
d01 1 0 mydiode
d02 1 0 mydiode
d03 1 0 mydiode
d04 1 0 mydiode
d05 1 0 mydiode
d06 1 0 mydiode
d07 1 0 mydiode
d08 1 0 mydiode
d09 1 0 mydiode
d10 1 0 mydiode
"""

##################################################
# @4220

    Ee7af = """
.param madd = 6
X1 a b sub1 m=5
.subckt sub1 a1 b1
   Cs1 a1 b1 C=5p m='madd-2'
.ends
"""

##################################################
# @4233

    Effc1 = """
.param madd = 4
X1 a b sub1 m=3
.subckt sub1 a1 b1
   X2 a1 b1 sub2 m='madd-2'
.ends
.subckt sub2 a2 b2
   Cs2 a2 b2 3p m=2
.ends
"""

##################################################
# @4262

    E4053 = """
Lload 1 2 1u ind1 dtemp=5
.MODEL ind1 L tc1=0.001
"""

############################################################
#
# 3.3 Elementary Devices
#

##################################################
# @4282

    F0cf6 = """
RXXXXXXX n+ n- <resistance|r=>value <ac=val> <m=val>
+ <scale=val> <temp=val> <dtemp=val> <tc1=val> <tc2=val>
+ <noisy=0|1>
"""

##################################################
# @4289

    E790a = """
R1 1 2 100
RC1 12 17 1K
R2 5 7 1K ac=2K
RL 1 4 2K m=2
"""

##################################################
# @4411

    E6d03 = """
RE1 1 2 800 newres dtemp=5
.MODEL newres R tc1=0.001

RE2 a b 1.4k tc1=2m tc2=1.4u

RE3 n1 n2 1Meg tce=700m
"""

##################################################
# @4493

    Ead3f = """
Rmd 134 57 1.5k noisy=0
"""

##################################################
# @4502

    F2296 = """
RXXXXXXX n+ n- <value> <mname> <l=length> <w=width>
+ <temp=val> <dtemp=val> <m=val> <ac=val> <scale=val>
+ <noisy = 0|1>
"""

##################################################
# @4509

    E87f7 = """
RLOAD 2 10 10K
RMOD 3 7 RMODEL L=10u W=1u
"""

##################################################
# @5175

    F03b8 = """
RXXXXXXX n+ n- R = 'expression' <tc1=value> <tc2=value> <noisy=0>
RXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value> <noisy=0>
"""

##################################################
# @5181

    E4667 = """
R1 rr 0 r = 'V(rr) < {Vt} ? {R0} : {2*R0}' tc1=2e-03 tc2=3.3e-06
R2 r2 rr r = {5k + 50*TEMPER}
.param rp1 = 20
R3 no1 no2 r = '5k * rp1' noisy=1
"""

##################################################
# @5193

    Ef40e = """
Non-linear resistor
.param R0=1k Vi=1 Vt=0.5
* resistor depending on control voltage V(rr)
R1 rr 0 r = 'V(rr) < {Vt} ? {R0} : {2*R0}'
* control voltage
V1 rr 0 PWL(0 0 100u {Vi})
.control
unset askquit
tran 100n 100u uic
plot i(V1)
.endc
.end
"""

##################################################
# @5215

    Ee863 = """
r2_cmc
v1 1 0 10
Rr2_cmc 1 0 rmodel w=1u l=20u isnoisy=1
.model rmodel r(level=2 rsh=200 xl=0.2u xw=-0.05u
+ p3=0.12 q3=1.6 p2=0.015 q2=3.8 tc1=1.5e-4 tc2=7e-7)
.control
op
let res = v(1) / -v1#branch
*s* print res .endc
 print res
.endc
.end
"""

##################################################
# @5232

    F6eac = """
CXXXXXXX n+ n- <value> <mname> <m=val> <scale=val> <temp=val>
+ <dtemp=val> <tc1=val> <tc2=val> <ic=init_condition>
"""

##################################################
# @5238

    E28a9 = """
CBYP 13 0 1UF
COSC 17 23 10U IC=3V
"""

##################################################
# @5251

    Edc09 = """
C1 15 5 cstd
C2 2 7 cstd
.model cstd C cap=3n
"""

##################################################
# @5262

    E32ff = """
CEB 1 2 1u cap1 dtemp=5
.MODEL cap1 C tc1=0.001
"""

##################################################
# @5316

    F1b10 = """
CXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <m=val>
+ <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
"""

##################################################
# @5322

    Ede19 = """
CLOAD 2 10 10P
CMOD 3 7 CMODEL L=10u W=1u
"""

##################################################
# @6057

    F433b = """
CXXXXXXX n+ n- C = 'expression' <tc1=value> <tc2=value>
CXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>

CXXXXXXX n+ n- Q = 'expression' <tc1=value> <tc2=value>
"""

##################################################
# @6065

    E2a61 = """
C1 cc 0 c = 'V(cc) < {Vt} ? {C1} : {Ch}' tc1=-1e-03 tc2=1.3e-05
C1 a b q = '1u*(4*atan(V(a,b)/4)*2+V(a,b))/3'
"""

##################################################
# @6075

    Eb125 = """
*s* Behavioral Capacitor
.param Cl=5n Ch=1n Vt=1m Il=100n
.ic v(cc) = 0    v(cc2) = 0
* capacitor depending on control voltage V(cc)
C1 cc 0 c = 'V(cc) < {Vt} ? {Cl} : {Ch}'
I1 0 1 {Il}
Exxx  n1-copy n2  n2 cc2  1
Cxxx  n1-copy n2  1
Bxxx  cc2 n2  I = '(V(cc2) < {Vt} ? {Cl} : {Ch})' * i(Exxx)
I2 n2 22 {Il}
vn2 n2 0 DC 0
* measure charge by integrating current
aint1 %id(1 cc) 2 time_count
aint2 %id(22 cc2) 3 time_count
.model time_count int(in_offset=0.0 gain=1.0
+ out_lower_limit=-1e12 out_upper_limit=1e12
+ limit_range=1e-9 out_ic=0.0)
.control
unset askquit
tran 100n 100u
plot v(2)
plot v(cc) v(cc2)
.endc
.end
"""

##################################################
# @6106

    F8d8e = """
LYYYYYYY n+ n- <value> <mname> <nt=val> <m=val>
+ <scale=val> <temp=val> <dtemp=val> <tc1=val>
+ <tc2=val> <ic=init_condition>
"""

##################################################
# @6113

    E3e69 = """
LLINK 42 69 1UH
LSHUNT 23 51 10U IC=15.7MA
"""

##################################################
# @6122

    E70fb = """
L1 15 5 indmod1
L2 2 7 indmod1
.model indmod1 L ind=3n
"""

##################################################
# @6733

    F2e95 = """
KXXXXXXX LYYYYYYY LZZZZZZZ value
"""

##################################################
# @6738

    E20b9 = """
K43 LAA LBB 0.999
KXFRMR L1 L2 0.87
"""

##################################################
# @6748

    E8552 = """
L1 1 0  10u
L2 2 0  11u
L3 3 0  10u

K12 L1 L2 0.99
K23 L2 L3 0.99
K13 L1 L3 0.98
"""

##################################################
# @6764

    Fe5c2 = """
LXXXXXXX n+ n- L = 'expression' <tc1=value> <tc2=value>
LXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
"""

##################################################
# @6770

    E3b18 = """
L1 l2 lll L = 'i(Vm) < {It} ? {Ll} : {Lh}' tc1=-4e-03 tc2=6e-05
"""

##################################################
# @6779

    Ee7c = """
Variable inductor
.param Ll=0.5m Lh=5m It=50u Vi=2m
.ic v(int21) = 0

* variable inductor depending on control current i(Vm)
L1 l2 lll L = 'i(Vm) < {It} ? {Ll} : {Lh}'
* measure current through inductor
vm lll 0 dc 0
* voltage on inductor
V1 l2 0 {Vi}

* fixed inductor
L3 33 331 {Ll}
* measure current through inductor
vm33 331 0 dc 0
* voltage on inductor
V3 33 0 {Vi}

* non linear inductor (discrete setup)
F21 int21 0 B21 -1
L21 int21 0 1
B21 n1 n2 V = '(i(Vm21) < {It} ? {Ll} : {Lh})' * v(int21)
* measure current through inductor
vm21 n2 0 dc 0
V21 n1 0 {Vi}

.control
unset askquit
tran 1u 100u uic
plot i(Vm) i(vm33)
plot i(vm21) i(vm33)
plot i(vm)-i(vm21)
.endc
.end
"""

##################################################
# @6851

    Fd5cd = """
SXXXXXXX N+ N- NC+ NC- MODEL <ON><OFF>
WYYYYYYY N+ N- VNAM MODEL <ON><OFF>
"""

##################################################
# @6857

    Ed310 = """
s1 1 2 3 4 switch1 ON
s2 5 6 3 0 sm2 off
Switch1 1 2 10 0 smodel1
w1 1 2 vclock switchmod1
W2 3 0 vramp sm1 ON
wreset 5 6 vclck lossyswitch OFF
"""

##################################################
# @7010

    Ea0e2 = """
Switch test
.tran 2us 5ms
*switch control voltage
v1 1 0 DC 0.0 PWL(0 0 2e-3 2 4e-3 0)
*switch control voltage starting inside hysteresis window
*please note influence of instance parameters ON, OFF
v2 2 0 DC 0.0 PWL(0 0.9 2e-3 2 4e-3 0.4)
*switch control current
i3 3 0 DC 0.0 PWL(0 0 2e-3 2m 4e-3 0) $ <--- switch control current
*load voltage
v4 4 0 DC 2.0
*input load for current source i3
r3 3 33 10k
vm3 33 0 dc 0 $ <--- measure the current
* ouput load resistors
r10 4 10 10k
r20 4 20 10k
r30 4 30 10k
r40 4 40 10k
*
s1 10 0 1 0 switch1 OFF
s2 20 0 2 0 switch1 OFF
s3 30 0 2 0 switch1 ON
.model switch1 sw vt=1 vh=0.2 ron=1 roff=10k
*
w1 40 0 vm3 wswitch1 off
.model wswitch1 csw  it=1m ih=0.2m ron=1 roff=10k
*
.control
run
plot v(1) v(10)
plot v(10) vs v(1) $ <-- get hysteresis loop
plot v(2) v(20) $ <--- different initial values
plot v(20) vs v(2) $ <-- get hysteresis loop
plot v(2) v(30) $ <--- different initial values
plot v(30) vs v(2) $ <-- get hysteresis loop
plot v(40) vs vm3#branch $ <--- current controlled switch hysteresis
.endc
.end
"""

####################################################################################################
#
# Chapter 4 Voltage and Current Sources
#

class VoltageCurrentSources(Examples):

############################################################
#
# 4.1
# Independent Sources for Voltage or Current
#

##################################################
# @7058

    F6b78 = """
VXXXXXXX N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>>
+ <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>
IYYYYYYY N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>>
+ <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>
"""

##################################################
# @7066

    E75bb = """
VCC 10 0 DC 6
VIN 13 2 0.001 AC 1 SIN(0 1 1MEG)
ISRC 23 21 AC 0.333 45.0 SFFM(0 1 10K 5 1K)
VMEAS 12 9
VCARRIER 1 0 DISTOF1 0.1 -90.0
VMODULATOR 2 0 DISTOF2 0.01
IIN1 1 5 AC 1 DISTOF1 DISTOF2 0.001
"""

##################################################
# @7101

    F4888 = """
PULSE(V1 V2 TD TR TF PW PER PHASE)
"""

##################################################
# @7106

    E4957 = """
VIN 3 0 PULSE(-1 1 2NS 2NS 2NS 50NS 100NS)
"""

##################################################
# @7287

    SEe4d9 = """
SIN(VO VA FREQ TD THETA PHASE)
"""

##################################################
# @7292

    SEd097 = """
VIN 3 0 SIN(0 1 100MEG 1NS 1E10)
"""

##################################################
# @7493

    Febd4 = """
EXP(V1 V2 TD1 TAU1 TD2 TAU2)
"""

##################################################
# @7498

    Ede66 = """
VIN 3 0 EXP(-4 -1 2NS 30NS 60NS 40NS)
"""

##################################################
# @7750

    F8edf = """
PWL(T1 V1 <T2 V2 T3 V3 T4 V4 ...>) <r=value> <td=value>
"""

##################################################
# @7755

    E7786 = """
VCLOCK 7 5 PWL(0 -7 10NS -7 11NS -3 17NS -3 18NS -7 50NS -7)
+ r=0 td=15NS
"""

##################################################
# @7813

    F6e26 = """
SFFM(VO VA FC MDI FS PHASEC PHASES)
"""

##################################################
# @7818

    E30b1 = """
V1 12 0 SFFM(0 1M 20K 5 1K)
"""

##################################################
# @8002

    Fa650 = """
AM(VA VO MF FC TD PHASES)
"""

##################################################
# @8007

    E01b6 = """
V1 12 0 AM(0.5 1 20K 5MEG 1m)
"""

##################################################
# @8171

    Fca74 = """
TRNOISE(NA NT NALPHA NAMP RTSAM RTSCAPT RTSEMT)
"""

##################################################
# @8176

    E9eb9 = """
VNoiw 1 0 DC 0 TRNOISE(20n 0.5n 0 0)      $ white
VNoi1of 1 0 DC 0 TRNOISE(0 10p 1.1 12p)   $ 1/f
VNoiw1of 1 0 DC 0 TRNOISE(20 10p 1.1 12p) $ white and 1/f
IALL 10 0 DC 0 trnoise(1m 1u 1.0 0.1m 15m 22u 50u)
                                          $ white, 1/f, RTS
"""

##################################################
# @8342

    F1471 = """
TRRANDOM(TYPE TS <TD <PARAM1 <PARAM2>>>)
"""

##################################################
# @8347

    E35de = """
VR1 r1  0 dc 0 trrandom (2 10m 0 1) $ Gaussian
"""

##################################################
# @8480

    F92f6 = """
EXTERNAL
"""

##################################################
# @8485

    Ee7f4 = """
Vex 1  0 dc 0 external
*s* Iex i1 i2 dc 0 external <m = xx>
"""

############################################################
#
# 4.2
# Linear Dependent Sources
#

##################################################
# @8555

    Ff168 = """
GXXXXXXX N+ N- NC+ NC- VALUE <m=val>
"""

##################################################
# @8560

    Ed956 = """
G1 2 0 5 0 0.1
"""

##################################################
# @8572

    F32ad = """
EXXXXXXX N+ N- NC+ NC- VALUE
"""

##################################################
# @8577

    E968b = """
E1 2 3 14 1 2.0
"""

##################################################
# @8587

    F60fd = """
FXXXXXXX N+ N- VNAM VALUE <m=val>
"""

##################################################
# @8592

    E8363 = """
F1 13 5 VSENS 5 m=2
"""

##################################################
# @8602

    F20d7 = """
HXXXXXXX N+ N- VNAM VALUE
"""

##################################################
# @8607

    E6ff6 = """
HX 5 17 VZ 0.5K
"""

####################################################################################################
#
# Chapter 5
# Non-linear Dependent Sources (Behavioral Sources)
#

class BehavioralSources(Examples):

############################################################
#
# 5.1
# Bxxxx: Nonlinear dependent source (ASRC)
#

##################################################
# @8669

    Fe6fc = """
BXXXXXXX n+ n- <i=expr> <v=expr> <tc1=value> <tc2=value>
+ <temp=value> <dtemp=value>
"""

##################################################
# @8675

    E909a = """
B1 0 1 I=cos(v(1))+sin(v(2))
B2 0 1 V=ln(cos(log(v(1,2)^2)))-v(3)^4+v(2)^v(1)
B3 3 4 I=17
B4 3 4 V=exp(pi^i(vdd))
B5 2 0 V = V(1) < {Vlow} ? {Vlow} :
+  V(1) > {Vhigh} ? {Vhigh} : V(1)
"""

##################################################
# @8873

    Ed5ad = """
* B source test Clamped voltage source
* C. P. Basso "Switched-mode power supplies", New York, 2008
.param Vhigh = 4.6
.param Vlow = 0.4
Vin1 1 0 DC 0 PWL(0 0 1u 5)
Bcl 2 0 V = V(1) < Vlow ? Vlow : V(1) > Vhigh ? Vhigh : V(1)
.control
unset askquit
tran  5n 1u
plot V(2) vs V(1)
.endc
.end
"""

##################################################
# @8899

    E4a6e = """
.Subckt nlcap pos neg
* Bx: calculate f(input voltage)
Bx 1 0 v = f(v(pos,neg))
* Cx: linear capacitance
Cx 2 0 1
* Vx: Ammeter to measure current into the capacitor
Vx 2 1 DC 0Volts
* Drive the current through Cx back into the circuit
Fx pos neg Vx 1
.ends
"""

##################################################
# @8915

    E4423 = """
Bx 1 0 V = v(pos,neg)*v(pos,neg)
"""

##################################################
# @8924

    Effbd = """
* use of 'hertz' variable in nonlinear resistor
*.param rbase=1k
* some tests
B1  1 0  V = hertz*v(33)
B2  2 0 V = v(33)*hertz
b3  3 0 V = 6.283e3/(hertz+6.283e3)*v(33)
V1 33 0 DC 0 AC 1
*** Translate R1 10 0 R='1k/sqrt(HERTZ)' to B source ***
.Subckt nlres pos neg rb=rbase
* Bx: calculate f(input voltage)
Bx   1    0    v = -1 / {rb} / sqrt(HERTZ) * v(pos, neg)
* Rx: linear resistance
Rx   2    0    1
"""

##################################################
# @8943

    Ed788 = """
* Vx: Ammeter to measure current into the resistor
Vx   2    1    DC 0Volts
* Drive the current through Rx back into the circuit
Fx   pos  neg  Vx 1
.ends
Xres 33 10 nlres rb=1k
*Rres 33 10 1k
Vres 10 0 DC 0
.control
*s* define check(a,b) vecmax(abs(a - b))
*s* ac lin 10 100 1k
*s* * some checks
*s* print v(1) v(2) v(3)
*s* if check(v(1), frequency) < 1e-12
*s* echo "INFO: ok"
*s* end
*s* plot vres#branch
.endc
.end
"""

##################################################
# @8976

    E0301 = """
Bdio 1 0 I = pwl(v(A), 0,0, 33,10m, 100,33m, 200,50m)
"""

##################################################
# @8987

    E6eb4 = """
Blimit b 0 V = pwl(v(1), -4,0, -2,2, 2,4, 4,5, 6,5)
"""

##################################################
# @9011

    E9f21 = """
Demonstrates usage of the pwl function in an B source (ASRC)
* Also emulates the TABLE function with limits

.param x0=-4 y0=0
.param x1=-2 y1=2
.param x2=2 y2=-2
.param x3=4 y3=1
.param xx0=x0-1
.param xx3=x3+1

Vin   1 0   DC=0V
R 1 0 2

* no limits outside of the tabulated x values
* (continues linearily)
Btest2 2 0  I = pwl(v(1),'x0','y0','x1','y1','x2','y2','x3','y3')

* like TABLE function with limits:
Btest3 3 0   I = (v(1) < 'x0') ? 'y0' :  (v(1) < 'x3') ?
+ pwl(v(1),'x0','y0','x1','y1','x2','y2','x3','y3') : 'y3'

* more efficient and elegant TABLE function with limits
*(voltage controlled):
Btest4 4 0   I = pwl(v(1),
+ 'xx0','y0', 'x0','y0',
+             'x1','y1',
+             'x2','y2',
+             'x3','y3', 'xx3','y3')
*
* more efficient and elegant TABLE function with limits
* (controlled by current):
Btest5 5 0   I = pwl(-2*i(Vin),
+ 'xx0','y0', 'x0','y0',
+             'x1','y1',
+             'x2','y2',
+             'x3','y3', 'xx3','y3')

Rint2 2 0 1
Rint3 3 0 1
Rint4 4 0 1
Rint5 5 0 1
.control
dc  Vin  -6 6  0.2
plot v(2) v(3) v(4)-0.5 v(5)+0.5
.endc

.end
"""

############################################################
#
# 5.2
# Exxxx: non-linear voltage source
#

##################################################
# @9066

    F8990 = """
EXXXXXXX n+ n- vol='expr'
"""

##################################################
# @9071

    Ee22e = """
E41 4 0 vol = 'V(3)*V(3)-Offs'
"""

##################################################
# @9080

    F3f88 = """
EXXXXXXX n+ n- value={expr}
"""

##################################################
# @9085

    E89ea = """
E41 4 0 value = {V(3)*V(3)-Offs}
"""

##################################################
# @9097

    F2124 = """
Exxx n1 n2 TABLE {expression} = (x0, y0) (x1, y1) (x2, y2)
"""

##################################################
# @9102

    E27f0 = """
ECMP 11 0 TABLE {V(10,9)} = (-5mV, 0V) (5mV, 5V)
"""

##################################################
# @9116

    E6908 = """
ELOPASS 4 0 LAPLACE {V(1)}
+                   {5 * (s/100 + 1) / (s^2/42000 + s/60 + 1)}
"""

##################################################
# @9122

    E45fe = """
AELOPASS 1 int_4 filter1
.model filter1 s_xfer(gain=5
+                    num_coeff=[{1/100} 1]
+                    den_coeff=[{1/42000} {1/60} 1]
+                    int_ic=[0 0])
ELOPASS 4 0 int_4 0 1
"""

##################################################
# @9138

    Ebc8a = """
ELOPASS 4 0 LAPLACE {V(1)*v(2)} {10 / (s/6800 + 1)}
"""

##################################################
# @9143

    E1c06 = """
BELOPASS int_1 0 V=V(1)*v(2)
AELOPASS int_1 int_4 filter1
.model filter1 s_xfer(gain=10
+                    num_coeff=[1]
+                    den_coeff=[{1/6800} 1]
+                    int_ic=[0])
ELOPASS 4 0 int_4 0 1
"""

############################################################
#
# 5.3
# Gxxxx: non-linear current source
#

##################################################
# @9158

    F8d70 = """
GXXXXXXX n+ n- cur='expr' <m=val>
"""

##################################################
# @9163

    Ef0b7 = """
G51 55 225 cur = 'V(3)*V(3)-Offs'
"""

##################################################
# @9172

    F4f3b = """
GXXXXXXX n+ n- value='expr' <m=val>
"""

##################################################
# @9177

    E6a89 = """
G51 55 225 value = 'V(3)*V(3)-Offs'
"""

##################################################
# @9188

    Ff0a9 = """
Gxxx n1 n2 TABLE  {expression} =
+  (x0, y0) (x1, y1) (x2, y2) <m=val>
"""

##################################################
# @9194

    E3dbe = """
GCMP 0 11 TABLE {V(10,9)} = (-5MV, 0V) (5MV, 5V)
R 11 0 1k
"""

##################################################
# @9210

    E5122 = """
*s* VCCS, VCVS, non-linear dependency
.param Vi=1
.param Offs='0.01*Vi'
* VCCS depending on V(3)
B21 int1 0 V = V(3)*V(3)
G1 21 22 int1 0 1
* measure current through VCCS
vm 22 0 dc 0
R21 21 0 1
* new VCCS depending on V(3)
G51 55 225 cur = 'V(3)*V(3)-Offs'
* measure current through VCCS
vm5 225 0 dc 0
R51 55 0 1
* VCVS depending on V(3)
B31 int2 0 V = V(3)*V(3)
E1 1 0 int2 0 1
R1 1 0 1
* new VCVS depending on V(3)
E41 4 0 vol = 'V(3)*V(3)-Offs'
R4 4 0 1
* control voltage
V1 3 0 PWL(0 0 100u {Vi})
.control
unset askquit
tran 10n 100u uic
plot i(E1) i(E41)
plot i(vm) i(vm5)
.endc
.end
"""

############################################################
#
# 5.4
# Debugging a behavioral source
#

##################################################
# @9249

    Ee8e6 = """
B source debugging

V1 1 0 1
V2 2 0 -2

E41 4 0 vol = 'V(1)*log(V(2))'

.control
tran 1 1
.endc

.end
"""

############################################################
#
# 5.5
# POLY Sources
#

##################################################
# @9294

    Faaaa = """
EXXXX N+ N- POLY(ND) NC1+ NC1- (NC2+ NC2-...) P0 (P1...)
"""

##################################################
# @9299

    E44d6 = """
ENONLIN 100 101 POLY(2) 3 0 4 0 0.0 13.6 0.2 0.005
"""

##################################################
# @9331

    F824d = """
FXXXX N+ N- POLY(ND) V1 (V2 V3 ...) P0 (P1...)
"""

##################################################
# @9336

    Eb131 = """
FNONLIN 100 101 POLY(2) VDD Vxx 0 0.0 13.6 0.2 0.005
"""

####################################################################################################
#
# Chapter 6 Transmission Lines
#

class TransmissionLines(Examples):

############################################################
#
# 6.1
# Lossless Transmission Lines
#

##################################################
# @9354

    Fd5b3 = """
TXXXXXXX N1 N2 N3 N4 Z0=VALUE <TD=VALUE>
+  <F=FREQ <NL=NRMLEN>> <IC=V1, I1, V2, I2>
"""

##################################################
# @9360

    Ea1d7 = """
T1 1 0 2 0 Z0=50 TD=10NS
"""

############################################################
#
# 6.2
# Lossy Transmission Lines
#

##################################################
# @9374

    Fbe3a = """
OXXXXXXX n1 n2 n3 n4 mname
"""

##################################################
# @9379

    E6516 = """
O23 1 0 2 0 LOSSYMOD
OCONNECT 10 5 20 5 INTERCONNECT
"""

############################################################
#
# 6.3
# Uniform Distributed RC Lines
#

##################################################
# @9702

    Fb5ff = """
UXXXXXXX n1 n2 n3 mname l=len <n=lumps>
"""

##################################################
# @9707

    E32ed = """
U1 1 2 0 URCMOD L=50U
URC2 1 12 2 UMODL l=1MIL N=6
"""

############################################################
#
# 6.4 KSPICE Lossy Transmission Lines
#

##################################################
# @9976

    F6dba = """
YXXXXXXX N1 0 N2 0 mname <LEN=LENGTH>
"""

##################################################
# @9981

    E1d7f = """
Y1 1 0 2 0 ymod LEN=2
.MODEL ymod txl R=12.45 L=8.972e-9 G=0 C=0.468e-12 length=16
"""

##################################################
# @10156

    F25c5 = """
PXXXXXXX NI1 NI2...NIX GND1 NO1 NO2...NOX GND2 mname <LEN=LENGTH>
"""

##################################################
# @10161

    Ecad4 = """
P1 in1 in2 0 b1 b2 0 PLINE
.model PLINE CPL length={Len}
+R=1 0 1
+L={L11} {L12} {L22}
+G=0 0 0
+C={C11} {C12} {C22}
.param Len=1 Rs=0
+ C11=9.143579E-11 C12=-9.78265E-12 C22=9.143578E-11
+ L11=3.83572E-7 L12=8.26253E-8 L22=3.83572E-7
"""

####################################################################################################
#
# Chapter 7
# Diodes
#

class Diodes(Examples):

############################################################
#
# 7.1
# Junction Diodes
#

##################################################
# @10335

    F489d = """
DXXXXXXX n+ n- mname <area=val> <m=val> <pj=val> <off>
+   <ic=vd> <temp=val> <dtemp=val>
+   <lm=val> <wm=val> <lp=val> <wp=val>
"""

##################################################
# @10342

    Edcc7 = """
DBRIDGE 2 10 DIODE1
DCLMP 3 7 DMOD AREA=3.0 IC=0.2
"""

############################################################
#
# 7.2 Diode Model (D)
#

##################################################
# @10356

    Ea3c6 = """
.model DMOD D
"""

##################################################
# @11613

    Ec19e = """
.model DMOD D (bv=50 is=1e-13 n=1.05)
"""

############################################################
#
# 7.3 Diode Equations
#

##################################################
# @13941

    F47b = """
DXXXXXXX n+ n- tj mname <off> <ic=vd> thermal
"""

##################################################
# @13946

    E133d = """
.model DPWR D (bv=16 is=1e-10 n=1.03 rth0=50 cth0=1u)
"""

####################################################################################################
#
# Chapter 8
# BJT
#

class BJT(Examples):

############################################################
#
# 8.1 Bipolar Junction Transistors (BJTs)
#

##################################################
# @13955

    F7111 = """
QXXXXXXX nc nb ne <ns> <tj> mname <area=val> <areac=val>
+ <areab=val> <m=val> <off> <ic=vbe,vce> <temp=val>
+ <dtemp=val>
"""

##################################################
# @13962

    E8680 = """
Q23 10 24 13 QMOD IC=0.6, 5.0
Q50A 11 26 4 20 MOD1
"""

############################################################
#
# 8.2 BJT Models (NPN/PNP)
#

##################################################
# @16553

    E2986 = """
vc c 0 0
vb b 0 1
ve e 0 0
vs s 0 0
Q1 c b e s dt mod1 area=1
.model mod1 npn Level=4
"""

##################################################
# @16565

    Efbd1 = """
Q1 c b e s dt mod2
X1 dt tamb junction-ambient
VTamb tamb 0 30
.subckt junction-ambient jct amb
rjc jct 1 0.4
ccs 1 0 5m
rcs 1 2 0.1
csa 2 0 30m
rsa 2 amb 1.3
.ends
"""

##################################################
# @16619

    Efe0c = """
vc c 0 0
vb b 0 1
ve e 0 0
vs s 0 0
Q1 c b e s dt mod1 area=1
.model mod1 npn Level=8
"""

####################################################################################################
#
# Chapter 9
# JFETs
#

class JFETS(Examples):

############################################################
#
# 9.1 Junction Field-Effect Transistors (JFETs)
#

##################################################
# @16636

    F0d9b = """
JXXXXXXX nd ng ns mname <area> <off> <ic=vds,vgs> <temp=t>
"""

##################################################
# @16641

    Ec11a = """
J1 7 2 3 JM1 OFF
"""

############################################################
#
# 9.2 JFET Models (NJF/PJF)
#

####################################################################################################
#
# Chapter 10
# MESFETs
#

class MESFETS(Examples):

############################################################
#
# 10.1 MESFETs
#

##################################################
# @18335

    F9b18 = """
ZXXXXXXX ND NG NS MNAME <AREA> <OFF> <IC=VDS, VGS>
"""

##################################################
# @18340

    E0aa7 = """
Z1 7 2 3 ZM1 OFF
"""

############################################################
#
# 10.2 MESFET Models (NMF/PMF)
#

##################################################
# @18888

    E226d = """
z1 2 3 0 mesmod area=1.4
"""

##################################################
# @18893

    E6710 = """
.model mesmod nmf level=1 rd=46 rs=46 vt0=-1.3
+ lambda=0.03 alpha=3 beta=1.4e-3
"""

####################################################################################################
#
# Chapter 11
# MOSFETs
#

class MOSFETS(Examples):

############################################################
#
# 11.1
# MOSFET devices
#

##################################################
# @18923

    Fb50f = """
MXXXXXXX nd ng ns nb mname <m=val> <l=val> <w=val>
+ <ad=val> <as=val> <pd=val> <ps=val> <nrd=val>
+ <nrs=val> <off> <ic=vds, vgs, vbs> <temp=t>
"""

##################################################
# @18930

    E8616 = """
M1 24 2 0 20 TYPE1
M31 2 17 6 10 MOSN L=5U W=2U
M1 2 9 3 0 MOSP L=10U W=5U AD=100P AS=100P PD=40U PS=40U
"""

############################################################
#
# 11.2 MOSFET models (NMOS/PMOS)
#

############################################################
#
# 11.3 Power MOSFET model (VDMOS)
#

##################################################
# @21857

    F5006 = """
MXXXXXXX nd ng ns mname <m=val> <temp=t> <dtemp=t>
.model mname VDMOS <Pchan> <parameters>
"""

##################################################
# @21863

    E968c = """
M1 24 2 0 IXTH48P20P
.MODEL IXTH48P20P VDMOS Pchan Vds=200 VTO=-4 KP=10 Lambda=5m
+ Mtriode=0.3 Ksubthres=120m Rs=10m Rd=20m Rds=200e6
+ Cgdmax=6000p Cgdmin=100p A=0.25 Cgs=5000p Cjo=9000p
+ Is=2e-6 Rb=20m BV=200 IBV=250e-6 NBV=4 TT=260e-9
"""

##################################################
# @23265

    Fe1bc = """
MXXXXXXX nd ng ns tj tc mname thermal <m=val> <temp=t> <dtemp=t>
"""

##################################################
# @23270

    Ef271 = """
M1 24 2 0 tj tc IXTH48P20P thermal
rcs tc 1 0.1
csa 1 0 30m
rsa 1 amb 1.3
VTamb tamb 0 25
.MODEL IXTH48P20P VDMOS Pchan Vds=200 VTO=-4 KP=10 Lambda=5m
+ Mtriode=0.3 Ksubthres=120m Rs=10m Rd=20m Rds=200e6
+ Cgdmax=6000p Cgdmin=100p A=0.25 Cgs=5000p Cjo=9000p
+ Is=2e-6 Rb=20m BV=200 IBV=250e-6 NBV=4 TT=260e-9
+ Rthjc=0.4 Cthj=5e-3
"""

####################################################################################################
#
# Chapter 12
# Mixed-Mode and Behavioral Modeling with XSPICE
#

class XSPICE(Examples):

############################################################
#
# 12.1 Code Model Element & .MODEL Cards
#

##################################################
# @23296

    Ec0da = """
a1 1 2 amp
.model amp gain(gain=5.0)
"""

##################################################
# @23306

    Ec054 = """
a1 %v(1) %v(2) amp
.model amp gain(gain=5.0)
"""

##################################################
# @23318

    Ff2f9 = """
AXXXXXXX <%v,%i,%vd,%id,%g,%gd,%h,%hd, or %d>
+ <[> <~><%v,%i,%vd,%id,%g,%gd,%h,%hd, or %d>
+ <NIN1 or +NIN1 -NIN1 or "null">
+ <~>...<NIN2.. <]> >
+ <%v,%i,%vd,%id,%g,%gd,%h,%hd,%d or %vnam>
+ <[> <~><%v,%i,%vd,%id,%g,%gd,%h,%hd,
      or %d><NOUT1 or +NOUT1 -NOUT1>
+ <~>...<NOUT2.. <]>>
+ MODELNAME

.MODEL MODELNAME MODELTYPE
+ <( PARAMNAME1= <[> VAL1 <VAL2... <]>> PARAMNAME2..>)>
"""

##################################################
# @23341

    E811d = """
a1 [~1 2] 3 nand1
.model nand1 d_nand (rise_delay=0.1 fall_delay=0.2)
"""

############################################################
#
# 12.2
# Analog Models
#

##################################################
# @23554

    E7d7d = """
a1 1 2 amp
.model amp gain(in_offset=0.1 gain=5.0
+ out_offset=-0.01)
"""

##################################################
# @23605

    E2d67 = """
a2 [1 2] 3 sum1
.model sum1 summer(in_offset=[0.1 -0.2] in_gain=[2.0 1.0]
+ out_gain=5.0 out_offset=-0.01)
"""

##################################################
# @23658

    E508f = """
a3 [1 2 3] 4 sigmult
.model sigmult mult(in_offset=[0.1 0.1 -0.1]
+ in_gain=[10.0 10.0 10.0] out_gain=5.0 out_offset=0.05)
"""

############################################################
#
# 12.3
# Hybrid Models
#

############################################################
#
# 12.4
# Digital Models
#

############################################################
#
# 12.5 Predefined Node Types for event driven simulation
#

####################################################################################################
#
# Chapter 13 Verilog A Device models
#

class VerilogADeviceModel(Examples):
    pass

####################################################################################################
#
# Chapter 14 Mixed-Level Simulation (ngspice with TCAD)
#

class TCAD(Examples):
    pass

####################################################################################################
#
# Chapter 15
# Analyses and Output Control (batch mode)
#

class AnalysesOutputControl(Examples):

############################################################
#
# 15.1
# Simulator Variables (.options)
#

##################################################
# @28087

    F6860 = """
.options opt1 opt2 ... (or opt=optval ...)
"""

##################################################
# @28092

    Ee884 = """
.options reltol=.005 trtol=8
"""

############################################################
#
# 15.2 Initial Conditions
#

##################################################
# @28360

    F2b7c = """
.nodeset v(nodnum)=val v(nodnum)=val ...
.nodeset all=val
"""

##################################################
# @28366

    E5c57 = """
.nodeset v(12)=4.5 v(4)=2.23
.nodeset all=1.5
"""

##################################################
# @28377

    F5cff = """
.ic v(nodnum)=val v(nodnum)=val ...
"""

##################################################
# @28382

    E9959 = """
.ic v(11)=5 v(4)=-5 v(2)=2.2
"""

############################################################
#
# 15.3
# Analyses
#

##################################################
# @28398

    F77be = """
.ac dec nd fstart fstop
.ac oct no fstart fstop
.ac lin np fstart fstop
"""

##################################################
# @28405

    Edd8f = """
.ac dec 10 1 10K
.ac dec 10 1K 100MEG
.ac lin 100 1 100HZ
"""

##################################################
# @28416

    Edae = """
Basic RC circuit
r 1 2 1.0
c 2 0 1.0
vin 1 0 dc 0 ac 1  $ <--- the ac source
.options noacct
.ac dec 10 .01 10
.plot ac  vdb(2) xlog
.end
"""

##################################################
# @28445

    F637b = """
.dc srcnam vstart vstop vincr [src2 start2 stop2 incr2]
"""

##################################################
# @28451

    Ec432 = """
.dc VIN 0.25 5.0 0.25
.dc VDS 0 10 .5 VGS 0 5 1
.dc VCE 0 10 .25 IB 0 10u 1u
.dc RLoad 1k 2k 100
.dc TEMP -15 75 5
"""

##################################################
# @28475

    F0703 = """
.disto dec nd fstart fstop <f2overf1>
.disto oct no fstart fstop <f2overf1>
.disto lin np fstart fstop <f2overf1>
"""

##################################################
# @28482

    Efe69 = """
.disto dec 10 1kHz 100MEG
.disto dec 10 1kHz 100MEG 0.9
"""

##################################################
# @29000

    Fb3ee = """
.noise v(output <,ref>) src ( dec | lin | oct ) pts fstart fstop
+ <pts_per_summary>
"""

##################################################
# @29006

    E26b4 = """
.noise v(5) VIN dec 10 1kHz 100MEG
.noise v(5,3) V1 oct 8 1.0 1.0e6 1
"""

##################################################
# @29100

    Efcb5 = """
.op
"""

##################################################
# @29133

    F2b65 = """
optran !noopiter gminsteps srcsteps tstep tstop supramp
"""

##################################################
# @29138

    E7df8 = """
optran 0 0 0 100n 10u 0
"""

##################################################
# @29147

    E8173 = """
optran 1 1 1 100n 10u 0
"""

##################################################
# @29162

    F93d5 = """
.pz node1 node2 node3 node4 cur pol
.pz node1 node2 node3 node4 cur zer
.pz node1 node2 node3 node4 cur pz
.pz node1 node2 node3 node4 vol pol
.pz node1 node2 NODE3 node4 vol zer
.pz node1 node2 node3 node4 vol pz
"""

##################################################
# @29172

    Ef287 = """
.pz 1 0 3 0 cur pol
.pz 2 3 5 0 vol zer
.pz 4 1 4 1 cur pz
"""

##################################################
# @29186

    Faa33 = """
.SENS OUTVAR
.SENS OUTVAR AC DEC ND FSTART FSTOP
.SENS OUTVAR AC OCT NO FSTART FSTOP
.SENS OUTVAR AC LIN NP FSTART FSTOP
"""

##################################################
# @29194

    E962b = """
.SENS V(1,OUT)
.SENS V(OUT) AC DEC 10 100 100k
.SENS I(VTEST)
"""

##################################################
# @29206

    Ff257 = """
.tf outvar insrc
"""

##################################################
# @29211

    Ee06b = """
.tf v(5, 3) VIN
.tf i(VLOAD) VIN
"""

##################################################
# @29222

    F21a1 = """
.tran tstep tstop <tstart <tmax>> <uic>
"""

##################################################
# @29227

    Ed24c = """
.tran 1ns 100ns
.tran 1ns 1000ns 500ns
.tran 10ns 1us
"""

##################################################
# @29275

    Efc76 = """
* Shot noise test with B source, diode
* voltage on device (diode, forward)
Vdev out 0 DC 0 PULSE(0.4 0.45 10u)
* diode, forward direction, to be modeled with noise
D1 mess 0 DMOD
.model DMOD D IS=1e-14 N=1
X1 0 mess out ishot
* device between 1 and 2
* new output terminals of device including noise: 1 and 3
.subckt ishot 1 2 3
* white noise source with rms 1V
* 20000 sample points
VNG 0 11 DC 0 TRNOISE(1 1n 0 0)
*measure the current i(v1)
V1 2 3 DC 0
* calculate the shot noise
* sqrt(2*current*q*bandwidth)
BI 1 3 I=sqrt(2*abs(i(v1))*1.6e-19*1e7)*v(11)
.ends ishot

.tran 1n 20u
.control
run
plot (-1)*i(vdev)
.endc
.end
"""

##################################################
# @29316

    E3a50 = """
* white noise, 1/f noise, RTS noise

* voltage source
VRTS2 13 12 DC 0 trnoise(0 0 0 0 5m 18u 30u)
VRTS3 11 0 DC 0 trnoise(0 0 0 0 10m 20u 40u)
VALL 12 11 DC 0 trnoise(1m 1u 1.0 0.1m 15m 22u 50u)

VW1of 21 0 DC  trnoise(1m 1u 1.0 0.1m)

* current source
IRTS2 10 0 DC 0 trnoise(0 0 0 0 5m 18u 30u)
IRTS3 10 0 DC 0 trnoise(0 0 0 0 10m 20u 40u)
IALL 10 0 DC 0 trnoise(1m 1u 1.0 0.1m 15m 22u 50u)
R10 10 0 1

IW1of 9 0 DC  trnoise(1m 1u 1.0 0.1m)
Rall 9 0 1

* sample points
.tran 1u 500u

.control
run
plot v(13) v(21)
plot v(10) v(9)
.endc

.end

"""

##################################################
# @29368

    F413c = """
.pss gfreq tstab oscnob psspoints harms sciter steadycoeff <uic>
"""

##################################################
# @29373

    Ed660 = """
.pss 150 200e-3 2 1024 11 50 5e-3 uic
.pss 624e6 1u v_plus 1024 10 150 5e-3 uic
.pss 624e6 500n bout 1024 10 100 5e-3 uic
"""

############################################################
#
# 15.4
# Measurements after AC, DC and Transient Analysis
#

##################################################
# @29408

    Ef8af = """
*s* input file
* ...
.tran 1ns 1000ns
* ...
*********************************
.control
run
write outputfile data
.endc
*********************************
.end
"""

##################################################
# @29447

    Ee729 = """
*s* File: simple-meas-tran.sp
* Simple .measure examples
* transient simulation of two sine
* signals with different frequencies
vac1 1 0 DC 0 sin(0 1 1k 0 0)
vac2 2 0 DC 0 sin(0 1.2 0.9k 0 0)
.tran 10u 5m
*
* .measure tran ... $ for the different inputs see below!
*
.control
run
plot v(1) v(2)
.endc
.end
"""

##################################################
# @29472

    F1159 = """
.MEASURE {DC|AC|TRAN|SP} result TRIG trig_variable VAL=val
+ <TD=td> <CROSS=# | CROSS=LAST> <RISE=# | RISE=LAST>
+ <FALL=# | FALL=LAST> <TRIG AT=time> TARG targ_variable
+ VAL=val <TD=td> <CROSS=# | CROSS=LAST> <RISE=# |
+ RISE=LAST> <FALL=# | FALL=LAST> <TARG AT=time>
"""

##################################################
# @29525

    F5ba7 = """
.MEASURE {DC|AC|TRAN|SP} result WHEN out_variable=val
+ <TD=td> <FROM=val> <TO=val> <CROSS=# | CROSS=LAST>
+ <RISE=# | RISE=LAST> <FALL=# | FALL=LAST>
"""

##################################################
# @29540

    F6507 = """
.MEASURE {DC|AC|TRAN|SP} result
+ WHEN out_variable=out_variable2
+ <TD=td> <FROM=val> <TO=val> <CROSS=# | CROSS=LAST>
+ <RISE=# | RISE=LAST> <FALL=# | FALL=LAST>
"""

##################################################
# @29556

    F0b08 = """
.MEASURE {DC|AC|TRAN|SP} result FIND out_variable
+ WHEN out_variable2=val <TD=td> <FROM=val> <TO=val>
+ <CROSS=# | CROSS=LAST> <RISE=# | RISE=LAST>
+ <FALL=# | FALL=LAST>
"""

##################################################
# @29572

    Fad98 = """
.MEASURE {DC|AC|TRAN|SP} result FIND out_variable
+ WHEN out_variable2=out_variable3  <TD=td>
+ <CROSS=# | CROSS=LAST>
+ <RISE=#|RISE=LAST> <FALL=#|FALL=LAST>
"""

##################################################
# @29588

    F87be = """
.MEASURE {DC|AC|TRAN|SP} result FIND out_variable AT=val
"""

##################################################
# @29602

    F15b8 = """
.MEASURE {DC|AC|TRAN|SP} result
+ {AVG|MIN|MAX|PP|RMS|MIN_AT|MAX_AT}
+ out_variable <TD=td> <FROM=val> <TO=val>
"""

##################################################
# @29634

    Ff073 = """
.MEASURE {DC|AC|TRAN|SP} result INTEG<RAL> out_variable
+ <TD=td> <FROM=val> <TO=val>
"""

##################################################
# @29648

    F490c = """
.MEASURE {DC|AC|TRAN|SP} result  param='expression'
"""

##################################################
# @29680

    F8b9d = """
.MEASURE {DC|TRAN|AC|SP} result
+ FIND par('expression') AT=val
"""

##################################################
# @29697

    F99e6 = """
.MEASURE {DC|AC|TRAN|SP} result DERIV<ATIVE> out_variable
+ AT=val

.MEASURE {DC|AC|TRAN|SP} result DERIV<ATIVE> out_variable
+ WHEN out_variable2=val <TD=td>
+ <CROSS=# | CROSS=LAST> <RISE=#|RISE=LAST>
+ <FALL=#|FALL=LAST>

.MEASURE {DC|AC|TRAN|SP} result DERIV<ATIVE> out_variable
+ WHEN out_variable2=out_variable3
+ <TD=td> <CROSS=# | CROSS=LAST>
+ <RISE=#|RISE=LAST> <FALL=#|FALL=LAST>
"""

##################################################
# @29718

    E7b8e = """
.meas tran inv_delay2 trig v(in) val='vp/2' td=1n fall=1
+     targ v(out) val='vp/2' rise=1
.meas tran test_data1 trig AT = 1n targ v(out)
+     val='vp/2' rise=3
.meas tran out_slew trig v(out) val='0.2*vp' rise=2
+     targ v(out) val='0.8*vp' rise=2
.meas tran delay_chk param='(inv_delay < 100ps) ? 1 : 0'
.meas tran skew when v(out)=0.6
.meas tran skew2 when v(out)=skew_meas
.meas tran skew3 when v(out)=skew_meas fall=2
.meas tran skew4 when v(out)=skew_meas fall=LAST
.meas tran skew5 FIND v(out) AT=2n
.meas tran v0_min  min i(v0)
+     from='dfall' to='dfall+period'
.meas tran v0_avg avg i(v0)
+     from='dfall' to='dfall+period'
.meas tran v0_integ integ i(v0)
+     from='dfall' to='dfall+period'
.meas tran v0_rms rms i(v0)
+     from='dfall' to='dfall+period'
.meas dc is_at FIND i(vs) AT=1
.meas dc is_max max i(vs) from=0 to=3.5
.meas dc vds_at when i(vs)=0.01
.meas ac vout_at FIND v(out) AT=1MEG
.meas ac vout_atd FIND vdb(out) AT=1MEG
.meas ac vout_max max v(out) from=1k to=10MEG
.meas ac freq_at when v(out)=0.1
.meas ac vout_diff trig v(out) val=0.1 rise=1 targ v(out)
+     val=0.1 fall=1
.meas ac fixed_diff trig AT = 10k targ v(out)
+     val=0.1 rise=1
.meas ac vout_avg   avg   v(out) from=10k to=1MEG
.meas ac vout_integ integ v(out) from=20k to=500k
.meas ac freq_at2 when v(out)=0.1 fall=LAST
.meas ac bw_chk param='(vout_diff < 100k) ? 1 : 0'
.meas ac vout_rms rms v(out) from=10 to=1G
"""

############################################################
#
# 15.5
# Safe Operating Area (SOA) warning messages
#

############################################################
#
# 15.6
# Batch Output
#

##################################################
# @29925

    F49f9 = """
.save vector vector vector ...
"""

##################################################
# @29930

    E61a1 = """
.save i(vin) node1 v(node2)
.save @m1[id] vsource#branch
.save all @m2[vdsat]
"""

##################################################
# @29944

    F553b = """
.print prtype ov1 <ov2 ... ov8>
"""

##################################################
# @29949

    E86ff = """
.print tran v(4) i(vin)
.print dc v(2) i(vsrc) v(23, 17)
.print ac vm(4, 2) vr(7) vp(8, 3)
"""

##################################################
# @30036

    F2712 = """
.plot pltype ov1 <(plo1, phi1)> <ov2 <(plo2, phi2)> ... ov8>
"""

##################################################
# @30041

    SEc010 = """
.plot dc v(4) v(5) v(1)
.plot tran v(17, 5) (2, 5) i(vin) v(17) (1, 9)
.plot ac vm(5) vm(31, 24) vdb(5) vp(5)
.plot disto hd2 hd3(R) sim2
.plot tran v(5, 3) v(4) (0, 5) v(7) (0, 10)
"""

##################################################
# @30057

    Faa14 = """
.four freq ov1 <ov2 ov3 ...>
"""

##################################################
# @30062

    Ed60e = """
.four 100K v(5)
"""

##################################################
# @30071

    F1700 = """
.probe vector <vector vector ...>
"""

##################################################
# @30076

    F0ee3 = """
.probe i(vin) input output
.probe @m1[id]
"""

##################################################
# @30087

    F10ed = """
par('expression')
output=par('expression')  $ not in .measure ac
"""

##################################################
# @30093

    Ee229 = """
.four 1001 sq1=par('v(1)*v(1)')
.measure tran vtest find par('(v(2)*v(1))') AT=2.3m
.print tran output=par('v(1)/v(2)') v(1) v(2)
.plot dc v(1) diff=par('(v(4)-v(2))/0.01') out222
"""

############################################################
#
# 15.7
# Measuring current through device terminals
#

##################################################
# @30125

    Eaa20 = """
*measure current through R1
V1 1 0 1
R1 1 0 5
R2 1 0 10
* will become
V1 1 0 1
R1 1 11 5
Vmess 11 0 dc 0
R2 1 0 10
"""

##################################################
# @30140

    E6283 = """
*measure current through R1 and R2
V1 1 0 1
R1 1 0 5
R2 1 0 10
.options savecurrents
"""

####################################################################################################
#
# Chapter 16 Starting ngspice
#

class StartingNgspice(Examples):

############################################################
#
# 16.1 Introduction
#

############################################################
#
# 16.4
# Starting options
#

##################################################
# @30392

    E9c24 = """
*  ADDER - 4 BIT ALL-NAND-GATE BINARY ADDER
.control
unset askquit
save vcc#branch
run
plot vcc#branch
rusage all
.endc
"""

##################################################
# @30408

    E8ee6 = """
*  ADDER - 4 BIT ALL-NAND-GATE BINARY ADDER
.control
unset askquit
save vcc#branch
run
write adder.raw vcc#branch
quit
.endc
"""

##################################################
# @30428

    E2a62 = """
*  ADDER - 4 BIT ALL-NAND-GATE BINARY ADDER
.control
unset askquit
save vcc#branch
tran 1n 500n
plot vcc#branch
rusage all
.endc
"""

############################################################
#
# 16.5
# Standard configuration file spinit
#

##################################################
# @30452

    scb86 = """
* Standard ngspice init file
alias exit quit
alias acct rusage all
** set the number of threads in openmp
** default (if compiled with --enable-openmp) is: 2
set num_threads=4

if $?sharedmode
  unset interactive
  unset moremode
else
  set interactive
  set x11lineararcs
end

strcmp __flag $program "ngspice"
if $__flag = 0

 codemodel ../lib/spice/spice2poly.cm
 codemodel ../lib/spice/analog.cm
 codemodel ../lib/spice/digital.cm
 codemodel ../lib/spice/xtradev.cm
 codemodel ../lib/spice/xtraevt.cm
 codemodel ../lib/spice/table.cm

end
unset __flag
"""

############################################################
#
# 16.6
# User defined configuration file .spiceinit
#

##################################################
# @30496

    s5e51 = """
* User defined ngspice init file
set filetype=ascii
*set ngdebug
set numthreads = 8
*set outputpath=C:\Spice64\out
set ngbehavior = psa
"""

############################################################
#
# 16.11 Server mode option -s
#

##################################################
# @30742

    s26aa = """
cat input.cir|ngspice -s|less
"""

##################################################
# @30751

    Ecd75 = """
*s* test -s
v1 1 0 1
r1 1 0 2k
.options filetype=ascii
.save i(v1)
.dc v1 -1 1 0.5
.end
"""

############################################################
#
# 16.12 Pipe mode option -p
#

##################################################
# @30811

    s64d1 = """
cat pipe-circuit.cir | ngspice -p
"""

##################################################
# @30820

    sda18 = """
*pipe-circuit.cir
source circuit.cir
tran 10u 2m
write pcir.raw all
"""

##################################################
# @30831

    E76ab = """
* Circuit.cir
V1 n0 0 SIN(0 10 1kHz)
C1 n1 n0 3.3nF
R1 0 n1 1k
.end
"""

############################################################
#
# 16.13 Ngspice control via input, output fifos
#

##################################################
# @30845

    sfb37 = """
#!/usr/bin/env bash

NGSPICE_COMMAND="ngspice"

rm input.fifo
rm output.fifo

mkfifo input.fifo
mkfifo output.fifo

$NGSPICE_COMMAND  -p -i <input.fifo >output.fifo &

exec 3>input.fifo
echo "I can write to input.fifo"

echo "Start processing..."
echo ""

echo "source circuit.cir" >&3
echo "unset askquit" >&3
echo "set nobreak" >&3
echo "tran 0.01ms 0.1ms">&3
echo "print n0" >&3
echo "quit" >&3

echo "Try to open output.fifo ..."
exec 4<output.fifo
echo "I can read from output.fifo"

echo "Ready to read..."
while read output
do
      echo $output
done <&4

exec 3>&-
exec 4>&-

echo "End processing"
"""

############################################################
#
# 16.14
# Compatibility
#

##################################################
# @31079

    Ed6c8 = """
*s* parameter sweep
* resistive divider, R1 swept from start_r to stop_r
* replaces .STEP R1 1k 10k 1k

R1 1 2 1k
R2 2 0 1k

VDD 1 0 DC 1
.dc VDD 0 1 .1

.control
let start_r = 1k
let stop_r = 10k
let delta_r = 1k
let r_act = start_r
* loop
while r_act le stop_r
  alter r1 r_act
  run
  write dc-sweep.out v(2)
  set appendwrite
  let r_act = r_act + delta_r
end
plot dc1.v(2) dc2.v(2) dc3.v(2) dc4.v(2) dc5.v(2)
+ dc6.v(2) dc7.v(2) dc8.v(2) dc9.v(2) dc10.v(2)
.endc

.end
"""

##################################################
# @31203

    E2939 = """
R1 1 0 4K7   ; 4.7k
R2 1 0 4R7   ; 4.7
R3 1 0 R47   ; 0.47
R4 1 0 470R  ; 470
R5 1 0 47K   ; 47k
R6 1 0 47K3  ; 47.3k
R7 1 0 470K  ; 470k
R8 1 0 4Meg7  tc1=1e-6 tc2=1e-9 dtemp=6
*            ; 4.7Meg  <-- Not defined in the RKM notation
R9 1 0 4L7   ; 4.7m
R10 1 0 470L ; 470m
R11 1 0 4M7  ; 4.7m  <-- This deviates fom the RKM notation
"""

##################################################
# @31221

    Ef20e = """
C1 1 0 4p7   ; 4.7p
C2 1 0 4n7   ; 4.7n
C3 1 0 4u7   ; 4.7u
C4 1 0 4m7   ; 4.7m
C5 1 0 4F7   ; 4.7f  <-- This deviates fom the RKM notation
C6 1 0 47p3  ; 4.73p
C7 1 0 470p  ; 470p
C8 1 0 4u76 tc1=1e-6 tc2=1e-9 dtemp=6
*            ; 4.76u
C9 1 0 4m7   ; 4.7m
C10 1 0 470nF ; 470n
C11 1 0 47fF ; 47f  <-- This deviates fom the RKM notation
"""

############################################################
#
# 16.15 Tests
#

############################################################
#
# 16.16
# Tools for debugging a circuit netlist
#

############################################################
#
# 16.17 Reporting bugs and errors
#

####################################################################################################
#
# Chapter 17
# Interactive Interpreter
#

class InteractiveInterpreter(Examples):

############################################################
#
# 17.1 Introduction
#

############################################################
#
# 17.2
# Expressions, Functions, and Constants
#

##################################################
# @31343

    sa8b2 = """
+ - * / ^ % ,
"""

##################################################
# @31773

    sbb48 = """
cos(TIME) + db(v(3))
sin(cos(log([1 2 3 4 5 6 7 8 9 10])))
TIME * rnd(v(9)) - 15 * cos(vin#branch) ^ [7.9e5 8]
not ((ac3.FREQ[32] & tran1.TIME[10]) gt 3)
(sunif(0) ge 0) ? 1.0 : 2.0
mag(fft(v(18)))
"""

############################################################
#
# 17.3
# Plots
#

############################################################
#
# 17.4
# Command Interpretation
#

##################################################
# @31970

    E0b74 = """
.control
pre_set strict_errorhandling
unset ngdebug
*save outputs and specials
save x1.x1.x1.7 V(9) V(10) V(11) V(12) V(13)
run
display
* plot the inputs, use offset to plot on top of each other
plot  v(1) v(2)+4 v(3)+8 v(4)+12 v(5)+16 v(6)+20 v(7)+24 v(8)+28
* plot the outputs, use offset to plot on top of each other
plot  v(9) v(10)+4 v(11)+8 v(12)+12 v(13)+16
.endc
"""

############################################################
#
# 17.5
# Commands
#

##################################################
# @31992

    F3d34 = """
ac ( DEC | OCT | LIN ) N Fstart Fstop
"""

##################################################
# @32013

    Eaebf = """
* AC test
Iin 1 0 AC 1
R1 1 2 100
L1 2 0 1

.control
AC LIN 101 10 10K
plot v(2)       $ real part !
plot mag(v(2))  $ magnitude
plot db(v(2))   $ same as vdb(2)
plot imag(v(2)) $ imaginary part of v(2)
plot real(v(2)) $ same as plot v(2)
plot phase(v(2))  $ phase in rad
plot cph(v(2))  $ phase in rad, continuous beyond pi
plot 180/PI*phase(v(2)) $ phase in deg
.endc
.end
"""

##################################################
# @32038

    Fcf46 = """
alias [word] [text ...]
"""

##################################################
# @32050

    F621b = """
alter dev = <expression>
alter dev param = <expression>
alter @dev[param] = <expression>
"""

##################################################
# @32061

    F2381 = """
alter device value
alter device parameter value [ parameter value ]
"""

##################################################
# @32073

    E808a = """
alter vd = 0.1
alter vg dc = 0.6
alter @m1[w]= 15e-06
alter  @vg[sin] [ -1 1.5 2MEG ]
alter @Vi[pwl] = [ 0 1.2 100p 0 ]
"""

##################################################
# @32086

    Ef16a = """
let newfreq = 10k
alter  @vg[sin] [ -1 1.5 $&newfreq ]  $ vector
set newperiod = 150u
alter @Vi[pwl] = [ 0 1.2 $newperiod 0 ] $ variable
"""

##################################################
# @32098

    E58f6 = """
alter m.xm1.msub1 w = 20u
alter @m.xm1.msub1[w] = 20u
"""

##################################################
# @32107

    Fb9c8 = """
altermod mod param = <expression>
altermod @mod[param] = <expression>
"""

##################################################
# @32113

    E25bd = """
altermod nc1 tox = 10e-9
altermod @nc1[tox] = 10e-9
"""

##################################################
# @32142

    Ff1b6 = """
altermod mod1 [mod2 .. mod15] file = <model file name>
altermod mod1 [mod2 .. mod15] file  <model file name>
"""

##################################################
# @32148

    E822a = """
altermod nc1 file = BSIM3_nmos.mod
altermod nc1 pc1 file BSIM4_mos.mod
"""

##################################################
# @32159

    F90ab = """
alterparam paramname=pvalue
alterparam subname paramname=pvalue
"""

##################################################
# @32165

    E0e7e = """
.param npar = 5
* ...
alterparam npar = 7 $ change npar from 5 to 7
reset
"""

##################################################
# @32173

    Ef3e6 = """
.subckt sname
.param subpar = 13
* ...
.ends
* ...
alterparam sname subpar = 11 $ change subpar from 13 to 11
reset
"""

##################################################
# @32189

    F1c6d = """
asciiplot plotargs
"""

##################################################
# @32198

    Feee2 = """
aspice input-file [output-file]
"""

##################################################
# @32207

    F6885 = """
bug
"""

##################################################
# @32217

    F5781 = """
cd [directory]
"""

##################################################
# @32227

    Fe917 = """
cdump
"""

##################################################
# @32236

    Ef4ba = """
let mc_runs=5
let run=0
* ...
define agauss(nom, avar, sig) (nom + avar/sig * sgauss(0))
define limit(nom, avar) (nom + ((sgauss(0) >=0) ? avar : -avar))
dowhile run < mc_runs
  alter c1=unif(1e-09, 0.1)
* ...
  ac oct 100 250k 10meg
  meas ac bw trig vdb(out) val=-10 rise=1 targ vdb(out)
+ val=-10 fall=1
  set run="$&run"
* ...
  let run=run + 1
end
plot db({$scratch}.allv)
echo
print {$scratch}.bwh
cdump
"""

##################################################
# @32262

    F5217 = """
circbyline line
"""

##################################################
# @32271

    Eedca = """
circbyline test circuit
circbyline v1 1 0 1
circbyline r1 1 0 1
circbyline .dc v1 0.5 1.5 0.1
circbyline .end
run
plot i(v1)
"""

##################################################
# @32285

    F5fb4 = """
codemodel [library file]
"""

##################################################
# @32295

    F1466 = """
compose name values value1 [ value2 ... ]
"""

##################################################
# @32300

    F97ff = """
compose name start=val stop=val step=val
compose name center=val span=val step=val
compose name lin=val center=val span=val
compose name lin=val <start=val> <stop=val> <step=val>
"""

##################################################
# @32308

    F830b = """
compose name (log=val | dec=val | oct=val) start=val stop=val
compose name (log=val | dec=val | oct=val) center=val span=val
"""

##################################################
# @32314

    F883b = """
compose name gauss=val <mean=val> <sd=val>
"""

##################################################
# @32319

    F5758 = """
compose name unif=val <mean=val> <span=val>
compose name unif=val start=val stop=val
"""

##################################################
# @32454

    E8045 = """
let cut-tstart = time1
let cut-tstop = time2
cutout
"""

##################################################
# @32467

    F7946 = """
dc Source Vstart Vstop Vincr [ Source2 Vstart2 Vstop2 Vincr2 ]
"""

##################################################
# @32477

    Fb5a7 = """
define function(arg1, arg2, ...) expression
"""

##################################################
# @32486

    s3e3e = """
define max(x,y) (x > y) * x + (x <= y) * y
define min(x,y) (x < y) * x + (x >= y) * y
define limit(nom, avar) (nom + ((sgauss(0) >= 0) ? avar : -avar))
"""

##################################################
# @32495

    F67c8 = """
deftype [v | p] typename abbrev
"""

##################################################
# @32504

    E805c = """
deftype v capacitance F
settype capacitance moscap
plot moscap vs v(cc)
"""

##################################################
# @32514

    Ff698 = """
delete [ debug-number ... ]
"""

##################################################
# @32523

    Ff36d = """
destroy [plotnames | all]
"""

##################################################
# @32532

    F5ff6 = """
devhelp [[-csv] device_name [parameter]]
"""

##################################################
# @32543

    E485a = """
devhelp
devhelp resistor
devhelp capacitor ic
"""

##################################################
# @32552

    F43f1 = """
diff plot1 plot2 [vec ...]
"""

##################################################
# @32562

    s0b59 = """
display [varname ...]
"""

##################################################
# @32572

    Fc67a = """
echo [-n] [text | $variable | $&vector] ...
"""

##################################################
# @32581

    Fc242 = """
edit [ file-name ]
"""

##################################################
# @32599

    F0045 = """
edisplay
"""

##################################################
# @32609

    Fb255 = """
eprint node [node]
eprint node [node] > nodeout.txt $ output redirected
"""

##################################################
# @32620

    sc9b5 = """
eprvcd node1 node2 .. noden [ > filename ]
"""

##################################################
# @32630

    s2914 = """
fft vector1 [vector2] ...
"""

##################################################
# @32650

    s60cf = """
ngspice 8 -> setplot tran1
ngspice 9 -> linearize V(2)
ngspice 9 -> set specwindow=blackman
ngspice 10 -> fft V(2)
ngspice 11 -> plot mag(V(2))
"""

##################################################
# @32692

    s45a2 = """
fourier fundamental_frequency [expression ...]
"""

##################################################
# @32703

    s6fef = """
* do the transient analysis
tran 1n 1m
* do the fourier analysis
fourier 3.34e6 v(2) v(3) $ first call
fourier 100e6 v(2) v(3)  $ second call
* get individual values
let newt1 = fourier11[0][1]
let newt2 = fourier11[1][1]
let newt3 = fourier11[2][1]
let newt4 = fourier12[0][4]
let newt5 = fourier12[1][4]
let newt6 = fourier12[2][4]
* plot magnitude of second expression (v(3))
* from first call versus frequency
plot fourier12[1] vs fourier12[0]
"""

##################################################
# @32726

    s162d = """
getcwd
"""

##################################################
# @32736

    s8d16 = """
gnuplot file plotargs
"""

##################################################
# @32745

    sb503 = """
hardcopy file plotargs
"""

##################################################
# @32756

    s456f = """
history [-r] [number]
"""

##################################################
# @33059

    sec99 = """
inventory
"""

##################################################
# @33068

    sbe30 = """
iplot [ node ...]
"""

##################################################
# @33079

    s6966 = """
jobs
"""

##################################################
# @33089

    s348d = """
let name = expr
"""

##################################################
# @33114

    sf9f9 = """
linearize vec ...
"""

##################################################
# @33123

    sf9a6 = """
ngspice 8 -> setplot tran1
ngspice 9 -> linearize V(2)
ngspice 9 -> set specwindow=blackman
ngspice 10 -> fft V(2)
ngspice 11 -> plot mag(V(2))tstep
"""

##################################################
# @33138

    sca07 = """
* original time scale by .tran command is from 0 to 16ns
save  out25 out50
run
plot out25 out50
let lin-tstart = 4n $ skip the start-up phase
let lin-tstop = 14n $ end earlier(just for demonstration)
let lin-tstep = 5p
linearize out25 out50
plot out25 out50
"""

##################################################
# @33156

    sf94a = """
listing [logical] [physical] [deck] [expand] [runable] [param]
"""

##################################################
# @33165

    sc806 = """
source d:\myngspice\inputs\decade_counter.cir
listing r > $inputdir/decade_counter_runable.cir
"""

##################################################
# @33178

    sfec1 = """
load [filename] ...
"""

##################################################
# @33188

    sdee5 = """
mc_source
"""

##################################################
# @33198

    Ffab6 = """
MEAS {DC|AC|TRAN|SP} result TRIG trig_variable VAL=val <TD=td>
<CROSS=# | CROSS=LAST> <RISE=#|RISE=LAST> <FALL=#|FALL=LAST>
<TRIG AT=time> TARG targ_variable VAL=val <TD=td>
<CROSS=# | CROSS=LAST> <RISE=#|RISE=LAST>
<FALL=#|FALL=LAST> <TRIG AT=time>
"""

##################################################
# @33213

    E6d80 = """
let vdiff = v(n1)-v(n0)
meas tran vtest find vdiff at=0.04e-3
*the following will not do here:
*meas tran vtest find par('v(n1)-v(n0)') at=0.04e-3
"""

##################################################
# @33223

    s4b28 = """
mdump <filename>
"""

##################################################
# @33232

    s7c35 = """
mrdump <filename>
"""

##################################################
# @33241

    s2471 = """
* Dump matrix and RHS values after 10 and 20 steps
* of a transient simulation
source rc.cir
step 10
mdump m1.txt
mrdump mr1.txt
step 10
mdump m2.txt
mrdump mr2.txt
* just to continue to the end
step 10000
"""

##################################################
# @33264

    sb55d = """
.control
tran 1e-6 1e-3
write test_tran.raw
noise V(out) vinp dec 333 1 1e8 16
print inoise_total onoise_total
*first option to get all of the output (two files)
setplot noise1
write test_noise1.raw all
setplot noise2
write test_noise2.raw all
* second option (all in one raw-file)
write testall.raw noise1.all noise2.all
.endc
"""

##################################################
# @33283

    s824f = """
op
"""

##################################################
# @33293

    sc6fc = """
option [option=val] [option=val] ...
"""

##################################################
# @33304

    sdd55 = """
.control
set noinit

option trtol=1
echo
echo trtol=1
run
rusage traniter trantime
reset
option trtol=3
echo
echo trtol=3
run
rusage traniter trantime
reset
option trtol=5
echo
echo trtol=5
run
rusage traniter trantime
reset
option trtol=7
echo
echo trtol=7
run
rusage traniter trantime
plot tran1.v(out25) tran1.v(out50) v(out25)  v(out50)
.endc
"""

##################################################
# @33339

    sc6bb = """
plot expr1 [vs scale_expr1] [expr2 [vs scale_expr2]] ...
[ylimit ylo yhi] [xlimit xlo xhi] [xindices xilo xihi]
[xcompress comp] [xdelta xdel] [ydelta ydel]
[xlog] [ylog] [loglog] [nogrid]
[linplot] [combplot] [pointplot] [nointerp] [retraceplot]
[polar] [smith] [smithgrid]
[xlabel word] [ylabel word] [title word]
[samep] [linear] [kicad] [plainplot]
"""

##################################################
# @33458

    se3f4 = """
pre_<command>
"""

##################################################
# @33467

    sbc0b = """
pre_unset ngdebug
pre_set strict_errorhandling
pre_codemodel mymod.cm
"""

##################################################
# @33479

    s726a = """
print [col] [line] expr ...
"""

##################################################
# @33488

    sa9a6 = """
print all
set width=300
print v(1) > outfile.out
"""

##################################################
# @33497

    s6974 = """
psd ave vector1 [vector2] ...
"""

##################################################
# @33508

    s43fe = """
quit
quit [exitcode]
"""

##################################################
# @33520

    sd9a5 = """
rehash
"""

##################################################
# @33529

    sa6da = """
remcirc
"""

##################################################
# @33538

    sccef = """
remzerovec
"""

##################################################
# @33548

    s91ef = """
reset
"""

##################################################
# @33561

    s6043 = """
reshape vector vector ...
or
reshape vector vector ... [ dimension, dimension, ... ]
or
reshape vector vector ... [ dimension ][ dimension ] ...
"""

##################################################
# @33574

    s04d6 = """
* generate vector with all (here 30) elements
let newvec=vector(30)
* reshape vector to format 3 x 10
reshape newvec [3][10]
* access elements of the reshaped vector
print newvec[0][9]
print newvec[1][5]
let newt = newvec[2][4]
"""

##################################################
# @33589

    sa2b4 = """
resume
"""

##################################################
# @33598

    sd1f6 = """
rspice <input file>
"""

##################################################
# @33609

    s63f9 = """
run [rawfile]
"""

##################################################
# @33618

    sc3d0 = """
rusage [resource ...]
"""

##################################################
# @33683

    s06b2 = """
save [all | outvec ...]
"""

##################################################
# @33700

    s1b08 = """
save vd_node vs#branch v(vs_node) i(vs2)
"""

##################################################
# @33709

    s5cce = """
save all @mn1[gm]
"""

##################################################
# @33720

    s5ed0 = """
save 3 x1.x2.x1.x2.8 v.x1.x1.x1.vmeas#branch
"""

##################################################
# @33727

    s7d50 = """
save @m.xmos3.mn1[gm]
"""

##################################################
# @33738

    s762a = """
save none
"""

##################################################
# @33747

    sf7b7 = """
sens output_variable
sens output_variable ac ( DEC | OCT | LIN ) N Fstart Fstop
"""

##################################################
# @33758

    s3ee8 = """
set [word]
set [word = value] ...
"""

##################################################
# @33780

    s1e74 = """
set invar < infile.txt
echo $invar
echo $invar[2]
echo $invar[5]
"""

##################################################
# @33792

    sd244 = """
* testing set input from file
3
NeXt
4
5 and 7
"""

##################################################
# @33815

    sf105 = """
setcs [word]
setcs [word = value] ...
"""

##################################################
# @33834

    s2891 = """
setcirc [circuit number]
"""

##################################################
# @33846

    s7fe4 = """
setplot
setplot [plotname]
setplot previous
setplot next
setplot new
"""

##################################################
# @33862

    s32f2 = """
setscale [vector]
"""

##################################################
# @33872

    s2da7 = """
setseed [number]
"""

##################################################
# @33881

    s9e2a = """
settype type vector ...
"""

##################################################
# @34097

    sa335 = """
shell [ command ]
"""

##################################################
# @34106

    sc4fe = """
shift [varname] [number]
"""

##################################################
# @34116

    sc56a = """
show devices [ : parameters ] , ...
"""

##################################################
# @34131

    s64f1 = """
showmod models [ : parameters ] , ...
"""

##################################################
# @34140

    sfc14 = """
showmod #cmosn #cmosp : lkvth0 vth0
"""

##################################################
# @34149

    s4c1a = """
netlist for default bipolar transistor
Q1 cc bb ee defbib
.model defbip npn
.control
op
showmod q1
.endc
"""

##################################################
# @34165

    s96cf = """
snload circuit-file file
"""

##################################################
# @34176

    se050 = """
*  SCRIPT: ADDER - 4 BIT BINARY
* script to reload circuit and continue the simulation
* begin with editing the file location
* to be started with 'ngspice adder_snload.script'

.control
* cd to where all files are located
cd D:\Spice_general\ngspice\examples\snapshot
* load circuit and snpashot file
snload adder_mos_circ.cir adder500.snap
* continue simulation
resume
* plot some node voltages
plot v(10) v(11) v(12)
.endc
"""

##################################################
# @34200

    sbd8b = """
snsave file
"""

##################################################
# @34209

    s407c = """
Example input file for snsave
* load a circuit (including transistor models and .tran command)
* starts transient simulation until stop point
* store intermediate data to file
* begin with editing the file location
* to be run with 'ngspice adder_mos.cir'

.include adder_mos_circ.cir

.control
*cd to where all files are located
cd D:\Spice_general\ngspice\examples\snapshot
unset askquit
set noinit
*interrupt condition for the simulation
stop when time > 500n
* simulate
run
* store snapshot to file
snsave adder500.snap
quit
.endc

.END
"""

##################################################
# @34244

    s6347 = """
source infile
"""

##################################################
# @34258

    seed8 = """
spec start_freq stop_freq step_freq vector [vector ...]
"""

##################################################
# @34268

    sadba = """
ngspice 13 -> linearize
ngspice 14 -> set specwindow = "blackman"
ngspice 15 -> spec 10 1000000 1000 v(out)
ngspice 16 -> plot mag(v(out))
"""

##################################################
# @34281

    s48a3 = """
status
"""

##################################################
# @34290

    sba8d = """
step [ number ]
"""

##################################################
# @34300

    sef20 = """
stop [ after n] [ when value cond value ] ...
"""

##################################################
# @34396

    sad7d = """
strcmp _flag $string1 "string2"
"""

##################################################
# @34405

    sbfd5 = """
sysinfo
"""

##################################################
# @34422

    s4373 = """
ngspice 1 -> sysinfo
OS: CYGWIN_NT-5.1 1.5.25(0.156/4/2) 2008-06-12 19:34
CPU: Intel(R) Pentium(R) 4 CPU 3.40GHz
Logical processors: 2
Total DRAM available = 1535.480469 MB.
DRAM currently available = 984.683594 MB.
ngspice 2 ->
"""

##################################################
# @34437

    s40e6 = """
tf output_node input_source
"""

##################################################
# @34452

    s8dac = """
* Tf test circuit
vs    1    0    dc 5
r1    1    2    100
r2    2    3    50
r3    3    0    150
r4    2    0    200

.control
tf v(3,5) vs
print all
.endc

.end
"""

##################################################
# @34480

    s1ed8 = """
trace [ node ...]
"""

##################################################
# @34490

    sfc2b = """
tran Tstep Tstop [ Tstart [ Tmax ] ] [ UIC ]
"""

##################################################
# @34501

    s2efd = """
transpose vector vector ...
"""

##################################################
# @34510

    sd6fc = """
ngspice > dc vgg 0 5 1 vdd 0 5 1
ngspice > plot i(vdd)
ngspice > reshape all [6,6]
ngspice > transpose i(vdd) v(drain)
ngspice > plot i(vdd) vs v(drain)[0]
"""

##################################################
# @34521

    sae97 = """
unalias [word ...]
"""

##################################################
# @34530

    sc6de = """
undefine [function ...]
undefine *
"""

##################################################
# @34541

    s3c4b = """
unlet [vector ...]
"""

##################################################
# @34550

    seeba = """
unset [word ...]
unset *
"""

##################################################
# @34560

    s81f2 = """
version [-s | -f | <version id>]
"""

##################################################
# @34577

    s794a = """
ngspice 10 -> version
******
** ngspice-24 : Circuit level simulation program
** The U. C. Berkeley CAD Group
** Copyright 1985-1994, Regents of the University of California.
** Please get your ngspice manual from
           http://ngspice.sourceforge.net/docs.html
** Please file your bug-reports at
           http://ngspice.sourceforge.net/bugrep.html
** Creation Date: Jan  1 2011   13:36:34
******
ngspice 2 ->
ngspice 11 -> version 14
Note: rawfile is version 14 (current version is 24)
ngspice 12 -> version 24
ngspice 13 ->
"""

##################################################
# @34602

    s4614 = """
where
"""

##################################################
# @34612

    s1544 = """
<set wr_singlescale>
<set wr_vecnames>
<option numdgt=7>
...
wrdata [file] [vecs]
"""

##################################################
# @34647

    sf092 = """
write [file] [exprs]
"""

##################################################
# @34662

    s7752 = """
wrnodev [file]
"""

##################################################
# @34671

    sae87 = """
* Intermediate Transient Solution
* Circuit: KiCad schematic
* Recorded at simulation time: 3.9
.ic v(net-_d1a1-pad2_) = -31.2016
.ic v(-32) = -32
.ic v(out) = -0.267414
.ic v(net-_q5-pad2_) = -26.5798
.ic v(q5tj) = 132.521
.ic v(q5tc) = 105.091
...
"""

##################################################
# @34689

    sae49 = """
stop when time=3.9
tran 20u 6
wrnodev $inputdir/F5ic1.txt
resume
wrnodev $inputdir/F5ic2.txt
...
"""

##################################################
# @34703

    sa870 = """
.include F5ic1.txt
...
"""

##################################################
# @34712

    sa2a0 = """
wrs2p [file]
"""

##################################################
# @34727

    sbfcd = """
!2-port S-parameter file
!Title: test for scattering parameters
!Generated by ngspice at Sat Oct 16 13:51:18  2010
# Hz S RI R 50
!freq             ReS11         ImS11        ReS21
 2.500000e+06 -1.358762e-03 -1.726349e-02 9.966563e-01
 5.000000e+06 -5.439573e-03 -3.397117e-02 9.867253e-01 ...
"""

############################################################
#
# 17.6
# Control Structures
#

##################################################
# @34743

    sabce = """
while condition
statement
...
end
"""

##################################################
# @34755

    s24cf = """
repeat [number]
statement
...
end
"""

##################################################
# @34767

    s4522 = """
dowhile condition
statement
...
end
"""

##################################################
# @34779

    s1baf = """
foreach var value ...
statement
...
end
"""

##################################################
# @34791

    s1fa5 = """
if condition
statement
...
else
statement
...
end
"""

##################################################
# @34806

    s29af = """
label word
"""

##################################################
# @34815

    sde7b = """
goto word
"""

##################################################
# @34824

    s3afb = """
if (1)
...
goto gohere
...
label gohere
end
"""

##################################################
# @34836

    s21a5 = """
continue [n]
"""

##################################################
# @34845

    sf019 = """
break [n]
"""

############################################################
#
# 17.7
# Internally predefined variables
#

############################################################
#
# 17.8
# Scripts
#

##################################################
# @35128

    s5eeb = """
* test node names from subcircuits
Xsub1 a b sub1

.subckt sub1 n11 n12
Xsub2 n11 n12 sub2
R11 n11 int1 1k
R12 n12 int1 1k
.ends

.subckt sub2 n21 n22
R21 n21 int2 1k
R22 n22 int2 1k
.ends

.end
"""

##################################################
# @35152

    s866f = """
r.xsub1.xsub2.r21 a xsub1.xsub2.int2 1k
r.xsub1.xsub2.r22 b xsub1.xsub2.int2 1k
r.xsub1.r11 a xsub1.int1 1k
r.xsub1.r12 b xsub1.int1 1k
"""

##################################################
# @35173

    sf3d5 = """
Test sequences for ngspice control structures
*vectors are used (except foreach)
*start in interactive mode

.control

* test sequence for while, dowhile
  let loop = 0
  echo
  echo enter loop with  "$&loop"
  dowhile loop < 3
    echo within dowhile loop "$&loop"
    let loop = loop + 1
  end
  echo after dowhile loop "$&loop"
  echo
  let loop = 0
  while loop < 3
    echo within while loop "$&loop"
    let loop = loop + 1
  end
  echo after while loop "$&loop"
  let loop = 3
  echo
  echo enter loop with  "$&loop"
  dowhile loop < 3
    echo within dowhile loop "$&loop"     $ output expected
    let loop = loop + 1
  end
  echo after dowhile loop "$&loop"
  echo
  let loop = 3
  while loop < 3
    echo within while loop "$&loop"       $ no output expected
    let loop = loop + 1
  end
  echo after while loop "$&loop"
"""

##################################################
# @35217

    s556f = """
* test for while, repeat, if, break
  let loop = 0
  while loop < 4
    let index = 0
    repeat
      let index = index + 1
      if index > 4
        break
      end
    end
    echo index "$&index"   loop "$&loop"
    let loop = loop + 1
  end

* test sequence for foreach
  echo
  foreach outvar 0 0.5 1 1.5
    echo parameters: $outvar   $ foreach parameters are variables,
                               $ not vectors!
  end

* test for if ... else ... end
  echo
  let loop = 0
  let index = 1
  dowhile loop < 10
    let index = index * 2
    if index < 128
      echo "$&index" lt 128
    else
      echo "$&index"  ge 128
    end
    let loop = loop + 1
  end

* simple test for label, goto
  echo
  let loop = 0
  label starthere
  echo start "$&loop"
  let loop = loop + 1
  if loop < 3
    goto starthere
  end
  echo end "$&loop"

"""

##################################################
# @35269

    s4c9d = """
* test for label, nested goto
  echo
  let loop = 0
  label starthere1
  echo start nested "$&loop"
  let loop = loop + 1
  if loop < 3
    if loop < 3
      goto starthere1
    end
  end
  echo end "$&loop"

* test for label, goto
  echo
  let index = 0
  label starthere2
  let loop = 0
  echo We are at start with index "$&index" and loop "$&loop"
  if index < 6
    label inhere
    let index = index + 1
    if loop < 3
      let loop = loop + 1
      if index > 1
        echo jump2
        goto starthere2
      end
    end
    echo jump
    goto inhere
  end
  echo We are at end with index "$&index" and loop "$&loop"

"""

##################################################
# @35309

    s803d = """
* test goto in while loop
  let loop = 0
  if 1    $ outer loop to allow nested forward label 'endlabel'
    while loop < 10
      if loop > 5
        echo jump
        goto endlabel
      end
      let loop = loop + 1
    end
    echo before  $ never reached
    label endlabel
    echo after "$&loop"
  end

* test for using variables, simple test for label, goto
  set loop = 0
  label starthe
  echo start $loop
  let loop = $loop + 1  $ expression needs vector at lhs
  set loop = "$&loop"   $ convert vector contents to variable
  if $loop < 3
    goto starthe
  end
  echo end $loop
.endc
"""

##################################################
# @35348

    s80cd = """
* test for script 'spectrum'
.control
load ring51_41.out
spectrum 10MEG 2500MEG 1MEG v(out25) v(out50)
.endc
"""

##################################################
# @35359

    s7988 = """
* agauss test in ngspice
* generate a sequence of gaussian distributed random numbers.
* test the distribution by sorting the numbers into
* a histogram (buckets)
.control
  define agauss(nom, avar, sig) (nom + avar/sig * sgauss(0))
  let mc_runs = 200
  let run = 0
  let no_buck = 8                $ number of buckets
  let bucket = unitvec(no_buck)  $ each element contains 1
  let delta = 3e-11    $ width of each bucket, depends
                       $ on avar and sig
  let lolimit = 1e-09 - 3*delta
  let hilimit = 1e-09 + 3*delta

  dowhile run < mc_runs
    let val = agauss(1e-09, 1e-10, 3) $ get the random number
    if (val < lolimit)
        let bucket[0] = bucket[0] + 1 $ 'lowest' bucket
    end
    let part = 1
    dowhile part < (no_buck - 1)
      if ((val < (lolimit + part*delta)) &
+         (val > (lolimit + (part-1)*delta)))
        let bucket[part] = bucket[part] + 1
                break
      end
      let part = part + 1
    end
    if (val > hilimit)
* 'highest' bucket
      let bucket[no_buck - 1] = bucket[no_buck - 1] + 1
    end
    let run = run + 1
  end

  let part = 0
  dowhile part < no_buck
    let value = bucket[part] - 1
    set value = "$&value"
* print the bucket's contents
    echo $value
    let part = part + 1
  end

.endc
.end
"""

##################################################
# @35415

    sf747 = """
parameter sweep
* resistive divider, R1 swept from start_r to stop_r
VDD 1 0 DC 1

R1 1 2 1k
R2 2 0 1k

.control
let start_r = 1k
let stop_r = 10k
let delta_r = 1k
let r_act = start_r
* loop
while r_act le stop_r
  alter r1 r_act
  op
  print v(2)
  let r_act = r_act + delta_r
end
.endc

.end
"""

##################################################
# @35447

    s4c3b = """
** MOSFET Gain Stage (AC):
** Benchmarking Implementation of BSIM4.0.0
** by Weidong Liu 5/16/2000.
** output redirection into file

M1 3 2 0 0 N1 L=1u W=4u
Rsource 1 2 100k
Rload 3 vdd 25k
Vdd vdd 0 1.8
Vin 1 0 1.2 ac 0.1

.control
ac dec 10 100 1000Meg
plot v(2) v(3)
let flen = length(frequency) $ length of the vector
let loopcounter = 0
echo output test > text.txt  $ start new file test.txt
* loop
while loopcounter lt flen
  let vout2 = v(2)[loopcounter] $ generate a single point
                                $ complex vector
  let vout2re = real(vout2)     $ generate a single point
                                $ real vector
  let vout2im = imag(vout2)     $ generate a single point
                                $ imaginary vector
  let vout3 = v(3)[loopcounter] $ generate a single
                                $ point complex vector
  let vout3re = real(vout3)     $ generate a single point
                                $ real vector
  let vout3im = imag(vout3)     $ generate a single point
                                $ imaginary vector
  let freq = frequency[loopcounter] $ generate a single point vector
  echo  bbb "$&freq" "$&vout2re" "$&vout2im"
+ "$&vout3re" "$&vout3im" >> text.txt
                                $ append text and
                                $ data to file
                                $ (continued from line above)
  let loopcounter = loopcounter + 1
end
.endc

.MODEL N1 NMOS LEVEL=14 VERSION=4.8.1 TNOM=27
.end
"""

############################################################
#
# 17.9
# Scattering parameters (S-parameters)
#

############################################################
#
# 17.10
# Using shell variables
#

##################################################
# @36629

    s362c = """
shell echo $HOME
/home/holger
"""

##################################################
# @36639

    scef6 = """
set myvar2=`/bin/bash -c "echo $HOME"`
echo $myvar2
/home/holger
"""

############################################################
#
# 17.11 MISCELLANEOUS
#

############################################################
#
# 17.12 Bugs
#

####################################################################################################
#
# Chapter 18 Ngspice User Interfaces
#

class NgspiceUserInterfaces(Examples):

############################################################
#
# 18.1
# MS Windows Graphical User Interface
#

##################################################
# @36663

    sd0ef = """
***** Single NMOS Transistor For BSIM3V3.1
***** general purpose check (Id-Vd) ***
*
*** circuit description ***
m1 2 1 3 0 n1 L=0.6u W=10.0u
vgs 1 0 3.5
vds 2 0 3.5
vss 3 0 0
*
.dc vds 0 3.5 0.05 vgs 0 3.5 0.5
*
.control
run
plot vss#branch
.endc
*
* UCB parameters BSIM3v3.2
.include ../Exam_BSIM3/Modelcards/modelcard.nmos
.include ../Exam_BSIM3/Modelcards/modelcard.pmos
*
.end
"""

##################################################
# @36705

    s21dd = """
.control
run
* white background
set color0=white
* black grid and text (only needed with X11, automatic with MS Win)
set color1=black
* wider grid and plot lines
set xbrushwidth=2
plot vss#branch
.endc
"""

############################################################
#
# 18.2 MS Windows Console
#

############################################################
#
# 18.3
# Linux
#

############################################################
#
# 18.4 CygWin
#

############################################################
#
# 18.5
# Error handling
#

############################################################
#
# 18.6
# Output-to-file options
#

##################################################
# @36774

    s59a0 = """
.control
set svg_intopts = ( 512 384 20 0 1 2 0 )
setcs svg_stropts = ( blue Arial Arial )
.endc
"""

##################################################
# @36809

    s88f7 = """
.control
* simulation commands here
set hcopydevtype = svg
set svg_intopts = ( 512 384 20 0 1 2 0 )
setcs svg_stropts = ( yellow Arial Arial )
set color1=blue
set color2=green
hardcopy plot_1.svg vss#branch title 'Plot no. 4'
+ xlabel 'Drain voltage' ylabel 'Drain current'
* plot to screen commands here
.endc
"""

##################################################
# @36831

    s8600 = """
* for MS Windows only
if $oscompiled = 1 | $oscompiled = 8
  shell Start plot_1.svg
else
* for CYGWIN, Linux
  shell feh --magick-timeout 1  plot_1.svg &
end
"""

##################################################
# @36924

    s6565 = """
.control
* simulation commands here
set gnuplot_terminal=png/quit
gnuplot plot_1 vss#branch vss2#branch
+ title 'Drain current versus drain voltage'
+ xlabel 'Drain voltage / V' ylabel 'Drain current / uA'
* plot to screen commands here
.endc
"""

##################################################
# @36944

    s5783 = """
* for MS Windows only
if $oscompiled = 1 | $oscompiled = 8
  shell Start c:\"program files"\irfanview\i_view64.exe plot_1.png
else
* for CYGWIN, Linux
  shell feh --magick-timeout 1  plot_1.png &
end
"""

##################################################
# @36969

    sbc1a = """
eprvcd 1 2 3 4 5 6 7 8 s0 s1 s2 s3 c3 > adder_x.vcd
"""

##################################################
# @36978

    s0625 = """
* plotting the vcd file (e.g. with GTKWave)
* For Windows: returns control to ngspice
if $oscompiled = 1 | $oscompiled = 8
  shell start gtkwave adder_x.vcd --script nggtk.tcl
else
* for CYGWIN, Linux, others
  shell gtkwave adder_x.vcd --script nggtk.tcl &
end
"""

##################################################
# @36994

    s2c2b = """
# tcl script for gtkwave: show vcd file data created by ngspice
set nfacs [ gtkwave::getNumFacs ]
for {set i 0} {$i < $nfacs } {incr i} {
    set facname [ gtkwave::getFacName $i ]
    set num_added [ gtkwave::addSignalsFromList $facname ]
}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Time/Zoom/Zoom_Full
"""

##################################################
# @37048

    s83b5 = """
* create a new file and write to it
echo new file > nfile.txt
* append line to existing file
echo second line >> nfile.txt
"""

##################################################
# @37066

    s9a52 = """
* variable
setcs myvar=great
set empty=""
* vector
let lineno=1
* empty line
echo
* vectors and variables may be included
echo This is a $myvar output with $&lineno line(s).
* no line feed, empty var to allow blank
echo -n This is still a $myvar output $empty
echo with $&lineno line(s).
"""

##################################################
# @37093

    s3208 = """
print v(1) 3*v(2)
"""

############################################################
#
# 18.7
# Gnuplot
#

##################################################
# @37126

    se86e = """
gnuplot temp vss#branch vss2#branch
+ title 'Drain current versus drain voltage'
+ xlabel 'Drain voltage / V' ylabel 'Drain current / uA'
"""

##################################################
# @37137

    sb45f = """
gnuplot newplot vss#branch vss2#branch
+ title 'Drain current versus drain voltage'
+ xlabel 'Drain voltage / V' ylabel 'Drain current / uA'
"""

############################################################
#
# 18.8
# Integration with CAD software and `third party' GUIs
#

############################################################
#
# Chapter 19
# ngspice as shared library or dynamic link library
#

class NgspiceSharedLibrary(Examples):

############################################################
#
# 19.1
# Compile options
#

############################################################
#
# 19.2 Linking shared ngspice to a calling application
#

############################################################
#
# 19.3 Shared ngspice API
#

##################################################
# @37213

    s4237 = """
typedef struct vector_info {
    char *v_name;           /* Same as so_vname */
    int v_type;             /* Same as so_vtype */
    short v_flags;          /* Flags (a combination of VF_*) */
    double *v_realdata;     /* Real data */
    ngcomplex_t *v_compdata;/* Complex data */
    int v_length;           /* Length of the vector */
} vector_info, *pvector_info;
"""

##################################################
# @37229

    s736d = """
typedef struct vecinfo
{
   int number;       /* number of vector, as position in the
                        linked list of vectors, starts with 0 */
   char *vecname;    /* name of the actual vector */
   bool is_real;     /* TRUE if the actual vector has real data */
   void *pdvec;      /* a void pointer to struct dvec *d, the
                        actual vector */
   void *pdvecscale; /* a void pointer to struct dvec *ds,
                        the scale vector */
} vecinfo, *pvecinfo;
"""

##################################################
# @37246

    se04b = """
typedef struct vecinfoall
{
    /* the plot */
    char *name;
    char *title;
    char *date;
    char *type;
    int veccount;

    /* the data as an array of vecinfo with
       length equal to the number of vectors
       in the plot */
    pvecinfo *vecs;

} vecinfoall, *pvecinfoall;
"""

##################################################
# @37270

    s87de = """
typedef struct vecvalues {
    char* name;      /* name of a specific vector */
    double creal;    /* actual data value */
    double cimag;    /* actual data value */
    NG_BOOL is_scale;   /* if 'name' is the scale vector */
    NG_BOOL is_complex; /* if the data are complex numbers */
} vecvalues, *pvecvalues;
"""

##################################################
# @37285

    s88f8 = """
typedef struct vecvaluesall {
    int veccount;      /* number of vectors in plot */
    int vecindex;      /* index of actual set of vectors, i.e.
                          the number of accepted data points */
    pvecvalues *vecsa; /* values of actual set of vectors,
                          indexed from 0 to veccount - 1 */
} vecvaluesall, *pvecvaluesall;
"""

############################################################
#
# 19.4 General remarks on using the API
#

##################################################
# @37492

    s2fdf = """
ngSpice_Command("source ../examples/adder_mos.cir");
"""

##################################################
# @37501

    s7d3b = """
ngSpice_Command("circbyline fail test");
ngSpice_Command("circbyline V1 1 0 1");
ngSpice_Command("circbyline R1 1 0 1");
ngSpice_Command("circbyline .dc V1 0 1 0.1");
ngSpice_Command("circbyline .end");
"""

##################################################
# @37514

    sbe6c = """
circarray = (char**)malloc(sizeof(char*) * 7);
circarray[0] = strdup("test array");
circarray[1] = strdup("V1 1 0 1");
circarray[2] = strdup("R1 1 2 1");
circarray[3] = strdup("C1 2 0 1 ic=0");
circarray[4] = strdup(".tran 10u 3 uic");
circarray[5] = strdup(".end");
circarray[6] = NULL;
ngSpice_Circ(circarray);
"""

##################################################
# @37545

    sca6b = """
ngSpice_Command("bg_run");
...
ngSpice_Command("bg_halt");
...
ngSpice_Command("bg_resume");
"""

##################################################
# @37582

    sc498 = """
ngSpice_Command("write testout.raw V(2)");
ngSpice_Command("print V(2)");
"""

############################################################
#
# 19.5
# Example applications
#

############################################################
#
# 19.6
# ngspice parallel
#

####################################################################################################
#
# Chapter 20
# TCLspice
#

class TCLspice(Examples):

############################################################
#
# 20.1 tclspice framework
#

############################################################
#
# 20.2 tclspice documentation
#

############################################################
#
# 20.3 spicetoblt
#

##################################################
# @37721

    s8b31 = """
blt::vector create Iex
spice::vectoblt Vex#branch Iex
"""

############################################################
#
# 20.4 Running TCLspice
#

##################################################
# @37734

    s5def = """
load /somepath/libspice.so
package require spice
"""

##################################################
# @37743

    s0fa4 = """
spice::source testCapa.cir
spice::spicetoblt example...
"""

##################################################
# @37752

    sfa84 = """
blt::graph .cimvd -title "Cim = f(Vd)"
pack .cimvd
.cimvd element create line1 -xdata Vcmd -ydata Cim
"""

############################################################
#
# 20.5 examples
#

##################################################
# @37819

    s39a5 = """
package require spice
"""

##################################################
# @37827

    s5fe9 = """
# Test of virtual capacitor circuit
# Vary the control voltage and log the resulting capacitance
"""

##################################################
# @37836

    sceac = """
spice::source "testCapa.cir"
"""

##################################################
# @37844

    s46a3 = """
set n 30 set dv 0.2
set vmax [expr $dv/2]
set vmin [expr -1 * $dv/2]
set pas [expr $dv/ $n]
"""

##################################################
# @37855

    sc73e = """
blt::vector create Ctmp
blt::vector create Cim
blt::vector create check
blt::vector create Vcmd
"""

##################################################
# @37866

    se8c6 = """
blt::graph .cimvd -title "Cim = f(Vd)"
blt::graph .checkvd -title "Rim = f(Vd)"
blt::vector create Iex
blt::vector create freq
blt::graph .freqanal -title "Analyse frequentielle"
#
# First simulation: A simple AC plot
#
set v [expr {$vmin + $n * $pas / 4}]
spice::alter vd = $v
spice::op
spice::ac dec 10 100 100k
"""

##################################################
# @37885

    sba75 = """
spice::vectoblt {Vex#branch} Iex
"""

##################################################
# @37893

    sba2d = """
spice::vectoblt {frequency} freq
"""

##################################################
# @37901

    s773d = """
pack .freqanal
"""

##################################################
# @37909

    s79a4 = """
.freqanal element create line1 -xdata freq -ydata Iex
#
# Second simulation: Capacitance versus voltage control
# for {set i 0} {[expr $n - $i]} {incr i }
#     { set v [expr {$vmin + $i * $pas}]
spice::alter vd = $v
spice::op spice::ac dec 10 100 100k
"""

##################################################
# @37923

    sd037 = """
spice::let Cim = real(mean(Vex#branch/(2*Pi*i*frequency*(V(5)-V(6)))))
spice::vectoblt Cim Ctmp
"""

##################################################
# @37932

    s604d = """
Cim append $Ctmp(0:end)
"""

##################################################
# @37940

    s0805 = """
spice::let err = real(mean(sqrt((Vex#branch-
        (2*Pi*i*frequency*Cim*V(5)-V(6)))^2)))
spice::vectoblt err Ctmp check
append $Ctmp(0:end)
"""

##################################################
# @37951

    sda0a = """
FALTA ALGO... Vcmd append $v }
"""

##################################################
# @37959

    s6758 = """
pack .cimvd
.cimvd element create line1 -xdata Vcmd -ydata Cim
pack .checkvd
.checkvd element create line1 -xdata Vcmd -ydata check
"""

##################################################
# @37975

    s384e = """
./testbench3.tcl
"""

##################################################
# @37992

    sdd3c = """
#!/bin/sh
# WishFix \
exec wish "$0" ${1+"$@"}
#
#
#
"""

##################################################
# @38013

    sd843 = """
source differentiate.tcl
"""

##################################################
# @38021

    sb4f1 = """
proc temperatures_calc {temp_inf temp_sup points} {
set tstep [ expr " ( $temp_sup - $temp_inf ) / $points " ]
set t $temp_inf
set temperatures ""
for { set i 0 } { $i < $points } { incr i } {
    set t [ expr { $t + $tstep } ]
    set temperatures "$temperatures $t"
}
return $temperatures }
"""

##################################################
# @38037

    s9e12 = """
proc thermistance_calc { res B points } {
set tzero 273.15
set tref 25
set thermistance ""
foreach t $points {
        set res_temp [expr " $res *
+       exp ( $B * ( 1 / ($tzero + $t) -
+       1 / ( $tzero + $tref ) ) ) " ]
        set thermistance "$thermistance $res_temp"
}
return $thermistance }
"""

##################################################
# @38055

    sd6d1 = """
proc tref_calc { points } {
set tref ""
foreach t $points {
    set tref "$tref[expr "6*(2.275-0.005*($t-20))-9"]"
}
return $tref }
"""

##################################################
# @38068

    secd9 = """
### NOTE:
### As component values are modified by a spice::alter
### Component values can be considered as global variable.
### R10 and R12 are not passed to iteration function
### because it is expected to be correct, i.e. to
### have been modified soon before
proc iteration { t } { set tzero 273.15 spice::alter
   r11 = [ thermistance_calc 10000 3900 $t ]
# Temperature simulation often crashes. Comment it out...
#spice::set temp = [ expr " $tzero + $t " ]
spice::op
spice::vectoblt vref_temp tref_tmp
### NOTE:
### As the library is executed once for the
### whole script execution, it is important to manage the memory
### and regularly destroy unused data set. The data
### computed here will not be reused. Clean it
spice::destroy all return [ tref_tmp range 0 0 ] }
"""

##################################################
# @38093

    s249d = """
proc cost { r10 r12 } {
tref_blt length 0
spice::alter r10 = $r10
spice::alter r12 = $r12
foreach point [ temperatures_blt range 0
+       [ expr " [temperatures_blt length ] - 1" ] ] {
+       tref_blt append [ iteration $point ]
}
set result [ blt::vector expr " 1000 *
        sum(( tref_blt - expected_blt )^2 )" ]
disp_curve $r10 $r12
return $result }
"""

##################################################
# @38112

    s7be1 = """
proc disp_curve { r10 r12 }
+  { .g configure -title "Valeurs optimales: R10 = $r10 R12 = $r12" }
"""

##################################################
# @38121

    s700a = """
#
# Optimization
# blt::vector create tref_tmp
blt::vector create tref_blt
blt::vector create expected_blt
blt::vector create temperatures_blt temperatures_blt
append [ temperatures_calc -25 75 30 ] expected_blt
append [ tref_calc [temperatures_blt range 0
+      [ expr " [ temperatures_blt length ] - 1" ] ] ]
blt::graph .g
pack .g -side top -fill both -expand true
.g element create real -pixels 4 -xdata temperatures_blt
+       -ydata tref_blt
.g element create expected -fill red -pixels 0 -dashes
+       dot -xdata temperatures_blt -ydata expected_blt
"""

##################################################
# @38143

    s0e64 = """
spice::source FB14.cir
set r10r12 [ ::math::optimize::minimumSteepestDescent
+            cost { 10000 10000 } 0.1 50 ]
regexp {([0-9.]*) ([0-9.]*)} $r10r12 r10r12 r10 r12
"""

##################################################
# @38154

    s7ac5 = """
#
# Results
# spice::alter r10 = $r10
spice::alter r12 = $r12
foreach point [ temperatures_blt range 0
+   [ expr " [temperatures_blt length ] - 1" ] ] {
        tref_blt append [ iteration $point ]
}
disp_curve $r10 $r12
"""

##################################################
# @38170

    s6bab = """
#!/bin/sh
# WishFix \
  exec wish -f "$0" ${1+"$@"}
###
package require BLT package require spice
"""

##################################################
# @38182

    sae28 = """
namespace import blt::*
wm title . "Vector Test script"
wm geometry . 800x600+40+40 pack propagate . false
"""

##################################################
# @38192

    s87fd = """
stripchart .chart
pack .chart -side top -fill both -expand true
.chart axis configure x -title "Time" spice::source example.cir
spice::bg
run after 1000 vector
create a0 vector
create b0 vectorry
create a1 vector
create b1 vector
create stime
proc bltupdate {} {
puts [spice::spice_data]
spice::spicetoblt a0 a0
spice::spicetoblt b0 b0
spice::spicetoblt a1 a1
spice::spicetoblt b1 b1
spice::spicetoblt time stime
after 100 bltupdate }
bltupdate .chart element create a0 -color red -xdata
+       stime -ydata a0
.chart element create b0 -color blue -xdata stime -ydata b0
.chart element create a1 -color yellow -xdata stime -ydata a1
.chart element create b1 -color black -xdata stime -ydata b1
"""

############################################################
#
# 20.6
# Compiling
#

############################################################
#
# 20.7 MS Windows 32 Bit binaries
#

####################################################################################################
#
# Chapter 21
# Example Circuits
#

class ExampleCircuits1(Examples):

############################################################
#
# 21.1
# AC coupled transistor amplifier
#

##################################################
# @38301

    Ea724 = """
*s* A Berkeley SPICE3 compatible circuit
*
* This circuit contains only Berkeley SPICE3 components.
*
* The circuit is an AC coupled transistor amplifier with
* a sinewave input at node "1", a gain of approximately -3.9,
* and output on node "coll".
*
.tran 1e-5 2e-3
*
vcc vcc 0 12.0
vin 1 0 0.0 ac 1.0 sin(0 1 1k)
ccouple 1 base 10uF
rbias1 vcc base 100k
rbias2 base 0 24k
q1 coll base emit generic
rcollector vcc coll 3.9k
remitter emit 0 1k
*
.model generic npn
*
.end
"""

############################################################
#
# 21.2
# Differential Pair
#

##################################################
# @38457

    Ea426 = """
*s* SIMPLE DIFFERENTIAL PAIR
VCC 7 0 12
VEE 8 0 -12
VIN 1 0 AC 1
RS1 1 2 1K
RS2 6 0 1K
Q1 3 2 4 MOD1
Q2 5 6 4 MOD1
RC1 7 3 10K
RC2 7 5 10K
RE 4 8 10K
.MODEL MOD1 NPN BF=50 VAF=50 IS=1.E-12 RB=100 CJC=.5PF TF=.6NS
.TF V(5) VIN
.AC DEC 10 1 100MEG
.END
"""

############################################################
#
# 21.3
# MOSFET Characterization
#

##################################################
# @38481

    E4961 = """
*s* MOS OUTPUT CHARACTERISTICS
.OPTIONS NODE NOPAGE
VDS 3 0
VGS 2 0
M1 1 2 0 0 MOD1 L=4U W=6U AD=10P AS=10P
* VIDS MEASURES ID, WE COULD HAVE USED VDS,
* BUT ID WOULD BE NEGATIVE
VIDS 3 1
.MODEL MOD1 NMOS VTO=-2 NSUB=1.0E15 UO=550
.DC VDS 0 10 .5 VGS 0 5 1
.END
"""

############################################################
#
# 21.4 RTL Inverter
#

##################################################
# @38500

    Ed09d = """
*s* SIMPLE RTL INVERTER
VCC 4 0 5
VIN 1 0 PULSE 0 5 2NS 2NS 2NS 30NS
RB 1 2 10K
Q1 3 2 0 Q1
RC 3 4 1K
.MODEL Q1 NPN BF 20 RB 100 TF .1NS CJC 2PF
.DC VIN 0 5 0.1
.TRAN 1NS 100NS
.END
"""

############################################################
#
# 21.5 Four-Bit Binary Adder (Bipolar)
#

##################################################
# @38518

    Ebf52 = """
*s* ADDER - 4 BIT ALL-NAND-GATE BINARY ADDER
*** SUBCIRCUIT DEFINITIONS
.SUBCKT NAND 1 2 3 4
* NODES: INPUT(2), OUTPUT, VCC
Q1 9 5 1 QMOD
D1CLAMP 0 1 DMOD
Q2 9 5 2 QMOD
D2CLAMP 0 2 DMOD
RB 4 5 4K
R1 4 6 1.6K
Q3 6 9 8 QMOD
R2 8 0 1K
RC 4 7 130
Q4 7 6 10 QMOD
DVBEDROP 10 3 DMOD
Q5 3 8 0 QMOD
.ENDS NAND
"""

##################################################
# @38541

    Eead9 = """
.SUBCKT ONEBIT 1 2 3 4 5 6
* NODES: INPUT(2), CARRY-IN, OUTPUT, CARRY-OUT, VCC
X1 1 2 7 6 NAND
X2 1 7 8 6 NAND
X3 2 7 9 6 NAND
X4 8 9 10 6 NAND
X5 3 10 11 6 NAND
X6 3 11 12 6 NAND
X7 10 11 13 6 NAND
X8 12 13 4 6 NAND
X9 11 7 5 6 NAND
.ENDS ONEBIT

.SUBCKT TWOBIT 1 2 3 4 5 6 7 8 9
* NODES: INPUT - BIT0(2) / BIT1(2), OUTPUT - BIT0 / BIT1,
* CARRY-IN, CARRY-OUT, VCC
X1 1 2 7 5 10 9 ONEBIT
X2 3 4 10 6 8 9 ONEBIT
.ENDS TWOBIT

.SUBCKT FOURBIT 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
* NODES: INPUT - BIT0(2) / BIT1(2) / BIT2(2) / BIT3(2),
* OUTPUT - BIT0 / BIT1 / BIT2 / BIT3, CARRY-IN, CARRY-OUT, VCC
X1 1 2 3 4 9 10 13 16 15 TWOBIT
X2 5 6 7 8 11 12 16 14 15 TWOBIT
.ENDS FOURBIT

*** DEFINE NOMINAL CIRCUIT
.MODEL DMOD D
.MODEL QMOD NPN(BF=75 RB=100 CJE=1PF CJC=3PF)
VCC 99 0 DC 5V
VIN1A 1 0 PULSE(0 3 0 10NS 10NS 10NS 50NS)
VIN1B 2 0 PULSE(0 3 0 10NS 10NS 20NS 100NS)
VIN2A 3 0 PULSE(0 3 0 10NS 10NS 40NS 200NS)
VIN2B 4 0 PULSE(0 3 0 10NS 10NS 80NS 400NS)
VIN3A 5 0 PULSE(0 3 0 10NS 10NS 160NS 800NS)
VIN3B 6 0 PULSE(0 3 0 10NS 10NS 320NS 1600NS)
VIN4A 7 0 PULSE(0 3 0 10NS 10NS 640NS 3200NS)
VIN4B 8 0 PULSE(0 3 0 10NS 10NS 1280NS 6400NS)
X1 1 2 3 4 5 6 7 8 9 10 11 12 0 13 99 FOURBIT
RBIT0 9 0 1K
RBIT1 10 0 1K
RBIT2 11 0 1K
RBIT3 12 0 1K
RCOUT 13 0 1K

*** (FOR THOSE WITH MONEY (AND MEMORY) TO BURN)
.TRAN 1NS 6400NS
.END
"""

############################################################
#
# 21.6
# Four-Bit Binary Adder (MOS)
#

##################################################
# @38599

    Ee066 = """
*s* ADDER - 4 BIT ALL-NAND-GATE BINARY ADDER
*** SUBCIRCUIT DEFINITIONS
.SUBCKT NAND in1 in2 out VDD
* NODES:  INPUT(2), OUTPUT, VCC
M1 out in2 Vdd Vdd p1 W=7.5u L=0.35u pd=13.5u ad=22.5p
+  ps=13.5u as=22.5p
M2 net.1 in2 0 0 n1   W=3u   L=0.35u pd=9u    ad=9p
+  ps=9u    as=9p
M3 out in1 Vdd Vdd p1 W=7.5u L=0.35u pd=13.5u ad=22.5p
+  ps=13.5u as=22.5p
M4 out in1 net.1 0 n1 W=3u   L=0.35u pd=9u    ad=9p
+  ps=9u    as=9p
.ENDS NAND
.SUBCKT ONEBIT 1 2 3 4 5 6 AND
X2   1  7  8  6   NAND
X3   2  7  9  6   NAND
X4   8  9 10  6   NAND
X5   3 10 11  6   NAND
X6   3 11 12  6   NAND
X7  10 11 13  6   NAND
X8  12 13  4  6   NAND
X9  11  7  5  6   NAND
.ENDS ONEBIT
.SUBCKT TWOBIT 1 2 3 4 5 6 7 8 9
* NODES:  INPUT - BIT0(2) / BIT1(2), OUTPUT - BIT0 / BIT1,
*         CARRY-IN, CARRY-OUT, VCC
X1   1  2  7  5 10  9   ONEBIT
X2   3  4 10  6  8  9   ONEBIT
.ENDS TWOBIT
.SUBCKT FOURBIT 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
*NODES: INPUT - BIT0(2) / BIT1(2) / BIT2(2) / BIT3(2),
*       OUTPUT - BIT0 / BIT1 / BIT2 / BIT3, CARRY-IN,
*       CARRY-OUT, VCC
X1   1  2  3  4  9 10 13 16 15   TWOBIT
X2   5  6  7  8 11 12 16 14 15   TWOBIT
.ENDS FOURBIT
"""

##################################################
# @38641

    Ed072 = """
*s* POWER
VCC   99  0   DC 3.3V
*** INPUTS
VIN1A  1  0   DC 0 PULSE(0 3 0 5NS 5NS   20NS   50NS)
VIN1B  2  0   DC 0 PULSE(0 3 0 5NS 5NS   30NS  100NS)
VIN2A  3  0   DC 0 PULSE(0 3 0 5NS 5NS   50NS  200NS)
VIN2B  4  0   DC 0 PULSE(0 3 0 5NS 5NS   90NS  400NS)
VIN3A  5  0   DC 0 PULSE(0 3 0 5NS 5NS  170NS  800NS)
VIN3B  6  0   DC 0 PULSE(0 3 0 5NS 5NS  330NS 1600NS)
VIN4A  7  0   DC 0 PULSE(0 3 0 5NS 5NS  650NS 3200NS)
VIN4B  8  0   DC 0 PULSE(0 3 0 5NS 5NS 1290NS 6400NS)
*** DEFINE NOMINAL CIRCUIT
X1     1  2  3  4  5  6  7  8  9 10 11 12  0 13 99 FOURBIT

.option acct
.save V(1) V(2) V(3) V(4) V(5) V(6) V(7) V(8) $ INPUTS
.save V(9) V(10) V(11) V(12) V(13) $ OUTPUTS

.TRAN 1NS 6400NS

* use BSIM3 model with default parameters
.model n1 nmos level=49 version=3.3.0
.model p1 pmos level=49 version=3.3.0

.END
"""

############################################################
#
# 21.7
# Transmission-Line Inverter
#

##################################################
# @38675

    E9f54 = """
*s* Transmission-line inverter

v1 1 0 pulse(0 1 0 0.1n)
r1 1 2 50
x1 2 0 0 4 tline
r2 4 0 50

.subckt tline 1 2 3 4
t1 1 2 3 4 z0=50 td=1.5ns
t2 2 0 4 0 z0=100 td=1ns
.ends tline

.tran 0.1ns 20ns
.end
"""

####################################################################################################
#
# Chapter 22
# Statistical circuit analysis
#

class StatisticalCircuitAnalysis(Examples):

############################################################
#
# 22.1 Introduction
#

############################################################
#
# 22.2
# Using random param(eters)
#

##################################################
# @38756

    Eb4ad = """
* random number tests
.param aga = agauss(1,2,3)
.param aga2='2*aga'
.param lim=limit(0,1.2)
.func rgauss(a,b,c) '5*agauss(a,b,c)'
* always same value as defined above
v1 1 0  'lim'
v2 2 0  'lim'
* may be a different value
v3 3 0  'limit(0,1.2)'
* always new random values
v11 11 0 'agauss(1,2,3)'
v12 12 0 'agauss(1,2,3)'
v13 13 0 'agauss(1,2,3)'
* same value as defined above
v14 14 0 'aga'
v15 15 0 'aga'
v16 16 0 'aga2'
* using .func, new random values
v17 17 0 'rgauss(0,2,3)'
v18 18 0 'rgauss(0,2,3)'
.op
.control
run
print v(1) v(2) v(3) v(11) v(12) v(13)
print v(14) v(15) v(16) v(17) v(18)
.endc
.end
"""

############################################################
#
# 22.3
# Behavioral sources (B, E, G, R, L, C) with random control
#

##################################################
# @38801

    E6723 = """
* random resistor
.param res = 10k
.param ttime=12000m
.param varia=100
.param ttime10 = 'ttime/varia'
* random control voltage (Gaussian distribution)
VR2 r2  0 dc 0 trrandom (2 'ttime10' 0 1)
* behavioral resistor
R2 4 6  R = 'res + 0.033 * res*V(r2)'
"""

############################################################
#
# 22.4 ngspice scripting language
#

############################################################
#
# 22.5
# Monte-Carlo Simulation
#

##################################################
# @38875

    E5aa8 = """
*s* Perform Monte Carlo simulation in ngspice
V1 N001 0 AC 1 DC 0
R1 N002 N001 141
*
C1 OUT 0 1e-09
L1 OUT 0 10e-06
C2 N002 0 1e-09
L2 N002 0 10e-06
L3 N003 N002 40e-06
C3 OUT N003 250e-12
*
R2 0 OUT 141
*
.control
*s*   let mc_runs = 100
*s*   let run = 1
*s*   set curplot = new       $ create a new plot
*s*   set scratch = $curplot  $ store its name to 'scratch'
*s* *
*s*   define unif(nom, var) (nom + nom*var * sunif(0))
*s*   define aunif(nom, avar) (nom + avar * sunif(0))
*s*   define gauss(nom, var, sig) (nom + nom*var/sig * sgauss(0))
*s*   define agauss(nom, avar, sig) (nom + avar/sig * sgauss(0))
*s* *
*s*   dowhile run <= mc_runs
*s* *   alter c1 = unif(1e-09, 0.1)
*s* *   alter l1 = aunif(10e-06, 2e-06)
*s* *   alter c2 = aunif(1e-09, 100e-12)
*s* *   alter l2 = unif(10e-06, 0.2)
*s* *   alter l3 = aunif(40e-06, 8e-06)
*s* *   alter c3 = unif(250e-12, 0.15)
*s*     alter c1 = gauss(1e-09, 0.1, 3)
*s*     alter l1 = agauss(10e-06, 2e-06, 3)
*s*     alter c2 = agauss(1e-09, 100e-12, 3)
*s*     alter l2 = gauss(10e-06, 0.2, 3)
*s*     alter l3 = agauss(40e-06, 8e-06, 3)
*s*     alter c3 = gauss(250e-12, 0.15, 3)
*s*     ac oct 100 250K 10Meg
*s*     set run ="$&run"     $ create a variable from the vector
*s*     set dt = $curplot    $ store the current plot to dt
*s*     setplot $scratch     $ make 'scratch' the active plot
*s* * store the output vector to plot 'scratch'
*s*     let vout{$run}={$dt}.v(out)
*s*     setplot $dt          $ go back to the previous plot
*s*     let run = run + 1
*s*   end
*s*   plot db({$scratch}.all)
.endc

.end
"""

############################################################
#
# 22.6
# Data evaluation with Gnuplot
#

##################################################
# @38967

    sedb4 = """
 # This file: pl-v4mag.p
 # ngspice file OpWien.sp
 # ngspice command:
 #  gnuplot pl4mag v4mag xlimit 500 1500
 # a gnuplot manual:
 # http://www.duke.edu/~hpgavin/gnuplot.html

 # Gauss function to be fitted
 f1(x)=(c1/(a1*sqrt(2*3.14159))*exp(-((x-b1)**2)/(2*a1**2)))
 # Gauss function to plot start graph
 f2(x)=(c2/(a2*sqrt(2*3.14159))*exp(-((x-b2)**2)/(2*a2**2)))
 # start values
 a1=50 ; b1=900 ; c1=50
 # keep start values in  a2, b2, c2
 a2=a1  b2=b1 ; c2=c1
 # curve fitting
 fit f1(x) 'pl4mag.data' using 1:2 via a1, b1, c1
 # plot original and fitted curves with new a1, b1, c1
 plot "pl4mag.data" using 1:2 with lines, f1(x), f2(x)
"""

####################################################################################################
#
# Chapter 23 Circuit optimization with ngspice
#

class CircuitOptimization(Examples):
    pass

############################################################
#
# Part II
# XSPICE Software User's Manual
#

####################################################################################################
#
# Chapter 25 XSPICE Basics
#

class XspiceBasics(Examples):
    pass

############################################################
#
# 25.1
# ngspice with the XSPICE option
#

############################################################
#
# 25.2 The XSPICE Code Model Subsystem
#

############################################################
#
# 25.3 XSPICE Top-Level Diagram
#

####################################################################################################
#
# Chapter 26
# Execution Procedures
#

class ExecutionProcedures(Examples):

############################################################
#
# 26.1 Simulation and Modeling Overview
#

##################################################
# @39404

    E5682 = """
*s* Small Signal Amplifier
*
* This circuit simulates a simple small signal amplifier.
*
Vin          Input 0                    0 SIN(0 .1 500Hz)
R_source     Input Amp_In               100
C1           Amp_In 0                   1uF
R_Amp_Input  Amp_In 0                   1MEG
E1           (Amp_Out 0) (Amp_In 0)    -10
R_Load       Amp_Out 0                  1000

.Tran 1.0u 0.01
.end
"""

##################################################
# @39466

    E73da = """
Small Signal Amplifier with Limit Diodes
*
* This circuit simulates a small signal amplifier
* with a diode limiter.
*
.dc Vin -1 1 .05

Vin       Input 0 DC            0
R_source  Input Amp_In        100
D_Neg     0 Amp_In            1n4148
D_Pos     Amp_In 0            1n4148
C1        Amp_In 0            1uF
X1        Amp_In 0 Amp_Out    Amplifier
R_Load    Amp_Out 0           1000

.model 1n4148 D (is=2.495e-09 rs=4.755e-01 n=1.679e+00
+ tt=3.030e-09 cjo=1.700e-12 vj=1 m=1.959e-01 bv=1.000e+02
+ ibv=1.000e-04)

.subckt Amplifier Input Common Output
E1        (Output Common) (Input Common) -10
R_Input   Input           Common 1meg
.ends Amplifier

.end
"""

##################################################
# @39513

    E834b = """
.model 1n4148 D (is=2.495e-09 rs=4.755e-01 n=1.679e+00
+ tt=3.030e-09 cjo=1.700e-12 vj=1 m=1.959e-01
+ bv=1.000e+02 ibv=1.000e-04)
"""

##################################################
# @39527

    Ed340 = """
X1 Amp_In 0 Amp_Out
"""

##################################################
# @39535

    F7fa3 = """
.subckt <Name> <Node1> <Node2> <Node3> ...
"""

##################################################
# @39543

    F74ae = """
.ends <Name>
"""

##################################################
# @39553

    E9e63 = """
*s* Small Signal Amplifier
*
* This circuit simulates a small signal amplifier
* with a diode limiter.
*
.dc Vin -1 1 .05

Vin       Input 0             DC 0
R_source  Input Amp_In        100
D_Neg 0   Amp_In              1n4148
D_Pos     Amp_In 0            1n4148
C1        Amp_In 0            1uF
A1        Amp_In 0 Amp_Out    Amplifier
R_Load    Amp_Out 0           1000

.model 1n4148 D (is=2.495e-09 rs=4.755e-01 n=1.679e+00
+ tt=3.030e-09 cjo=1.700e-12 vj=1 m=1.959e-01 bv=1.000e+02
+ ibv=1.000e-04)

.model Amplifier Amp (gain = -10 in_offset = 1e-3
+                     rin = 1meg rout = 0.4)
.end
"""

############################################################
#
# 26.2 Circuit Description Syntax
#

##################################################
# @39604

    Eb87c = """
*s* Supply ramping option
*
* This circuit demonstrates the use of the option
* "ramptime" that ramps independent sources and the
* capacitor and inductor initial conditions from
* zero to their final value during the time period
* specified.
*
*
.tran 0.1 5
.option ramptime=0.2
* a1 1 0 cap
.model cap capacitor (c=1000uf ic=1)
r1 1 0 1k
*
a2 2 0 ind
.model ind inductor (l=1H ic=1)
r2 2 0 1.0
*
v1 3 0 1.0
r3 3 0 1k
*
i1 4 0 1e-3
r4 4 0 1k
*
v2 5 0 0.0 sin(0 1 0.3 0 0 45.0)
r5 5 0 1k
*
.end
"""

############################################################
#
# 26.3
# How to create code models
#

##################################################
# @39675

    E5109 = """
*s* Code Model Test: new xxor
*
*** analysis type ***
.tran .01s 4s
*
*** input sources ***
*
v2 200 0 DC PWL( (0 0.0) (2 0.0) (2.0000000001 1.0) (3 1.0) )
*
v1 100 0 DC PWL( (0 0.0) (1.0 0.0) (1.0000000001 1.0) (2 1.0)
+     (2.0000000001 0.0) (3 0.0) (3.0000000001 1.0) (4 1.0) )
*
*** resistors to ground ***
r1 100 0 1k
r2 200 0 1k
*
*** adc_bridge blocks ***
aconverter [200 100] [2 1] adc_bridge1
.model adc_bridge1 adc_bridge (in_low=0.1 in_high=0.9
+                  rise_delay=1.0e-12 fall_delay=1.0e-12)
*
*** xor block ***
a7 [1 2] 70 d_xor1
.model d_xor1 d_xxor (rise_delay=1.0e-6 fall_delay=2.0e-6
+                    input_load=1.0e-12)
*
*** dac_bridge blocks ****
abridge1 [70] [out] dac1
.model dac1 dac_bridge(out_low = 0.7 out_high = 3.5
+ out_undef = 2.2 input_load = 5.0e-12 t_rise = 50e-9
+ t_fall = 20e-9)
*
*** simulation and plotting ***
.control
run
plot allv
.endc
*
.end
"""

####################################################################################################
#
# Chapter 27 Example circuits
#

class ExampleCircuits2(Examples):

############################################################
#
# 27.1 Amplifier with XSPICE model `gain'
#

##################################################
# @39742

    Ee350 = """
*s* A transistor amplifier circuit
*
.tran 1e-5 2e-3
*
vin 1 0 0.0 ac 1.0 sin(0 1 1k)
*
ccouple 1 in 10uF
rzin in 0 19.35k
*
aamp in aout gain_block
.model gain_block gain (gain = -3.9 out_offset = 7.003)
*
rzout aout coll 3.9k
rbig coll 0 1e12
*
.end
"""

############################################################
#
# 27.2 XSPICE advanced usage
#

##################################################
# @39807

    E0dd0 = """
*s* Mixed IO types
* This circuit contains a mixture of IO types, including
* analog, digital, user-defined (real), and 'null'.
*
* The circuit demonstrates the use of the digital and
* user-defined node capability to model system-level designs
* such as sampled-data filters. The simulated circuit
* contains a digital oscillator enabled after 100us. The
* square wave oscillator output is divided by 8 with a
* ripple counter. The result is passed through a digital
* filter to convert it to a sine wave.
*
.tran 1e-5 1e-3
*
v1 1 0 0.0 pulse(0 1 1e-4 1e-6)
r1 1 0 1k
*
abridge1 [1] [enable] atod
.model atod adc_bridge
*
aclk [enable clk] clk nand
.model nand d_nand (rise_delay=1e-5 fall_delay=1e-5)
*
adiv2 div2_out clk NULL NULL NULL div2_out dff
adiv4 div4_out div2_out NULL NULL NULL div4_out dff
adiv8 div8_out div4_out NULL NULL NULL div8_out dff
.model dff d_dff
"""

##################################################
# @39840

    Ee1d3 = """
abridge2 div8_out enable filt_in node_bridge2
.model node_bridge2 d_to_real (zero=-1 one=1)
*
xfilter filt_in clk filt_out dig_filter
*
abridge3 filt_out a_out node_bridge3
.model node_bridge3 real_to_v
*
rlpf1 a_out oa_minus 10k
*
xlpf 0 oa_minus lpf_out opamp
*
rlpf2 oa_minus lpf_out 10k
clpf lpf_out oa_minus 0.01uF
***************************************
.subckt dig_filter filt_in clk filt_out
.model n0 real_gain (gain=1.0)
.model n1 real_gain (gain=2.0)
.model n2 real_gain (gain=1.0)
.model g1 real_gain (gain=0.125)
.model zm1 real_delay
.model d0a real_gain (gain=-0.75)
.model d1a real_gain (gain=0.5625)
.model d0b real_gain (gain=-0.3438)
.model d1b real_gain (gain=1.0)
*
an0a filt_in x0a n0
an1a filt_in x1a n1
an2a filt_in x2a n2
*
az0a x0a clk x1a zm1
az1a x1a clk x2a zm1
*
ad0a x2a x0a d0a
ad1a x2a x1a d1a
*
az2a x2a filt1_out g1
az3a filt1_out clk filt2_in zm1
*
an0b filt2_in x0b n0
an1b filt2_in x1b n1
an2b filt2_in x2b n2
*
az0b x0b clk x1b zm1
az1b x1b clk x2b zm1
*
ad0 x2b x0b d0b
ad1 x2b x1b d1b
*
az2b x2b clk filt_out zm1
.ends dig_filter
"""

##################################################
# @39897

    E8987 = """
.subckt opamp plus minus out
*
r1 plus minus 300k
a1 %vd (plus minus) outint lim
.model lim limit (out_lower_limit = -12 out_upper_limit = 12
+ fraction = true limit_range = 0.2 gain=300e3)
r3 outint out 50.0
r2 out 0 1e12
*
.ends opamp
*
.end
"""

####################################################################################################
#
# Chapter 28
# Code Models and User-Defined Nodes
#

class CodeModels(Examples):

############################################################
#
# 28.1 Code Model Data Type Definitions
#

############################################################
#
# 28.2
# Creating Code Models
#

############################################################
#
# 28.3
# Creating User-Defined Nodes
#

############################################################
#
# 28.4
# Adding a new code model library
#

############################################################
#
# 28.5
# Compiling and loading the new code model (library)
#

############################################################
#
# 28.6
# Interface Specification File
#

##################################################
# @40373

    s79b3 = """
/* Define local pointer variable */
double *local.x;

/* Allocate storage to be referenced by the static variable x. */
/* Do this only if this is the initial call of the code model. */
if (INIT == TRUE) {
    STATIC_VAR(x) = calloc(size, sizeof(double));
}

/* Assign the value from the static pointer value to the local */
/* pointer variable. */
local_x = STATIC_VAR(x);

/* Assign values to first two members of the array */
local_x[0] = 1.234;
local_x[1] = 5.678;
"""

############################################################
#
# 28.7
# Model Definition File
#

##################################################
# @40397

    s21f0 = """
void code.model(ARGS) /* private structure accessed by
                         accessor macros              */
{
/* The following code fragments are intended to show how
   information in the argument list is accessed. The reader
   should not attempt to relate one fragment to another.
   Consider each fragment as a separate example.
*/

   double p,/* variable for use in the following code fragments */
       x,   /* variable for use in the following code fragments */
       y;   /* variable for use in the following code fragments */


   int i,   /* indexing variable for use in the following */
       j;   /* indexing variable for use in the following */

   UDN_Example_Type *a_ptr, /* A pointer used to access a
                                User-Defined Node type */
                    *y_ptr; /* A pointer used to access a
                                User-Defined Node type */

   /* Initializing and outputting a User-Defined Node result */
   if(INIT) {
      OUTPUT(y) = malloc(sizeof(user.defined.struct));
      y_ptr = OUTPUT(y);
      y_ptr->component1 = 0.0;
      y_ptr->component2 = 0.0;
   }
   else {
      y_ptr = OUTPUT(y);
      y_ptr->component1 = x1;
      y_ptr->component2 = x2;
   }

   /* Determining analysis type */
   if(ANALYSIS == AC) {
       /* Perform AC analysis-dependent operations here */
   }

   /* Accessing a parameter value from the .model card */
   p = PARAM(gain);

   /* Accessing a vector parameter from the .model card */
   for(i = 0; i < PARAM_SIZE(in_offset); i++)
      p = PARAM(in_offset[i]);

   /* Accessing the value of a simple real-valued input */
   x = INPUT(a);

   /* Accessing a vector input and checking for null port */
   if( ! PORT_NULL(a))
      for(i = 0; i < PORT_SIZE(a); i++)
         x = INPUT(a[i]);

   /* Accessing a digital input */
   x = INPUT(a);

   /* Accessing the value of a User-Defined Node input...     */
   /* This node type includes two elements in its definition. */
   a_ptr = INPUT(a);
   x = a_ptr->component1;
   y = a_ptr->component2;

   /* Outputting a simple real-valued result */
   OUTPUT(out1) = 0.0;

   /* Outputting a vector result and checking for null */
   if( ! PORT_NULL(a))
      for(i = 0; i < PORT.SIZE(a); i++)
         OUTPUT(a[i]) = 0.0;

   /* Outputting the partial of output out1 w.r.t. input a */
   PARTIAL(out1,a) = PARAM(gain);

  /* Outputting the partial of output out2(i) w.r.t. input b(j) */
   for(i = 0; i < PORT_SIZE(out2); i++) {
      for(j = 0; j < PORT_SIZE(b); j++) {
         PARTIAL(out2[i],b[j]) = 0.0;
      }
   }

  /* Outputting gain from input c to output out3 in an
     AC analysis */
   complex_gain_real = 1.0;
   complex_gain_imag = 0.0;
   AC_GAIN(out3,c) = complex_gain;

   /* Outputting a digital result */
   OUTPUT_STATE(out4) = ONE;

   /* Outputting the delay for a digital or user-defined output */
   OUTPUT_DELAY(out5) = 1.0e-9;
}
"""

############################################################
#
# 28.8
# User-Defined Node Definition File
#

##################################################
# @41546

    sa98f = """
#include <stdio.h>
#include "ngspice/cm.h"
#include "ngspice/evtudn.h"

void *tmalloc(size_t);
#define TMALLOC(t,n)  (t*) tmalloc(sizeof(t)*(size_t)(n))

/* macro to ignore unused variables and parameters */
#define NG_IGNORE(x)  (void)x

/* ************************************************* */

static void udn_int_create(CREATE_ARGS)
{
    /* Malloc space for an int */
    MALLOCED_PTR = TMALLOC(int, 1);
}

/* ************************************************* */

static void udn_int_dismantle(DISMANTLE_ARGS)
{
    NG_IGNORE(STRUCT_PTR);
    /* Do nothing.  There are no internally malloc'ed
       things to dismantle */
}

/* ************************************************* */

static void udn_int_initialize(INITIALIZE_ARGS)
{
    int  *int_struct = (int *) STRUCT_PTR;

    /* Initialize to zero */
    *int_struct = 0;
}

/* ************************************************* */

static void udn_int_invert(INVERT_ARGS)
{
    int      *int_struct = (int *) STRUCT_PTR;

    /* Invert the state */
    *int_struct = -(*int_struct);
}

/* ************************************************* */

static void udn_int_copy(COPY_ARGS)
{
    int  *int_from_struct = (int *) INPUT_STRUCT_PTR;
    int  *int_to_struct   = (int *) OUTPUT_STRUCT_PTR;

    /* Copy the structure */
    *int_to_struct = *int_from_struct;
}

/* ************************************************* */

static void udn_int_resolve(RESOLVE_ARGS)
{
    int **array    = (int**)INPUT_STRUCT_PTR_ARRAY;
    int *out       = (int *) OUTPUT_STRUCT_PTR;
    int num_struct = INPUT_STRUCT_PTR_ARRAY_SIZE;

    int         sum;
    int         i;

    /* Sum the values */
    for(i = 0, sum = 0; i < num_struct; i++)
        sum += *(array[i]);

    /* Assign the result */
    *out = sum;
}

/* ************************************************* */

static void udn_int_compare(COMPARE_ARGS)
{
    int  *int_struct1 = (int *) STRUCT_PTR_1;
    int  *int_struct2 = (int *) STRUCT_PTR_2;

    /* Compare the structures */
    if((*int_struct1) == (*int_struct2))
        EQUAL = TRUE;
    else
        EQUAL = FALSE;
}

/* ************************************************* */

static void udn_int_plot_val(PLOT_VAL_ARGS)
{
    int   *int_struct = (int *) STRUCT_PTR;
    NG_IGNORE(STRUCT_MEMBER_ID);

    /* Output a value for the int struct */
    PLOT_VAL = *int_struct;
}

/* ************************************************* */

static void udn_int_print_val(PRINT_VAL_ARGS)
{
    int   *int_struct = (int *) STRUCT_PTR;
    NG_IGNORE(STRUCT_MEMBER_ID);

    /* Allocate space for the printed value */
    PRINT_VAL = TMALLOC(char, 30);

    /* Print the value into the string */
    sprintf(PRINT_VAL, "%8d", *int_struct);
}

/* ************************************************* */

static void udn_int_ipc_val(IPC_VAL_ARGS)
{
    /* Simply return the structure and its size */
    IPC_VAL = STRUCT_PTR;
    IPC_VAL_SIZE = sizeof(int);
}

Evt_Udn_Info_t udn_int_info = {
    "int",
    "integer valued data",

    udn_int_create,
    udn_int_dismantle,
    udn_int_initialize,
    udn_int_invert,
    udn_int_copy,
    udn_int_resolve,
    udn_int_compare,
    udn_int_plot_val,
    udn_int_print_val,
    udn_int_ipc_val
};
"""

####################################################################################################
#
# Chapter 29
# Error Messages
#

class ErrorMessages(Examples):
    pass

############################################################
#
# Part III CIDER
#

####################################################################################################
#
# Chapter 30
# CIDER User’s Manual
#

class CIDER(Examples):

############################################################
#
# 30.1 SPECIFICATION
#

##################################################
# @42146

    F12f6 = """
.MODEL M_NUMERICAL NUPD LEVEL=2
+ cardnamel numberl=val1 (number2 val2), (number3 = val3)
+ cardname2 numberl=val1 string1 = name1
+
+ cardname3 numberl=val1, flag1, ^flag2
+ + number2=val2, flag3
"""

##################################################
# @42158

    E7223 = """
dl 1 2 M_NUMERICAL area=lOOpm^2 ic.file = "diode.IC"
"""

############################################################
#
# 30.2 BOUNDARY, INTERFACE
#

##################################################
# @42166

    F7ae2 = """
boundary domain [bounding-box] [properties]
interface domain neighbor [bounding-box] [properties]
"""

##################################################
# @42422

    E77d7 = """
interface dom=l neigh=2 sn=l.Oe4 sp=l.Oe4
"""

##################################################
# @42445

    E815f = """
interface dom=l neigh=2 x.l=l.l x.h=2.9 layer.w=0.01
"""

##################################################
# @42450

    Ebfd9 = """
interface dom=l neigh=% x.l=l.l x.h=2.9 layer.w=0.0
"""

############################################################
#
# 30.3 COMMENT
#

##################################################
# @42458

    Fca31 = """
comment [text]
* [text]
$ [text]
# [text]
"""

##################################################
# @42471

    E0589 = """
* CIDER and SPICE would ignore this input line
$ CIDER and PISCES would ignore this , but SPICE wouldn't
# CIDER and Linux Shell scripts would ignore this input line
"""

############################################################
#
# 30.4 CONTACT
#

##################################################
# @42482

    F4146 = """
contact number [workfunction]
"""

##################################################
# @42525

    E2fc0 = """
contact num=2 workf=5.29
"""

############################################################
#
# 30.5 DOMAIN, REGION
#

##################################################
# @42536

    Fd0b4 = """
domain number material [position]
region number material [position]
"""

##################################################
# @42672

    E2514 = """
domain num=l material=l x.l=O.O x.h=4.0 y.l=O.O y.h=2.0
"""

##################################################
# @42680

    Ee3ee = """
domain n=l m=l y.l=O.O
domain n=2 m=2 y.h=O.O
"""

############################################################
#
# 30.6 DOPING
#

##################################################
# @42692

    F9e3e = """
doping [domains] profile-type [lateral-profile-type] [axis]
    [impurity-type1 [constant-box] [profile-specifications]
"""

##################################################
# @43067

    E1b9c = """
doping uniform p.type conc=l.0el6
"""

##################################################
# @43075

    E161b = """
doping gauss lat.rotate n.type conc=l.0el9
+ x.l=0.0 x.h=0.5 y.l=0.0 y.h=0.2 ratio=0.7
"""

##################################################
# @43084

    E5b6b = """
doping gauss lat.erfc conc=l.0el9
+ x.l=0.0 x.h=0.5 y.l=0.0 y.h=0.2 ratio=0.7
"""

##################################################
# @43105

    Ef3e7 = """
doping ascii suprem3 infile=implant.s3 lat.unif boron
+ x.l=1.0 x.h=3.0 y.l=0.0
"""

############################################################
#
# 30.7 ELECTRODE
#

##################################################
# @43117

    Ff8b8 = """
electrode [number] [position]
"""

##################################################
# @43243

    Edcf5 = """
* DRAIN
electrode x.l=0.0 x.h=0.5 y.l=0.0 y.h=0.0
* GATE
electrode x.l=1.0 x.h=3.0 iy.l=0 iy.h=0
* SOURCE
electrode x.l=3.0 x.h=4.0 y.l=0.0 y.h=0.0
* BULK
electrode x.l=0.0 x.h=4.0 y.l=2.0 y.h=2.0
"""

##################################################
# @43258

    Ef72e = """
* EMITTER
electrode num=3 x.l=1.0 x.h=2.0 y.l=0.0 y.h=0.0
* BASE
electrode num=2 x.l=0.0 x.h=0.5 y.l=0.0 y.h=0.0
electrode num=2 x.l=2.5 x.h=3.0 y.l=0.0 y.h=0.0
* COLLECTOR
electrode num=1 x.l=0.0 x.h=3.0 y.l=1.0 y.h=1.0
"""

############################################################
#
# 30.8 END
#

##################################################
# @43275

    F7a92 = """
end
"""

############################################################
#
# 30.9 MATERIAL
#

##################################################
# @43286

    Ffe5c = """
material number type [physical-constants]
"""

##################################################
# @43757

    E00ba = """
material num=1 silicon eg=1.12 deg.dt=4.7e-4 eg.tref=640.0
"""

##################################################
# @43765

    Eec32 = """
material num=2 silicon tn=1ps tp=1ps
"""

############################################################
#
# 30.10 METHOD
#

##################################################
# @43776

    Fd589 = """
method [types] [parameters]
"""

##################################################
# @43859

    E87dd = """
method onec ac.an=direct
"""

##################################################
# @43879

    EEe984 = """
method devtol=1e-10 itlim=15
"""

############################################################
#
# 30.11 Mobility
#

##################################################
# @43888

    F08b9 = """
mobility material [carrier] [parameters] [models] [initialize]
"""

##################################################
# @44054

    Ef5a1 = """
mobility mat=l concmod=sg fieldmod=sg
mobility mat=l elec major mumax=1000.0 mumin=l00.0
+ ntref=l.0el6 ntexp=0.8 vsat=l.0e7 vwarm=3.0e6
mobility mat=l elec minor mumax=1000.0 mumin=200.O
+ ntref=l.0el7 ntexp=0.9
mobility mat=l hole major mumax=500.0 mumin=50.0
+ ntref=l.0el6 ntexp=0.7 vsat=8.0e6 vwarm=l.0e6
mobility mat=l hole minor mumax=500.0 mumin=150.0
+ ntref=l.0el7 ntexp=0.8
"""

##################################################
# @44070

    E1b84 = """
mobility mat=l elec mus=800.0 ec.a=3.0e5 ec.b=9.0e5
"""

##################################################
# @44078

    E58f1 = """
mobility mat=l init elec major fieldmodel=sg
mobility mat=l init hole major fieldmodel=sg
mobility mat=l fieldmodel=ga
"""

############################################################
#
# 30.12 MODELS
#

##################################################
# @44093

    F5f6c = """
models [model flags]
"""

##################################################
# @44208

    Eede3 = """
models bgn srh conctau auger aval
"""

##################################################
# @44216

    E61c7 = """
models surfmob transmob fieldmob ^aval
"""

############################################################
#
# 30.13 OPTIONS
#

##################################################
# @44229

    F563c = """
options [device-type] [initial-state] [dimensions]
    [measurement-temperature]
"""

##################################################
# @44403

    E2467 = """
options bipolar defl=1.0
"""

##################################################
# @44411

    E98c1 = """
options base.area=0.1 base.depth=0.2 base.len=1.5
"""

##################################################
# @44419

    E7c90 = """
options unique ic.file="OP1"
"""

############################################################
#
# 30.14
# OUTPUT
#

##################################################
# @44431

    F3b48 = """
output [debugging-flags] [general-info] [saved-solutions]
"""

##################################################
# @44714

    E95e8 = """
output all.debug mater stat
"""

##################################################
# @44722

    E95ba = """
output phin phjp phic phiv vac.psi
"""

##################################################
# @44732

    E1845 = """
output psi n.conc p.conc ^e.f ^jn ^jp ^jd
"""

############################################################
#
# 30.15 TITLE
#

##################################################
# @44743

    Fc078 = """
title [text]
"""

##################################################
# @44753

    E5cf2 = """
title L=1.0um NMOS Device, 1.0um BiCMOS Process
"""

############################################################
#
# 30.16 X.MESH, Y.MESH
#

##################################################
# @44764

    F655c = """
x.mesh position numbering-method [spacing-parameters]
y.mesh position numbering-method [spacing-parameters]
"""

##################################################
# @44870

    Ebe64 = """
x.mesh loc=0.0 n=1
x.mesh loc=5.0 n=50
"""

##################################################
# @44879

    Ecf13 = """
x.mesh w=0.75 h.e=0.001 h.m=0.l ratio=1.5
x.mesh w=2.25 h.s=0.001 h.m=0.l ratio=1.5
"""

##################################################
# @44888

    E887c = """
y.mesh loc=-0.04 node=1
y.mesh loc=0.0 node=6
y.mesh width=0.5 h.start=0.001 h.max=.05 ratio=2.0
y.mesh width=2.5 h.start=0.05 ratio=2.0
"""

############################################################
#
# 30.17 NUMD
#

##################################################
# @44902

    Febc9 = """
.MODEL model-name NUMD [level]
+ ...
"""

##################################################
# @44910

    Fe700 = """
DXXXXXXX nl n2 model-name [geometry] [temperature] [initial-conditions]
"""

##################################################
# @44917

    Fbdc1 = """
.SAVE [small-signal values]
"""

##################################################
# @45067

    E5789 = """
DSWITCH 1 2 M_SWITCH_DIODE AREA=2
.MODEL M_SWITCH_DIODE NUMD
+ options defa=1p ...
+ ...
"""

##################################################
# @45078

    E99d1 = """
DMOSCAP 11 12 M_MOSCAP W=20um IC=3v
.MODEL M_MOSCAP NUMD LEVEL=2
+ options moscap defw=1m
+ ...
"""

##################################################
# @45089

    Eb6ec = """
D1 POSN NEGN POWERMOD AREA=2 W=6um TEMP=100.0
.MODEL POWERMOD NUMD LEVEL=2
* + ...
"""

##################################################
# @45099

    Edae2 = """
.SAVE @d1[g11] @d1[g12] @d1[g21] @d1[g22]
.SAVE @d1[c11] @d1[c12] @d1[c21] @d1[c22]
.SAVE @d1[y11] @d1[y12] @d1[y21] @d1[y22]
"""

############################################################
#
# 30.18 NBJT
#

##################################################
# @45114

    Faf46 = """
.MODEL model-name NBJT [level]
+ ...
"""

##################################################
# @45122

    F9b6e = """
QXXXXXXX nl n2 n3 model-name [geometry]
+ [temperature] [initial-conditions]
"""

##################################################
# @45282

    Ed2a0 = """
Q2 1 2 3 M_BJT AREA=4
"""

##################################################
# @45290

    Eb2ec = """
.SAVE @q2[g11] @q2[g12] @q2[g22]
"""

##################################################
# @45298

    Ee8f1 = """
QJ1 11 12 13 M_JFET W=5um IC.FILE="IC.jfet"
.MODEL M_JFET NBJT LEVEL=2
+ options jfet
* + ...
"""

##################################################
# @45309

    E5482 = """
Q2 NC2 NB2 NE2 BJTMOD AREA=1
Q3 NC3 NB3 NE3 BJTMOD AREA=1
.MODEL BJTMOD NBJT LEVEL=2
+ options defw=2um
+ * Define half of the device now
* + ...
"""

############################################################
#
# 30.19 NUMOS
#

##################################################
# @45327

    Fa29c = """
.MODEL model-name NUMOS [level]
+ ...
"""

##################################################
# @45335

    E44e0 = """
MXXXXXXX nl n2 n3 n4 model-name [geometry]
+ [temperature] [initial-conditions]
"""

##################################################
# @45504

    Ee768 = """
M1 1 2 3 4 M_NMOS_1UM W=5um L=1um IC.FILE="NM1.vth"
.MODEL MNMOS_1UM NUMOS
+ * Description of a lum device
* + ...
"""

##################################################
# @45515

    E5b76 = """
.SAVE @m1[y11] @m1[y12] @ml[y14]
.SAVE @m1[y21] @m1[y22] @ml[y24]
.SAVE @m1[y41] @m1[y42] @ml[y44]
"""

##################################################
# @45525

    E2764 = """
MQ1 NC NB NE NS N_BJT
.MODEL M_BJT NUMOS LEVEL=2
+ options bipolar defw=5um
* + ...
"""

############################################################
#
# 30.20 Cider examples
#

############################################################
#
# Part IV Miscellaneous
#

####################################################################################################
#
# Chapter 31
# Model and Device Parameters
#

class ModelDeviceParameters(Examples):

############################################################
#
# 31.1
# Accessing internal device parameters
#

##################################################
# @45544

    E3294 = """
save @m1[cgs]
"""

##################################################
# @45549

    Ee2a3 = """
plot @m1[cgs]
"""

##################################################
# @45560

    F1d37 = """
@device_identifier.subcircuit_name.<subcircuit_name_nn>
+.device_name[parameter]
"""

##################################################
# @45566

    Eb921 = """
* transistor output characteristics
* two nested subcircuits
vdd d1 0 2.0
vss vsss 0 0
vsig g1 vsss 0
xmos1 d1 g1 vsss level1
.subckt level1 d3 g3 v3
xmos2  d3 g3 v3 level2
.ends
.subckt level2 d4 g4 v4
m1 d4 g4 v4 v4 nmos w=1e-5 l=3.5e-007
.ends
.dc vdd 0 5 0.1 vsig 0 5 1
.control
save all @m.xmos1.xmos2.m1[vdsat]
run
plot vss#branch   $ current measured at the top level
plot @m.xmos1.xmos2.m1[vdsat]
.endc
.MODEL NMOS NMOS  LEVEL   = 8
+VERSION = 3.2.4  TNOM    = 27  TOX     = 7.4E-9
.end
"""
