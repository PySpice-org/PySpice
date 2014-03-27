from PySpice.SpiceLibrary import SpiceLibrary

spice_library = SpiceLibrary('/home/gv/sys/fc14/fabrice/electronic-design-pattern/spice/libraries')
# print list(spice_library.iter_on_subcircuits())
# print list(spice_library.iter_on_models())
print spice_library.subcircuits.keys()
print spice_library.models.keys()
