####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

""" This module implements Spice elements. """

####################################################################################################

from ..Tools.StringTools import join_list
from .Netlist import (Pin, 
                      IntKeyParameter, FloatKeyParameter, FloatPairKeyParameter,
                      FlagKeyParameter, BoolKeyParameter,
                      ExpressionKeyParameter,
                      Element, ElementWithValue,
                      TwoPinElement, TwoPinElementWithValue, TwoPortElementWithValue)

####################################################################################################

class Resistor(TwoPinElementWithValue):

    """ This class implements a resistor.

    Spice syntax::

        RXXXXXXX n+ n- value <ac=val> <m=val> <scale=val> <temp=val> <dtemp=val> <noisy=0|1>
    

    """

    alias = 'R'
    prefix = 'R'

    ac = FloatKeyParameter('ac')
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    noisy = BoolKeyParameter('noisy')

####################################################################################################

class SemiconductorResistor(TwoPinElementWithValue):

    """ This class implements a Semiconductor resistor.

    Spice syntax::

        RXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <temp=val> <dtemp=val> m=<val> <ac=val> <scale=val> <noisy=0|1>

    """

    alias = 'SemiconductorResistor'
    prefix = 'R'

    # modele
    length = FloatKeyParameter('l')
    width = FloatKeyParameter('w')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    multiplier = IntKeyParameter('m')
    ac = FloatKeyParameter('ac')
    scale = FloatKeyParameter('scale')
    noisy = BoolKeyParameter('noisy')

####################################################################################################

class BehavorialResistor(TwoPinElementWithValue):

    """ This class implements a behavorial resistor.

    Spice syntax::

        RXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        Rxxxxxxx n+ n- R='expression' <tc1=value> <tc2=value>

    """

    alias = 'BehavorialResistor'
    prefix = 'R'

    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')

####################################################################################################

class Capacitor(TwoPinElementWithValue):

    """ This class implements a capacitor.

    Spice syntax::

        CXXXXXXX n+ n- <value> <mname> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>

    """

    alias = 'C'
    prefix = 'C'

    # Modele
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    initial_condition = FloatKeyParameter('init_condition')

####################################################################################################

class SemiconductorCapacitor(TwoPinElementWithValue):

    """ This class implements a semiconductor capacitor.

    Spice syntax::

        CXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
    

    """

    alias = 'SemiconductorCapacitor'
    prefix = 'C'

    # modele
    length = FloatKeyParameter('l')
    width = FloatKeyParameter('w')
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    initial_condition = FloatKeyParameter('init_condition')

####################################################################################################

class BehavorialCapacitor(TwoPinElementWithValue):

    """ This class implements a behavioral capacitor.

    Spice syntax::

        CXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        CXXXXXXX n+ n- C='expression' <tc1=value> <tc2=value>

    """

    alias = 'BehavorialCapacitor'
    prefix = 'C'

    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')

####################################################################################################

class Inductor(TwoPinElementWithValue):

    """ This class implements an inductor.

    Spice syntax::

        LYYYYYYY n+ n- <value> <mname> <nt=val> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>

    """

    alias = 'L'
    prefix = 'L'

    # Modele
    nt = FloatKeyParameter('nt')
    multiplier = IntKeyParameter('m')
    scale = FloatKeyParameter('scale')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')
    initial_condition = FloatKeyParameter('init_condition')

####################################################################################################

class BehavorialInductor(TwoPinElementWithValue):

    """ This class implements a behavioral inductor.

    Spice syntax::

        LXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        LXXXXXXX n+ n- L='expression' <tc1=value> <tc2=value>

    """

    alias = 'BehavorialInductor'
    prefix = 'L'

    tc1 = FloatKeyParameter('tc1')
    tc2 = FloatKeyParameter('tc2')

####################################################################################################

class CoupledInductor(ElementWithValue):

    """ This class implementss a coupled (mutual) inductors.

    Spice syntax::

        KXXXXXXX LYYYYYYY LZZZZZZZ value

    """

    alias = 'CoupledInductor'
    prefix = 'K'

    ##############################################

    def __init__(self, name, inductor_name1, inductor_name2, coupling_factor):

        # Fixme: any pins here
        super(CoupledInductor, self).__init__(name, (),
                                              inductor_name1, inductor_name2, coupling_factor)
        self._inductor_names = (inductor_name1, inductor_name2)

####################################################################################################

