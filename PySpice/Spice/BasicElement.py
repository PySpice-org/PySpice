####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

"""This module implements SPICE circuit elements.

See Ngspice documentation for details.

.. warning:: Some elements are partially implemented.

.. note:: It would be nice to have an use-full and working documentation in the interactive environment.

"""

####################################################################################################

from ..Tools.StringTools import join_list
from .Netlist import Pin, Element, TwoPinElement, TwoPortElement
from .ElementParameter import (
    BoolKeyParameter,
    ElementNamePositionalParameter,
    ExpressionKeyParameter,
    ExpressionPositionalParameter,
    FlagParameter,
    FloatKeyParameter,
    FloatPairKeyParameter,
    FloatPositionalParameter,
    InitialStatePositionalParameter,
    IntKeyParameter,
    ModelPositionalParameter,
    )

####################################################################################################

class SubCircuitElement(Element):

    """ This class implements a sub-circuit.

    Spice syntax::

        XYYYYYY node1 node2 ... subcircuit_name

    Attributes:

      :attr:`subcircuit_name`
    
    """

    alias = 'X'
    prefix = 'X'

    subcircuit_name = ElementNamePositionalParameter(position=0, key_parameter=False)

    ##############################################

    def __init__(self, name, subcircuit_name, *nodes):

        pins = [Pin(self, None, node) for node in nodes]

        super(SubCircuitElement, self).__init__(name, pins, subcircuit_name)

####################################################################################################

class Resistor(TwoPinElement):

    """ This class implements a resistor.

    Spice syntax::

        RXXXXXXX n+ n- value <ac=val> <m=val> <scale=val> <temp=val> <dtemp=val> <noisy=0|1>

    Attributes:

      :attr:`resistance`

      :attr:`ac`

      :attr:`multiplier`

      :attr:`scale`

      :attr:`temperature`

      :attr:`device_temperature`

      :attr:`noisy`

    """

    alias = 'R'
    prefix = 'R'

    resistance = FloatPositionalParameter(position=0, key_parameter=False)
    ac = FloatKeyParameter('ac')
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    noisy = BoolKeyParameter('noisy')

####################################################################################################

class SemiconductorResistor(TwoPinElement):

    """ This class implements a Semiconductor resistor.

    Spice syntax::

        RXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <temp=val> <dtemp=val> m=<val> <ac=val> <scale=val> <noisy=0|1>

    Attributes:

      :attr:`resistance`

      :attr:`model`

      :attr:`length`

      :attr:`width`

      :attr:`temperature`

      :attr:`device_temperature`

      :attr:`multiplier`

      :attr:`ac`

      :attr:`scale`

      :attr:`noisy`

    """

    alias = 'SemiconductorResistor'
    prefix = 'R'

    resistance = FloatPositionalParameter(position=0, key_parameter=False)
    model = ModelPositionalParameter(position=1, key_parameter=True)
    length = FloatKeyParameter('l')
    width = FloatKeyParameter('w')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    multiplier = IntKeyParameter('m')
    ac = FloatKeyParameter('ac')
    scale = FloatKeyParameter('scale')
    noisy = BoolKeyParameter('noisy')

####################################################################################################

class BehavorialResistor(TwoPinElement):

    """ This class implements a behavorial resistor.

    Spice syntax::

        RXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        Rxxxxxxx n+ n- R='expression' <tc1=value> <tc2=value>

    Attributes:

      :attr:`resistance_expression`

      :attr:`tc1`

      :attr:`tc2`

    """

    alias = 'BehavorialResistor'
    prefix = 'R'

    resistance_expression = ExpressionPositionalParameter(position=0, key_parameter=False)
    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')

####################################################################################################

class Capacitor(TwoPinElement):

    """ This class implements a capacitor.

    Spice syntax::

        CXXXXXXX n+ n- <value> <mname> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>

    Attributes:

      :attr:`capacitance`

      :attr:`model`

      :attr:`multiplier`

      :attr:`scale`

      :attr:`temperature`

      :attr:`device_temperature`

      :attr:`initial_condition`

    """

    alias = 'C'
    prefix = 'C'

    capacitance = FloatPositionalParameter(position=0, key_parameter=False)
    model = ModelPositionalParameter(position=1, key_parameter=True)
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    initial_condition = FloatKeyParameter('ic')

