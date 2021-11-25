####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = ["Hdf5File"]

####################################################################################################

# File structure
#   using h5ls -r simulation.hdf5
#
# /                        Group
# /version                 Dataset {SCALAR}
# /simulation              Group
# /abscissas               Group
# /abscissas/time          Dataset {10038}
# /branches                Group
# /branches/e.xdz.ev1      Dataset {10038}
# /branches/...
# /elements                Group
# /internal_parameters     Group
# /nodes                   Group
# /nodes/1                 Dataset {10038}
# /nodes/...

# h5dump -g "/simulation" simulation.hdf5
# h5dump -d "/abscissas/time" simulation.hdf5
# h5dump -d "/nodes/1" simulation.hdf5

####################################################################################################

import pickle

import numpy as np

# https://docs.h5py.org/en/stable/index.html
import h5py

####################################################################################################

class Hdf5File:

    _VERSION = 1

    ##############################################

    @classmethod
    def save(cls, analysis, path):
        self = cls(path, 'w')
        self._save(analysis)

    ##############################################

    def __init__(self, path, mode=None):
        self._file = h5py.File(path, mode)

    ##############################################

    def _save(self, analysis):
        self._file["version"] = self._VERSION

        simulation = analysis.simulation
        group = self._file.create_group("simulation")
        attrs = group.attrs
        attrs["simulator"] = simulation.simulator.SIMULATOR
        attrs["simulator_version"] = simulation.simulator_version
        attrs["simulation_date"] = str(simulation.simulation_date)
        attrs["simulation_duration"] = str(simulation.simulation_duration)
        attrs["spice_circuit"] = str(simulation.circuit)
        attrs["spice_simulation"] = str(simulation) # Fixme: remove desk
        # https://docs.h5py.org/en/stable/strings.html#how-to-store-raw-binary-data
        attrs["pickled_simulation"] = np.void(pickle.dumps(simulation))

        self._abscissa = self._file.create_group("abscissas")
        for list_name in ("nodes", "branches", "elements", "internal_parameters"):
            group = self._file.create_group(list_name)
            for waveform in getattr(analysis, list_name).values():
                self._add_waveform(group, waveform)

    ##############################################

    def _add_waveform_common(self, group, waveform):
        dset = group.create_dataset(
            waveform.name,
            data=waveform,
            compression="gzip", compression_opts=9
            # compression="lzf
        )
        attrs = dset.attrs
        attrs["unit"] = str(waveform.unit)
        return dset

    ##############################################

    def _add_abscissa(self, abscissa):
        # Fixme: is time always unique ???
        # See https://docs.h5py.org/en/stable/high/group.html#hard-links
        if abscissa.name not in self._abscissa:
            # self._abscissa[abscissa.name] = abscissa
            self._add_waveform_common(self._abscissa, abscissa)
        return self._abscissa[abscissa.name]

    ##############################################

    def _add_waveform(self, group, waveform):
        dset = self._add_waveform_common(group, waveform)
        attrs = dset.attrs
        if waveform.title:
            attrs["title"] = waveform.title
        attrs["abscissa"] = self._add_abscissa(waveform.abscissa).ref
