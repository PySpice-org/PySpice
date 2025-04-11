from PySpice.Doc.ExampleTools import find_libraries
from PySpice import SpiceLibrary, Circuit, Simulator, plot
from PySpice.Unit import *

####################################################################################################

libraries_path = "/home/asepahvand/repos/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib_custom.spice"
# libraries_path = '/home/asepahvand/repos/skywater-pdk/libraries/sky130_fd_pr/latest/cells/res_high_po/sky130_fd_pr__res_high_po.model.spice'
# libraries_path = "/home/asepahvand/repos/spice_libraries/"
spice_lib = SpiceLibrary(libraries_path, recurse=True)

####################################################################################################

circuit = Circuit('Circuit with Subcircuits')


# # Safely iterate through subcircuits with error handling
# print("\nSubcircuit details:")
# for subcirc in spice_lib.subcircuits:
#     try:
#         print(f"\nProcessing subcircuit: {subcirc}")
        
#         # Safely access the subcircuit
#         subckt = spice_lib[subcirc]
#         print(f"  Successfully loaded subcircuit: {subcirc}")
        
#         # Check what attributes are available
#         if hasattr(subckt, "path"):
#             print(f"  Path: {subckt.path}")
        
#         # Try to access nodes safely
#         if hasattr(subckt, "_nodes"):
#             print(f"  Nodes: {len(subckt._nodes)} nodes found")
#             for i, node in enumerate(subckt._nodes):
#                 print(f"    Node {i+1}: {node}")
#         else:
#             print("  No _nodes attribute found")
            
#         # Check for additional attributes
#         for attr in ["name", "pin_names", "description"]:
#             if hasattr(subckt, attr):
#                 print(f"  {attr}: {getattr(subckt, attr)}")
                
#     except KeyError as e:
#         print(f"  Error: Could not find subcircuit '{subcirc}' - {e}")
#     except Exception as e:
#         print(f"  Error processing subcircuit '{subcirc}': {e}")

# Print information about the library
print(f"Library loaded from: {libraries_path}")
print(f"Available subcircuits in library: {list(spice_lib.subcircuits)}")
print(f"Total number of subcircuits found: {len(list(spice_lib.subcircuits))}")
# Print the circuit
print("\nCircuit:")
print(circuit)