####################################################################################################

class SemiconductorCapacitor(TwoPinElement):

    """ This class implements a semiconductor capacitor.

    Spice syntax::

        CXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>

    Attributes:

      :attr:`capacitance`

      :attr:`model`

      :attr:`length`

      :attr:`width`

      :attr:`multiplier`

      :attr:`scale`

      :attr:`temperature`

      :attr:`device_temperature`

      :attr:`initial_condition`

    """

    alias = 'SemiconductorCapacitor'
    prefix = 'C'

    capacitance = FloatPositionalParameter(position=0, key_parameter=False)
    model = ModelPositionalParameter(position=1, key_parameter=True)
    length = FloatKeyParameter('l')
    width = FloatKeyParameter('w')
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    initial_condition = FloatKeyParameter('ic')

####################################################################################################

class BehavorialCapacitor(TwoPinElement):

    """ This class implements a behavioral capacitor.

    Spice syntax::

        CXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        CXXXXXXX n+ n- C='expression' <tc1=value> <tc2=value>

    Attributes:

      :attr:`capacitance_expression`

      :attr:`tc1`

      :attr:`tc2`

    """

    alias = 'BehavorialCapacitor'
    prefix = 'C'

    capacitance_expression = ExpressionPositionalParameter(position=0, key_parameter=False)
    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')

####################################################################################################

class Inductor(TwoPinElement):

    """ This class implements an inductor.

    Spice syntax::

        LYYYYYYY n+ n- <value> <mname> <nt=val> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>

    Attributes:

      :attr:`inductance`

      :attr:`model`

      :attr:`nt`

      :attr:`multiplier`

      :attr:`scale`

      :attr:`temperature`

      :attr:`device_temperature`

      :attr:`initial_condition`

    """

    alias = 'L'
    prefix = 'L'

    inductance = FloatPositionalParameter(position=0, key_parameter=False)
    model = ModelPositionalParameter(position=1, key_parameter=True)
    nt = FloatKeyParameter('nt')
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    initial_condition = FloatKeyParameter('ic')

####################################################################################################

class BehavorialInductor(TwoPinElement):

    """ This class implements a behavioral inductor.

    Spice syntax::

        LXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        LXXXXXXX n+ n- L='expression' <tc1=value> <tc2=value>

    Attributes:

      :attr:`inductance_expression`

      :attr:`tc1`

      :attr:`tc2`

    """

    alias = 'BehavorialInductor'
    prefix = 'L'

    inductance_expression = ExpressionPositionalParameter(position=0, key_parameter=False)
    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')

####################################################################################################

class CoupledInductor(Element):

    """ This class implementss a coupled (mutual) inductors.

    Spice syntax::

        KXXXXXXX LYYYYYYY LZZZZZZZ value

    Attributes:

      :attr:`inductor1`

      :attr:`inductor2`

      :attr:`coupling_factor`

    """

    alias = 'CoupledInductor'
    prefix = 'K'

    inductor1 = ElementNamePositionalParameter(position=0, key_parameter=False)
    inductor2 = ElementNamePositionalParameter(position=1, key_parameter=False)
    coupling_factor = FloatPositionalParameter(position=2, key_parameter=False)

 ##############################################

    def __init__(self, name, inductor_name1, inductor_name2, coupling_factor):

        # Fixme: any pins here
        super(CoupledInductor, self).__init__(name, (),
                                              inductor_name1, inductor_name2, coupling_factor)
        self._inductor_names = (inductor_name1, inductor_name2)

####################################################################################################

class VoltageControlledSwitch(TwoPortElement):

    """ This class implements a voltage controlled switch.

    Spice syntax::

        SXXXXXXX n+ n- nc+ nc- model <on> <off>

    Attributes:

      :attr:`model`

      :attr:`initial_state`

    """

    alias = 'VCS'
    prefix = 'S'

    model = ModelPositionalParameter(position=0, key_parameter=True)
    initial_state = InitialStatePositionalParameter(position=1, key_parameter=True)

