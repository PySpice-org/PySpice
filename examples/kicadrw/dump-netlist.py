"""This example shows how to read a KiCAD schema in order to dump the netlist, and to convert it
to Python PySpice code and to generate a Circuit_macros draft.

"""

####################################################################################################

from pathlib import Path

import PySpice.Logging.Logging as Logging
from kicadrw.drawings.CircuitMacros import CircuitMacrosDumper
from kicadrw.sexp.schema import KiCadSchema
from PySpice.KiCad import PythonDumper, SpiceDumper

logger = Logging.setup_logging()

####################################################################################################

# schema_path = Path(
#     'examples', 'power-supplies', 'kicad', 'capacitive-half-wave-rectification-pre-zener',
#     'capacitive-half-wave-rectification-pre-zener.kicad_sch'
# )

schema_path = Path(
    'kicad-schema',
    'charge-pump', 'charge-pump.kicad_sch'
)

RULE = '─' * 100

#m# Read the schema and dump the netlist:
kicad_schema = KiCadSchema(schema_path)
print()
print(RULE)
kicad_schema.dump_netlist()

#m# Convert the netlist to PySpice Python code:
print()
print(RULE)
python_code = PythonDumper(kicad_schema, use_pyspice_unit=True)
print(python_code)

print()
print(RULE)
spice_circuit = SpiceDumper(kicad_schema)
print(spice_circuit)

#m# Generate a Circuit_macros draft for this circuit.
#m# Then you have to add manually the tracks.
#m# Notice the KiCAD schema format is very simple. A track is only a bunch of segments.
#m# As opposite Circuit_macros is much more sophisticated.
print()
print(RULE)
cm_code = CircuitMacrosDumper(kicad_schema)
print(cm_code)
