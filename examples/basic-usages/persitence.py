#r# ============================
#r#  Data Persistence / Caching
#r# ============================

#r# This example explains how to save or cache data with PySpice.

####################################################################################################

#r# Pickling
#r# --------

#r# The first method, it is to use the `pickle <https://docs.python.org/3/library/pickle.html>`_
#r# module provided with the Python standad library.  Pickle implements binary protocols for
#r# serializing and de-serializing a Python object structure.

#r# We will first create a circuit and run a simulation for our example.

####################################################################################################

from pathlib import Path
import pickle

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice import plot, SpiceLibrary, Circuit, Simulator
# from PySpice import *
from PySpice.Unit import *

from PySpice.Doc.ExampleTools import find_libraries
libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

pickle_file_path = Path('pickled-simulation.data')
run_simulation = not pickle_file_path.exists()

####################################################################################################

if run_simulation:
    circuit = Circuit('Capacitive Half-Wave Rectification (Pre Zener)')
    circuit.include(spice_library['1N4148'])
    circuit.include(spice_library['d1n5919brl'])
    ac_line = circuit.AcLine('input', 'L', circuit.gnd, rms_voltage=230@u_V, frequency=50@u_Hz)
    circuit.C('in', 'L', 1, 330@u_nF)
    circuit.R('emi', 'L', 1, 165@u_kΩ)
    circuit.R('in', 1, 2, 2*47@u_Ω)
    circuit.X('D1', '1N4148', 2, 'out')
    circuit.C('2', 'out', 3, 250@u_uF)
    circuit.R('2', 3, circuit.gnd, 1@u_kΩ)
    circuit.X('D2', '1N4148', 3, 2)
    circuit.X('Dz', 'd1n5919brl', circuit.gnd, 'out')
    circuit.C('', 'out', circuit.gnd, 250@u_uF)
    circuit.R('load', 'out', circuit.gnd, 1@u_kΩ)

    simulator = Simulator.factory()
    simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
    analysis = simulation.transient(step_time=ac_line.period/200, end_time=ac_line.period*50)

    #r# We can now save, or pickle, our analysis object to a file.

    print(f"Save {pickle_file_path}")
    with open(pickle_file_path, 'wb') as fh:
         pickle.dump(analysis, fh)

if not run_simulation:
    #r# And later, we can reload the data from the file.
    print(f"Save {pickle_file_path}")
    with open(pickle_file_path, 'rb') as fh:
        analysis = pickle.load(fh)
    simulation = analysis.simulation
    print(f"Simulation date: {simulation.simulation_date}")
    print(f"Simulation duration: {simulation.simulation_duration}")
    print(f"Simulator: {simulation.simulator.SIMULATOR} {simulation.simulator_version}")

    #r# The circuit and the simulation parameters was saved.
    print(analysis.simulation.circuit)
    print(str(analysis.simulation))

    figure, ax = plt.subplots(1, figsize=(20, 10))
    ax.plot(analysis.out)
    ax.grid()
    ax.set_xlabel('t [s]')
    ax.set_ylabel('[V]')
    plt.tight_layout()
    plt.show()

    #f# save_figure('figure', 'persistence.png')

####################################################################################################

#<r

# In details, pickle recursively serialize all data referenced in the analysis object, except for
# the simulator object which is replaced by its name, and recreated when the data are unpickled.
# Pickle can only serialize Python data structures out of the box.  This is not the case for the
# simulation object, e.g. the NgSpice wrapper contains a library reference.

# Despite the Pickle method do the job very simply, it has counterparts for its ability to handle
# API modifications.  By design, pickled data should be serialized and de-serialized by the the same
# API version.  Thus Pickle is more suited for data caching or to transport analysis data between
# two processes.

# To summarise, you can use Pickle if you just want to cache data temporarily.  But you should avoid
# to use it to save a simulation output.

#r>

####################################################################################################

#r# HDF5
#r# ----

# If you want to save a simulation output without the counterparts of Pickle, then a powerful
# approach is to use the `HDF5 <https://www.hdfgroup.org/solutions/hdf5>`_ file format.  This format
# was designed to save n-dimensional datasets and will guarantee data could be reloaded later by
# another software.  But this approach needs more work than just pickle data.

# Data must be organised in the HDF5 file.  A good way to do that is to save at least, the Spice
# input, the date of the simulation, the name and version of the simulator, and all the waveforms.

####################################################################################################

#r# Simulation Cache
#r# ----------------

# It can be useful to cache the simulations, for example to avoid to rerun a simulation that
# required a long computing time.

# A simulation cache can be implemented by different ways, from the simpler to the complex one.  A
# first idea, is to use a checksum of the SPICE input, e.g. an algorithm like SHA-256, as a key to
# check if the simulation is already available.  Of course, we can check for a match that the two
# inputs are equal.  Then we can simply save the data in a file identified by the checksum.

####################################################################################################


# data
# data
# simulator identity and release
