#! /usr/bin/env python3

# Program to test pole-zero, noise, and distortion function of ngspice, PySpice

import argparse

####################################################################################################

import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging

####################################################################################################

from PySpice.Spice.Netlist import Circuit

# This program implements the PySpice equivalent of the following circuit,
# which is run using the shell command
# $ ngspice -b file.ckt
FILE_CKT = """
.title test circuit
.model qbc847b npn (BF=324.4 BR=8.29 CJC=3.347e-12 CJE=1.244e-11 CJS=0 EG=1.11 FC=0.979 IKF=0.109 IKR=0.09 IRB=5e-06 IS=1.822e-14 ISC=9.982e-12 ISE=2.894e-16 ITF=0.3131 MJC=0.391 MJE=0.3656 MJS=0.333 NC=1.763 NE=1.4 NF=0.9932 NR=0.9931 PTF=0 RB=10 RBM=5 RC=0.7014 RE=0.649 TF=4.908e-10 TR=9e-08 VAF=82 VAR=17.9 VJC=0.5463 VJE=0.7579 VJS=0.75 VTF=2.927 XCJC=0.6193 XTB=0 XTF=9.51 XTI=3)
R1 3 2 2200k
Q1 3 2 0 qbc847b
R3 1 3 1k
C1 4 2 100e-9
C2 3 5 1e-6
C4 1 3 10e-9
R5 5 0 10k
Vpwr 1 0 dc 6
Vin 4 0 dc 0 ac .001 distof1 1 distof2 0.1
.control
op 27
print all
ac dec 10 10 1e5
print V(5)
pz 4 0 5 0 vol pz
print all
noise v(5,0) Vin dec 10 10 1e5 1
print all
disto dec 10 10 1e5
print V(5)
disto dec 10 10 1e5 0.9
print V(5)
"""

class NodeNames:
    """ Allow setting of nodes with appropriate names. """
    def __init__(self, *args):
        for arg in args:
            setattr(self, arg, arg)

# npn gp signal transistor
def set_model_qbc847b(circuit):
    model = 'qbc847b'
    circuit.model(
        model, 'npn', IS=1.822E-14, NF=0.9932, ISE=2.894E-16, NE=1.4, BF=324.4,
        IKF=0.109, VAF=82, NR=0.9931, ISC=9.982E-12, NC=1.763, BR=8.29, IKR=0.09, VAR=17.9,
        RB=10, IRB=5E-06, RBM=5, RE=0.649, RC=0.7014, XTB=0, EG=1.11, XTI=3, CJE=1.244E-11,
        VJE=0.7579, MJE=0.3656, TF=4.908E-10, XTF=9.51, VTF=2.927, ITF=0.3131, PTF=0, CJC=3.347E-12,
        VJC=0.5463, MJC=0.391, XCJC=0.6193, TR=9E-08, CJS=0, VJS=0.75, MJS=0.333, FC=0.979,
    )
    return model

def simple_bjt_amp():
    circuit = Circuit('test circuit')
    model_npn = set_model_qbc847b(circuit)
    n = NodeNames('n1', 'n2', 'n3', 'n4', 'n5')
    gnd = 0
    circuit.R('1', n.n3, n.n2, 2.2e6)
    circuit.Q('1', n.n3, n.n2, gnd, model=model_npn)
    circuit.R('3', n.n1, n.n3, 1e3)
    circuit.C('1', n.n4, n.n2, 100e-9)
    circuit.C('2', n.n3, n.n5, 1e-6)
    circuit.C('4', n.n1, n.n3, 10e-9)
    circuit.R('5', n.n5, gnd, 10e3)
    circuit.V('pwr', n.n1, gnd, 6)
    circuit.V('in', n.n4, gnd, 'dc 0 ac 1 distof1 1 distof2 0.1')
    return circuit, n

def dump_circuit():
    circuit, n = simple_bjt_amp()
    print(circuit)

def do_dc_analysis():
    circuit, n = simple_bjt_amp()
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    print("Collector voltage: ", np.array(analysis[n.n3])[0])
    print("base voltage: ", np.array(analysis[n.n2])[0])