class VoltageControlledSwitch(TwoPortElementWithValue):

    """ This class implements a voltage controlled switch.

    Spice syntax::

        SXXXXXXX N+ N- NC+ NC- MODEL <ON><OFF>

    """

    alias = 'VCS'
    prefix = 'S'

####################################################################################################

class CurrentControlledSwitch(TwoPinElementWithValue):

    """ This class implements a current controlled switch.

    Spice syntax::

        WYYYYYYY N+ N- VNAM MODEL <ON><OFF>

    """

    alias = 'CCS'
    prefix = 'W'

####################################################################################################

class VoltageSource(TwoPinElement):

    """ This class implements an independent sources for voltage.

    Spice syntax::

        VXXXXXXX n+ n- <<dc> dc/tran value> <ac <acmag <acphase>>> <distof1 <f1mag <f1phase>>> <distof2 <f2mag <f2phase>>>

    """

    alias = 'V'
    prefix = 'V'

####################################################################################################

class CurrentSource(TwoPinElement):

    """ This class implements an independent sources for current.

    Spice syntax::

       IYYYYYYY N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>> <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>

    """

    alias = 'I'
    prefix = 'I'

####################################################################################################

class VoltageControlledVoltageSource(TwoPortElementWithValue):

    """ This class implements a linear voltage-controlled voltage sources (VCVS).

    Spice syntax::

        EXXXXXXX N+ N- NC+ NC- VALUE

    """

    alias = 'VCVS'
    prefix = 'E'

####################################################################################################

class CurrentControlledCurrentSource(TwoPortElementWithValue):

    """ This class implements a linear current-controlled current sources (CCCS).

    Spice syntax::

       FXXXXXXX N+ N- VNAM VALUE

    """

    alias = 'CCCS'
    prefix = 'F'

####################################################################################################

class VoltageControlledCurrentSource(TwoPortElementWithValue):

    """ This class implements a linear voltage-controlled current sources (VCCS).

    Spice syntax::

        GXXXXXXX N+ N- NC+ NC- VALUE

    """

    alias = 'VCCS'
    prefix = 'G'

####################################################################################################

class CurrentControlledVoltageSource(TwoPortElementWithValue):

    """ This class implements a linear current-controlled voltage sources (ccvs).

    Spice syntax::

        HXXXXXXX n+ n- vnam value

    """

    alias = 'CCVS'
    prefix = 'H'

####################################################################################################

class BehavorialSource(TwoPinElement):

    """ This class implements a behavorial source.

    Spice syntax::

        BXXXXXXX n+ n- <i=expr> <v=expr> <tc1=value> <tc2=value> <temp=value> <dtemp=value>

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

    """

    alias = 'D'
    prefix = 'D'

    area = FloatKeyParameter('area')
    multiplier = IntKeyParameter('m')
    pj = FloatKeyParameter('pj')
    off = FlagKeyParameter('off')
    ic = FloatPairKeyParameter('ic')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')

####################################################################################################

class BipolarJunctionTransistor(Element):

    """ This class implements a bipolar junction transistor.

    Spice syntax::

         QXXXXXXX nc nb ne <ns> mname <area=val> <areac=val> <areab=val> <m=val> <off> <ic=vbe,vce> <temp=val> <dtemp=val>

    """

    # Fixme: off doesn't fit in kwargs !

    alias = 'BJT'
    prefix = 'Q'

    area = FloatKeyParameter('area')
    areac = FloatKeyParameter('areac')
    areab = FloatKeyParameter('areab')
    multiplier = IntKeyParameter('m')
    off = FlagKeyParameter('off')
    ic = FloatPairKeyParameter('ic')
    temperature = FloatKeyParameter('temp')
    device_temperature = FloatKeyParameter('dtemp')

    ##############################################

    def __init__(self, name,
                 collector_node, base_node, emitter_node,
                 model_name,
                 substrate_node=None, # default is ground
                 **kwargs):

        pins = [Pin(self, 'collector', collector_node),
                Pin(self, 'base', base_node),
                Pin(self, 'emitter', emitter_node),]
        if substrate_node is not None:
            self._substrate_pin = Pin(self, 'substrate', substrate_node)
            pins.append(self._substrate_pin)
        else:
            self._substrate_pin = None

        super(BipolarJunctionTransistor, self).__init__(name, pins, model_name, **kwargs)

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
        return self._substrate_pin

####################################################################################################
# 
# End
# 
####################################################################################################
