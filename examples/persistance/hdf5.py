#r# ======
#r#  HDF5
#r# ======

#r# This example explains how to save a simulation to a HDF5 file.

####################################################################################################

#r# If you want to save a simulation output without the counterparts of Pickle, then a powerful
#r# approach is to use the `HDF5 <https://www.hdfgroup.org/solutions/hdf5>`_ file format.  This format
#r# was designed to save n-dimensional datasets and will guarantee data could be reloaded later by
#r# another software.  But this approach needs more work than just pickle data.

#r# Data must be organised in the HDF5 file.  A good way to do that is to save at least, the Spice
#r# input, the date of the simulation, the name and version of the simulator, and all the waveforms.

####################################################################################################

from pathlib import Path

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Export.Hdf5 import Hdf5File

from SimulateCircuit import simulate_circuit

####################################################################################################

analysis = simulate_circuit()

#r# Create a HDF5 file containing the simulation setting and result.
path = Path('simulation.hdf5')
Hdf5File.save(analysis, path)

#r# Dump the HDF5 file content using the command :code:`h5dump simulation.hdf5`