def do_ac_analysis():
    circuit, n = simple_bjt_amp()
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.ac(start_frequency=10, stop_frequency=1e6, number_of_points=100, variation='dec')
    gain = np.array(analysis[n.n5])
    figure = plt.figure(1, (20, 10))
    axe = plt.subplot(211)
    axe.grid(True)
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("dB gain.")
    axe.semilogx(analysis.frequency, 20*np.log10(np.abs(gain)))

    axe = plt.subplot(212)
    axe.grid(True)
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Phase.")
    axe.semilogx(analysis.frequency, np.arctan2(gain.imag, gain.real))
    plt.show()

def do_pz_analysis():
    circuit, n = simple_bjt_amp()
    com = 0
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.polezero(n.n4, com, n.n5, com, 'vol', 'pz')
    print("Poles")
    for n in analysis.nodes:
        if not n.startswith('pole'):
            continue
        pole = np.array(analysis[n])
        print(pole)
    print("Zeros")
    for n in analysis.nodes:
        if not n.startswith('zero'):
            continue
        zero = np.array(analysis[n])
        print(zero)

def do_noise_analysis():
    circuit, n = simple_bjt_amp()
    com = 0
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.noise(output_node=n.n5, ref_node=com, src='Vin', variation='dec', points=10, start_frequency=100, stop_frequency=1e5, points_per_summary=1)
    print("Total noise (Vrms) at circuit output:", np.array(analysis.nodes['onoise_total'])[0])
    print("Total noise (Vrms) as if at circuit input:", np.array(analysis.nodes['inoise_total'])[0])

def do_distortion_analysis(f2overf1):
    circuit, n = simple_bjt_amp()
    com = 0
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.distortion(variation='dec', points=10, start_frequency=100, stop_frequency=1e4, f2overf1=f2overf1)
    output = np.array(analysis[n.n5])
    analysis_ac = simulator.ac(start_frequency=100, stop_frequency=1e4, number_of_points=10, variation='dec')
    gain = np.array(analysis_ac[n.n5])
    print("output", output)
    print("gain", gain)
    figure = plt.figure(1, (20, 10))
    axe = plt.subplot(211)
    axe.grid(True)
    axe.set_xlabel("Frequency [Hz]")
    if f2overf1:
        axe.set_ylabel("Harmonic Magnitude.")
    else:
        axe.set_ylabel("Spectral Magnitude.")
    harmonics = output/gain
    axe.semilogx(analysis.frequency, np.abs(harmonics))
    axe = plt.subplot(212)
    axe.grid(True)
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Phase.")
    axe.semilogx(analysis.frequency, np.arctan2(harmonics.imag, harmonics.real))
    plt.show()

if __name__ == '__main__':

    logger = Logging.setup_logging()

    parser = argparse.ArgumentParser("Test pyspice pole-zero, noise, distortion analysis")
    parser.add_argument('-dcir', action='store_true', dest='dump_circuit', help='dump_circuit.')
    parser.add_argument('-ac', action='store_true', dest='do_ac', help='Output AC analysis.')
    parser.add_argument('-dc', action='store_true', dest='do_dc', help='Output DC bias points.')
    parser.add_argument('-pz', action='store_true', dest='do_pz', help='Output poles and zeros.')
    parser.add_argument('-n', action='store_true', dest='do_noise', help='Output noise analysis.')
    parser.add_argument('-dh', action='store_true', dest='do_distoh', help='Output harmonic distortion analysis.')
    parser.add_argument('-ds', action='store_true', dest='do_distos', help='Output spectral distortion analysis.')

    args = parser.parse_args()

    if args.dump_circuit:
        dump_circuit()
    if args.do_ac:
        do_ac_analysis()
    if args.do_dc:
        do_dc_analysis()
    if args.do_pz:
        do_pz_analysis()
    if args.do_noise:
        do_noise_analysis()
    if args.do_distoh:
        do_distortion_analysis(None)
    if args.do_distos:
        do_distortion_analysis(0.9)