####################################################################################################

class CurrentControlledSwitch(TwoPinElement):

    """ This class implements a current controlled switch.

    Spice syntax::

        WYYYYYYY n+ n- vname model <on> <off>

    Attributes:

      :attr:`source`

      :attr:`model`

      :attr:`initial_state`

    """

    alias = 'CCS'
    prefix = 'W'

    source = ElementNamePositionalParameter(position=0, key_parameter=True)
    model = ModelPositionalParameter(position=1, key_parameter=True)
    initial_state = InitialStatePositionalParameter(position=2, key_parameter=True)

####################################################################################################

class VoltageSource(TwoPinElement):

    """ This class implements an independent sources for voltage.

    Spice syntax::

        VXXXXXXX n+ n- <<dc> dc/tran value> <ac <acmag <acphase>>> <distof1 <f1mag <f1phase>>> <distof2 <f2mag <f2phase>>>

    Attributes:

      :attr:`dc_value`

    """

    alias = 'V'
    prefix = 'V'

    # Fixme: ngspice manual doesn't describe well the syntax
    dc_value = FloatPositionalParameter(position=0, key_parameter=False)

####################################################################################################

class CurrentSource(TwoPinElement):

    """ This class implements an independent sources for current.

    Spice syntax::

       IYYYYYYY n+ n- <<dc> dc/tran value> <ac <acmag <acphase>>> <distof1 <f1mag <f1phase>>> <distof2 <f2mag <f2phase>>>

    Attributes:

      :attr:`dc_value`

    """

    alias = 'I'
    prefix = 'I'

    # Fixme: ngspice manual doesn't describe well the syntax
    dc_value = FloatPositionalParameter(position=0, key_parameter=False)

####################################################################################################

class VoltageControlledVoltageSource(TwoPortElement):

    """ This class implements a linear voltage-controlled voltage sources (VCVS).

    Spice syntax::

        EXXXXXXX n+ n- nc+ nc- value

    Attributes:

      :attr:`voltage_gain`

    """

    alias = 'VCVS'
    prefix = 'E'

    voltage_gain = ExpressionPositionalParameter(position=0, key_parameter=False)

####################################################################################################

class CurrentControlledCurrentSource(TwoPortElement):

    """ This class implements a linear current-controlled current sources (CCCS).

    Spice syntax::

       FXXXXXXX n+ n- vname value

    Attributes:

      :attr:`source`

      :attr:`current_gain`
    
    """

    alias = 'CCCS'
    prefix = 'F'

    source = ElementNamePositionalParameter(position=0, key_parameter=True)
    current_gain = ExpressionPositionalParameter(position=1, key_parameter=False)

####################################################################################################

class VoltageControlledCurrentSource(TwoPortElement):

    """ This class implements a linear voltage-controlled current sources (VCCS).

    Spice syntax::

        GXXXXXXX n+ n- nc+ nc- value

    Attributes:

      :attr:`transconductance`

    """

    alias = 'VCCS'
    prefix = 'G'

    transconductance = ExpressionPositionalParameter(position=0, key_parameter=False)

####################################################################################################

class CurrentControlledVoltageSource(TwoPortElement):

    """ This class implements a linear current-controlled voltage sources (ccvs).

    Spice syntax::

        HXXXXXXX n+ n- vname value

    Attributes:

      :attr:`source`

      :attr:`transresistance`

    """

    alias = 'CCVS'
    prefix = 'H'

    source = ElementNamePositionalParameter(position=0, key_parameter=True)
    transresistance = ExpressionPositionalParameter(position=1, key_parameter=False)

####################################################################################################

class BehavorialSource(TwoPinElement):

    """ This class implements a behavorial source.

    Spice syntax::

        BXXXXXXX n+ n- <i=expr> <v=expr> <tc1=value> <tc2=value> <temp=value> <dtemp=value>

    Attributes:

      :attr:`current_expression`

      :attr:`voltage_expression`

      :attr:`tc1`

      :attr:`tc2`

      :attr:`temperature`

      :attr:`device_temperature`

    """

    alias = 'BehavorialSource'
    prefix = 'B'

    current_expression = ExpressionKeyParameter('i')
    voltage_expression = ExpressionKeyParameter('v')
    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')

