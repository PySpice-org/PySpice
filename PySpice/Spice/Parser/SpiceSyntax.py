####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = [
    'BuiltinFunctions',
    'DotCommands',
    'ElementLetters',
    'UnitSuffix',
]

####################################################################################################

class DotCommands:
    # Fixme: from Ngspice flavour
    AC = "start an ac simulation"
    CONTROL = "start a .control section"
    CSPARAM = "define parameter(s) made available in a control section"
    DC = "start a dc simulation"
    DISTO = "start a distortion analysis simulation"
    ELSE = "conditional branching in the netlist"
    ELSEIF = "conditional branching in the netlist"
    END = "end of the netlist"
    ENDC = "end of the .control section"
    ENDIF = "conditional branching in the netlist"
    ENDS = "end of subcircuit definition"
    FOUR = "Fourier analysis of transient simulation output"
    FUNC = "define a function"
    GLOBAL = "define global nodes"
    IC = "set initial conditions"
    IF = "conditional branching in the netlist"
    INCLUDE = "include part of the netlist"
    LIB = "include a library"
    MEAS = "measurements during the simulation"
    MODEL = "list of device model parameters"
    NODESET = "set initial conditions"
    NOISE = "start a noise simulation"
    OP = "start an operating point simulation"
    OPTIONS = "set simulator options"
    PARAM = "define parameter(s)"
    PLOT = "printer plot during batch simulation"
    PRINT = "tabular listing during batch simulation"
    PROBE = "same as .SAVE: name simulation result vectors to be saved"
    PSS = "start a periodic steady state analysis"
    PZ = "start a pole-zero analysis simulation"
    SAVE = "name simulation result vectors to be saved"
    SENS = "start a sensitivity analysis"
    SUBCKT = "start of subcircuit definitions"
    TEMP = "set the ciruit temperature"
    TF = "start a transfer function analysis"
    TITLE = "title of the netlist"
    TRAN = "start a transient simulation"
    WIDTH = "width of printer plot"

####################################################################################################

class ElementLetters:
    # Fixme: from Ngspice flavour
    # from A to Z
    A = "XSPICE code model"
    B = "Behavioral (arbitrary) source"
    C = "Capacitor"
    D = "Diode"
    E = "Voltage-controlled voltage source (VCVS) linear"
    F = "Current-controlled current source (CCCs) linear"
    G = "Voltage-controlled current source (VCCS) linear"
    H = "Current-controlled voltage source (CCVS) linear"
    I = "Current source"
    J = "Junction field effect transistor (JFET)"
    K = "Coupled (Mutual) Inductors"
    L = "Inductor"
    M = "Metal oxide field effect transistor (MOSFET)"
    N = "Numerical device for GSS"
    O = "Lossy transmission line"
    P = "Coupled multiconductor line (CPL)"
    Q = "Bipolar junction transistor (BJT)"
    R = "Resistor"
    S = "Switch (voltage-controlled)"
    T = "Lossless transmission line"
    U = "Uniformly distributed RC line"
    V = "Voltage source"
    W = "Switch (current-controlled)"
    X = "Subcircuit"
    Y = "Single lossy transmission line (TXL)"
    Z = "Metal semiconductor field effect transistor (MESFET)"

####################################################################################################

class BuiltinFunctions:
    sqrt = ('x')
    sin = ('x')
    cos = ('x')
    tan = ('x')
    sinh = ('x')
    cosh = ('x')
    tanh = ('x')
    asin = ('x')
    acos = ('x')
    atan = ('x')
    asinh = ('x')
    acosh = ('x')
    atanh = ('x')
    arctan = ('x')   # atan = ('x'), kept for compatibility
    exp = ('x')
    ln = ('x')
    log = ('x')
    abs = ('x')
    nint = ('x')       # Nearest integer, half integers towards even
    int = ('x')        # Nearest integer rounded towards 0
    floor = ('x')      # Nearest integer rounded towards -∞
    ceil = ('x')       # Nearest integer rounded towards +∞
    pow = ('x', 'y')   # x raised to the power of y (pow from C runtime library)
    pwr = ('x', 'y')   # pow(fabs = ('x'), y)
    min = ('x', 'y')
    max = ('x', 'y')
    sgn = ('x')   # 1.0 for x > 0, 0.0 for x == 0, -1.0 for x < 0
    ternary_fcn = ('x', 'y', 'z')      # x ? y : z
    gauss = ('nom', 'rvar', 'sigma')   # nominal value plus variation drawn from Gaussian
                                       # distribution with mean 0 and standard deviation rvar
                                       # (relative to nominal), divided by sigma
    agauss = ('nom', 'avar', 'sigma')  # nominal value plus variation drawn from Gaussian
                                       # distribution with mean 0 and standard deviation avar
                                       # (absolute), divided by sigma
    unif = ('nom', 'rvar')    # nominal value plus relative variation (to nominal) uniformly distributed between +/-rvar
    aunif = ('nom', 'avar')   # nominal value plus absolute variation uniformly distributed between +/-avar
    limit = ('nom', 'avar')   # nominal value +/-avar, depending on random number in [-1, 1[ being > 0 or < 0

####################################################################################################

class UnitSuffix:
    T = 'Tera'    # 10**12
    G = 'Giga'    # 10**9
    Meg = 'Mega'  # 10**6
    K = 'Kilo'    # 10**3
    mil = 'Mil'   # 25.4 ×10**−6
    m = 'milli'   # 10**−3
    u = 'micro'   # 10**−6
    n = 'nano'    # 10**−9
    p = 'pico'    # 10**−12
    f = 'femto'   # 10**−15
