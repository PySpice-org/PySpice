####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

    parser.add_argument('--format',
                        default=False, action='store_true',
                        help='Format circuit')

    parser.add_argument('--build',
                        default=False, action='store_true',
                        help='Build circuit')

    args = parser.parse_args()

    ##############################################

    spice_file = SpiceFile(path=args.circuit_file)

    if args.format:
        print(spice_file.to_spice(comment=True, line_length_max=100))

    if args.build:
        Builder().translate(spice_file)

    circuit = ToPython().translate(spice_file, ground=args.ground)
    if args.output is not None:
        with open(args.output, 'w') as f:
            f.write(circuit)
    else:
        print(circuit)