####################################################################################################

class NonLinearVoltageSource(TwoPinElement):

    """ This class implements a non linear voltage source.

    Spice syntax::

        EXXXXXXX n+ n- vol='expr'
        EXXXXXXX n+ n- value={expr}
        Exxx n1 n2 TABLE {expression}=(x0,y0) (x1,y1) (x2,y2)
        EXXXX n+ n- ( POLY (nd) ) nc1+ nc1- ( nc2+ nc2- ... ) p0 ( p1 ... )
        Laplace

    Attributes:

    """

    alias = 'NonLinearVoltageSource'
    prefix = 'E'

    ##############################################

    def __init__(self, name,
                 node_plus, node_minus,
                 expression=None,
                 table=None):

        super(NonLinearVoltageSource, self).__init__(name, node_plus, node_minus)

        self.expression = expression
        self.table = table

    ##############################################

    def __str__(self):

        spice_element = self.format_node_names()
        if self.table is not None:
            # TABLE {expression} = (x0, y0) (x1, y1) ...
            table = ['({}, {})'.format(x, y) for x, y in self.table]
            spice_element += ' TABLE {%s} = %s' % (self.expression, join_list(table)) 
        return spice_element

####################################################################################################

class Diode(TwoPinElement):

    """ This class implements a junction diode.

    Spice syntax::

        DXXXXXXX n+ n- mname <area=val> <m=val> <pj=val> <off> <ic=vd> <temp=val> <dtemp=val>

    Attributes:

      :attr:`model`

      :attr:`area`

      :attr:`multiplier`

      :attr:`pj`

      :attr:`off`

      :attr:`ic`

      :attr:`temperature`

      :attr:`device_temperature`

    """

    alias = 'D'
    prefix = 'D'

    model = ModelPositionalParameter(position=0, key_parameter=True)
    area = FloatKeyParameter('area')
    multiplier = IntKeyParameter('m')
    pj = FloatKeyParameter('pj')
    off = FlagParameter('off')
    ic = FloatPairKeyParameter('ic')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')

####################################################################################################

class BipolarJunctionTransistor(Element):

    """ This class implements a bipolar junction transistor.

    Spice syntax::

         QXXXXXXX nc nb ne <ns> mname <area=val> <areac=val> <areab=val> <m=val> <off> <ic=vbe,vce> <temp=val> <dtemp=val>

    Attributes:

      :attr:`model`

      :attr:`area`

      :attr:`areac`

      :attr:`areab`

      :attr:`multiplier`

      :attr:`off`

      :attr:`ic`

      :attr:`temperature`

      :attr:`device_temperature`

    """

    # Fixme: off doesn't fit in kwargs !

    alias = 'BJT'
    prefix = 'Q'

    model = ModelPositionalParameter(position=0, key_parameter=True)
    area = FloatKeyParameter('area')
    areac = FloatKeyParameter('areac')
    areab = FloatKeyParameter('areab')
    multiplier = IntKeyParameter('m')
    off = FlagParameter('off')
    ic = FloatPairKeyParameter('ic')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')

    ##############################################

    def __init__(self, name,
                 collector_node, base_node, emitter_node,
                 substrate_node=None, # default is ground
                 **kwargs):

        pins = [Pin(self, 'collector', collector_node),
                Pin(self, 'base', base_node),
                Pin(self, 'emitter', emitter_node),]
        if substrate_node is not None:
            self._substrate_pin = Pin(self, 'substrate', substrate_node)
            pins.append(self._substrate_pin)

        super(BipolarJunctionTransistor, self).__init__(name, pins, **kwargs)

    ##############################################

    @property
    def collector(self):
        return self.pins[0]

    ##############################################

    @property
    def base(self):
        return self.pins[1]

    ##############################################

    @property
    def emitter(self):
        return self.pins[2]

    ##############################################

    @property
    def substrate(self):
        try:
            return self.pins[3]
        except IndexError:
            return None

####################################################################################################
# 
# End
# 
####################################################################################################
