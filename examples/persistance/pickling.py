#r# ==========
#r#  Pickling
#r# ==========

#r# This example explains how to pickle a simulation.

#r# The first method to save simulation data, it is to use the `pickle <https://docs.python.org/3/library/pickle.html>`_
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

from PySpice import plot

from SimulateCircuit import simulate_circuit

####################################################################################################

pickle_file_path = Path('pickled-simulation.data')
run_simulation = not pickle_file_path.exists()

####################################################################################################

if run_simulation:
    analysis = simulate_circuit()

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
    print(simulation.circuit)
    print(str(simulation))

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
