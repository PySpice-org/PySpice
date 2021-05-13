####################################################################################################

from pathlib import Path

from KiCadTools.Schema import KiCadSchema
from PySpice.KiCad import NetlistWrapper

####################################################################################################

schema_path = Path(
    'examples', 'power-supplies', 'kicad', 'capacitive-half-wave-rectification-pre-zener',
    'capacitive-half-wave-rectification-pre-zener.kicad_sch'
)

# schema_path = Path(
#     'KiCadTools', 'kicad-example', 'kicad-example.kicad_sch'
# )

kicad_schema = KiCadSchema(schema_path)
print()
print('='*100)
kicad_schema.dump_netlist()

print()
print('='*100)
netlist_wrapper = NetlistWrapper(kicad_schema)
