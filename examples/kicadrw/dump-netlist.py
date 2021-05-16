####################################################################################################

from pathlib import Path

from KiCadRW.Schema import KiCadSchema
from KiCadRW.CircuitMacros import CircuitMacrosDumper
from PySpice.KiCad import PythonDumper

####################################################################################################

schema_path = Path(
    'examples', 'power-supplies', 'kicad', 'capacitive-half-wave-rectification-pre-zener',
    'capacitive-half-wave-rectification-pre-zener.kicad_sch'
)

kicad_schema = KiCadSchema(schema_path)
print()
print('='*100)
kicad_schema.dump_netlist()

print()
print('='*100)
python_code = PythonDumper(kicad_schema, use_pyspice_unit=True)
print(python_code)

print()
print('='*100)
cm_code = CircuitMacrosDumper(kicad_schema)
print(cm_code)
