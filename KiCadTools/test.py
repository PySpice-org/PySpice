####################################################################################################

from pathlib import Path

from KiCadTools.Schema import KiCadSchema

####################################################################################################

schema_path = Path(
    'examples', 'power-supplies', 'kicad', 'capacitive-half-wave-rectification-pre-zener',
    'capacitive-half-wave-rectification-pre-zener.kicad_sch'
)

kicad_schema = KiCadSchema(schema_path)
print()
print('='*100)
kicad_schema.netlist()
