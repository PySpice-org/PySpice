from pathlib import Path
from PySpice.Spice.Library import SpiceLibrary

library_path = Path(__file__).resolve().parents[1].joinpath('examples', 'libraries')
print(library_path)
spice_library = SpiceLibrary(library_path)
# print list(spice_library.iter_on_subcircuits())
# print list(spice_library.iter_on_models())
print(list(spice_library.subcircuits))
print(list(spice_library.models))
