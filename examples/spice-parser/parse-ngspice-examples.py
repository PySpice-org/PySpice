####################################################################################################

#r#
#r# ========================
#r#  Parse NgSpice Examples
#r# ========================
#r#
#r# This example shows a to use the module :mod:`PySpice.Spice.NgSpice.ManualExamples`.
#r#

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from pathlib import Path
import os

from PySpice.Spice.NgSpice import ManualExamples
from PySpice.Spice.Parser import SpiceSource, SpiceFile

####################################################################################################

classes_to_process = (
    'CircuitDescription',
    'CircuitElementsModels',
    'VoltageCurrentSources',
    'BehavioralSources',
    'TransmissionLines',
    'Diodes',
    'BJT',
    'JFETS',
    'MESFETS',
    'MOSFETS',
    'XSPICE',
    # 'VerilogADeviceModel',
    # 'TCAD',
    'AnalysesOutputControl',
    # 'StartingNgspice',
    # 'InteractiveInterpreter',
    # 'NgspiceUserInterfaces',
    # 'NgspiceSharedLibrary',
    # 'TCLspice',
    'ExampleCircuits1',
    'StatisticalCircuitAnalysis',
    'CircuitOptimization',
    'XspiceBasics',
    # 'ExecutionProcedures',
    'ExampleCircuits2',
    # 'CodeModels',
    # 'ErrorMessages',
    # 'CIDER',
    'ModelDeviceParameters',
)

def generator():
    line_counter = 0
    for cls in ManualExamples.Examples.subclasses():
        if cls.__name__ in classes_to_process:
            for _, value in cls.iter_on_examples(label='E'):
                for line in value.strip().splitlines():
                    # print(f'{line_counter}>>> {line}')
                    if line:
                        yield line_counter, line
                    line_counter += 1

# spice_source = SpiceSource()
# spice_source.read(generator(), title_line=False)

# #r# Dump the pre-processed lines
# for line in spice_source.lines:
#     print(line)

# #r# Note: set env PySpiceLogLevel=debug
# spice_source.parse()

# #r# Dump the parsed lines
# for obj in spice_source.obj_lines:
#     print('-'*80)
#     print(obj.line)
#     print()
#     print(obj.ast.pretty_print())
#     print(obj)

####################################################################################################

spice_examples_path = Path(__file__).parents[1].joinpath('spice-examples')

for filename in (
        'ac-coupled-transistor-amplifier.cir',
        'operational-amplifier-model-1.cir',
):
    print('='*100)
    print(f'File {filename}')
    path = spice_examples_path.joinpath(filename)
    spice_file = SpiceFile(path)
