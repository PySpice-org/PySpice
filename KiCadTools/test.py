####################################################################################################

from pathlib import Path

from KiCadTools.Schema import KiCadSchema

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
kicad_schema.netlist()

####################################################################################################

# for lib in kicad_schema.symbol_libs:
#     print(lib)

# spice-ngspice:0
# spice-ngspice:C
# spice-ngspice:CHOKE
# spice-ngspice:CURRENT_MEASURE
# spice-ngspice:Csmall
# spice-ngspice:DIODE
# spice-ngspice:INDUCTOR
# spice-ngspice:ISOURCE
# spice-ngspice:ISRC_ICTL
# spice-ngspice:ISRC_VCTL
# spice-ngspice:NMOS
# spice-ngspice:OPAMP
# spice-ngspice:PMOS
# spice-ngspice:QNPN
# spice-ngspice:QPNP
# spice-ngspice:R
# spice-ngspice:Rsmall
# spice-ngspice:SWITCH
# spice-ngspice:TOGGLE
# spice-ngspice:VSOURCE
# spice-ngspice:VSRC_ICTL
# spice-ngspice:VSRC_VCTL
# spice-ngspice:Vsrc
# spice-ngspice:ZENOR
