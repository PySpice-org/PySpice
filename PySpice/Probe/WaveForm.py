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

class WaveForm(object):

    ##############################################

    def __init__(self, name, unit, data, title=None, abscissa=None):

        self.name = str(name)
        self.unit = str(unit)
        self.title = title # str(title)
        self._data = data
        self.abscissa = abscissa

    ##############################################

    def __repr__(self):

        return 'variable {self.name} [{self.unit}]'.format(self=self)

    ##############################################

    def __str__(self):

        if self.title is not None:
            return self.title
        else:
            return '{self.name} [{self.unit}]'.format(self=self)

    ##############################################

    def __float__(self):

        return self._data

    ##############################################

    @property
    def v(self):
        return self._data

    ##############################################

    def __pos__(self):
        
        return self.__class__(name=self.name,
                              unit=self.unit,
                              data=self._data,
                              abscissa=self.abscissa,
                             )

    ##############################################

    def __neg__(self):
        
        return self.__class__(name=self.name,
                              unit=self.unit,
                              data=-self._data,
                              abscissa=self.abscissa,
                             )

    ##############################################

    def __add__(self, other):
        
        if isinstance(other, self.__class__):
            if self.abscissa != other.abscissa:
                raise NameError("Abscissa is different")
            name = self.name + ' + ' + other.name
            data = self._data + other._data
        else:
            name = self.name + ' + ?'
            data = self._data + other
        return self.__class__(name=name,
                              unit=self.unit,
                              data=data,
                              abscissa=self.abscissa,
                             )

    ##############################################

    def __sub__(self, other):
        
        if isinstance(other, self.__class__):
            if self.abscissa != other.abscissa:
                raise NameError("Abscissa is different")
            name = self.name + ' - ' + other.name
            data = self._data - other._data
        else:
            name = self.name + ' - ?'
            data = self._data - other
        return self.__class__(name=name,
                              unit=self.unit,
                              data=data,
                              abscissa=self.abscissa,
                             )

    ##############################################

    def __mul__(self, other):
        
        if isinstance(other, self.__class__):
            if self.abscissa != other.abscissa:
                raise NameError("Abscissa is different")
            name = self.name + ' * ' + other.name
            data = self._data * other._data
        else:
            name = self.name + ' * ?'
            data = self._data * other
        return self.__class__(name=name,
                              unit=None, # Fixme:
                              data=data,
                              abscissa=self.abscissa,
                             )

    ##############################################

    def __div__(self, other):
        
        if isinstance(other, self.__class__):
            if self.abscissa != other.abscissa:
                raise NameError("Abscissa is different")
            name = self.name + ' / ' + other.name
            data = self._data / other._data
        else:
            name = self.name + ' / ?'
            data = self._data / other
        return self.__class__(name=name,
                              unit=None, # Fixme
                              data=data,
                              abscissa=self.abscissa,
                             )

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
