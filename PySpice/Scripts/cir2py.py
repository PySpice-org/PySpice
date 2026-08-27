####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

import argparse

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Parser import SpiceFile
from PySpice.Spice.Parser.Translator import Builder, ToPython

####################################################################################################

def main():

    parser = argparse.ArgumentParser(description='Convert a circuit file to PySpice')

    parser.add_argument('circuit_file', # metavar='circuit_file',
                        help='.cir file')

    parser.add_argument('-o', '--output',
                        default=None,
                        help='Output file')

    parser.add_argument('--ground',
                        type=int,
                        default=0,
                        help='Ground node')

    parser.add_argument('--show',
                        default=False, action='store_true',
                        help='Show circuit')

    parser.add_argument('--format',
                        default=False, action='store_true',
                        help='Format circuit')

    parser.add_argument('--build',
                        default=False, action='store_true',
                        help='Build circuit')

    parser.add_argument('--translate',
                        default=False, action='store_true',
                        help='translate circuit')

    args = parser.parse_args()

    ##############################################

    spice_file = SpiceFile(path=args.circuit_file)

    if args.show:
        print('Title header:', spice_file.title)
        print('Subcircuits:')
        for subcircuit in spice_file.subcircuits:
            print(f'  {subcircuit.name}')
        print('Models:')
        for model in spice_file.models:
            print(f'  {model.name}')

    if args.format:
        print(spice_file.to_spice(comment=True, line_length_max=100))

    if args.build:
        Builder().translate(spice_file)

    if args.translate:
        circuit = ToPython().translate(spice_file, ground=args.ground)
        if args.output is not None:
            with open(args.output, 'w') as f:
                f.write(circuit)
        else:
            print(circuit)
