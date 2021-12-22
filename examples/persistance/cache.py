####################################################################################################

#r# ==================
#r#  Simulation Cache
#r# ==================

# It can be useful to cache the simulations, for example to avoid to rerun a simulation that
# required a long computing time.

# A simulation cache can be implemented by different ways, from the simpler to the complex one.  A
# first idea, is to use a checksum of the SPICE input, e.g. an algorithm like SHA-256, as a key to
# check if the simulation is already available.  Of course, we can check for a match that the two
# inputs are equal.  Then we can simply save the data in a file identified by the checksum.

####################################################################################################

from pathlib import Path

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Cache import SimulationCache

from SimulateCircuit import simulate_circuit

####################################################################################################

cache = SimulationCache()
print(cache.directory)

analysis = simulate_circuit()
print(cache.simulation_key(analysis.simulation))

# data
# data
# simulator identity and release
