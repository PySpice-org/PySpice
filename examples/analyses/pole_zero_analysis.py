#! /usr/bin/env python3

####################################################################################################

# Program to test pole-zero function of ngspice, PySpice

import argparse

####################################################################################################

import math
import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging

####################################################################################################

from PySpice.Spice.Netlist import Circuit, SubCircuit

class NodeNames:
    """Allow setting of nodes with appropriate names."""
    def __init__(self, *args):
        for arg in args:
            setattr(self, arg, arg)

def test_simple():
    circuit = Circuit('pole-zero test circuit')
    n = NodeNames('input', 'output')
    com = 0
    circuit.R('1', n.input, n.output, 1e4)
    circuit.C('1', n.input, n.output, 1e-6)
    circuit.R('2', n.output, com, 1000)
    circuit.C('2', n.output, com, 1e-6)
    circuit.L('1', n.output, com, 1e-3)
    print("circuit",circuit)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.polezero(n.input,com, n.output,com, 'vol', 'pz')
    print("Poles")
    for n in analysis.nodes:
        if not n.startswith('pole'): continue
        pole = np.array(analysis[n])
        print(pole)
    print("Zeros")
    for n in analysis.nodes:
        if not n.startswith('zero'): continue
        zero = np.array(analysis[n])
        print(zero)

if __name__ == '__main__':
    logger = Logging.setup_logging()
    parser = argparse.ArgumentParser("Test pyspice pole-zero function")
    parser.add_argument('-ts', action='store_true', dest='t_simple', help='Test simple rlc network.')
    args=parser.parse_args()
    if args.t_simple: test_simple()

