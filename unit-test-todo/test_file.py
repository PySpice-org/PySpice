from PySpice.Spice.Library import SpiceLibrary

spice_library = SpiceLibrary('../examples/libraries')
# print list(spice_library.iter_on_subcircuits())
# print list(spice_library.iter_on_models())
print(list(spice_library.subcircuits))
print(list(spice_library.models))
