####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################
#
# op: value
# transient: time
# dc: v-sweep
# ac: frequency 
# sens: element parameters
#
# Probes
#
# Nodes:
#   Voltage versus gnd
#   real or complex
#   static or (temporale/transient, v-sweep, frequency)
#
#   static waveform: (node->, unit, value)
#   waveform: (node->, unit, values, abscissa->)
#
#   analysis.1.v !
#   analysis.in.v !
#   analysis['1'].v
#   analysis.n1.v
#
# Source:
#   Current
#
#   analysis.Vinput.i
#
# Vinput -> lower case

# axe.plot(x, y, *args, **kwargs)
#
###################################################################################################

####################################################################################################
#
# Analysis versus Simulation
#
####################################################################################################

####################################################################################################

import numpy as np

####################################################################################################

class WaveForm(np.ndarray):

    ##############################################

    def __new__(cls, name, unit, data, title=None, abscissa=None):

        obj = np.asarray(data).view(cls)

        obj.name = str(name)
        obj.unit = str(unit)
        obj.title = title # str(title)
        obj.abscissa = abscissa

        return obj

    ##############################################

    def __array_finalize__(self, obj):

        if obj is None:
            return

        self.name = getattr(obj, 'name', None)
        self.unit = getattr(obj, 'unit', None)
        self.title = getattr(obj, 'title', None)
        self.abscissa = getattr(obj, 'abscissa', None)

    ##############################################

    def __repr__(self):

        return 'variable {self.name} [{self.unit}]'.format(self=self)

    ##############################################

    def __str__(self):

        if self.title is not None:
            return self.title
        else:
            return '{self.name} [{self.unit}]'.format(self=self)

####################################################################################################

class Analysis(object):

    ##############################################

    def __init__(self, nodes=(), branches=(), elements=()):

        # Fixme: to func?
        self.nodes = {waveform.name:waveform for waveform in nodes}
        self.branches = {waveform.name:waveform for waveform in branches}
        self.elements = {waveform.name:waveform for waveform in elements}

    ##############################################

    def __getitem__(self, name):

        if name in self.nodes:
            return self.nodes[name]
        elif name in self.branches:
            return self.branches[name]
        elif name in self.elements:
            return self.elements[name]
        else:
            raise IndexError(name)

    ##############################################

    def __getattr__(self, name):
        
        try:
            return self.__getitem__(name)
        except IndexError:
            raise AttributeError(name)

####################################################################################################

class OperatingPoint(Analysis):
    pass

####################################################################################################

class SensitivityAnalysis(Analysis):

    ##############################################

    def __init__(self, elements):

        super(SensitivityAnalysis, self).__init__(elements=elements)

####################################################################################################

class DcAnalysis(Analysis):

    ##############################################

    def __init__(self, v_sweep, nodes, branches):

        super(DcAnalysis, self).__init__(nodes, branches)

        self._v_sweep = v_sweep

    ##############################################

    @property
    def v_sweep(self):
        pass

####################################################################################################

class AcAnalysis(Analysis):

    ##############################################

    def __init__(self, frequency, nodes, branches):

        super(AcAnalysis, self).__init__(nodes, branches)

        self._frequency = frequency

    ##############################################

    @property
    def frequency(self):
        return self._frequency

####################################################################################################

class TransientAnalysis(Analysis):

    ##############################################

    def __init__(self, time, nodes, branches):

        super(TransientAnalysis, self).__init__(nodes, branches)

        self._time = time

    ##############################################

    @property
    def time(self):
        return self._time

####################################################################################################
# 
# End
# 
####################################################################################################
