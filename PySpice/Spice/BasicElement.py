####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

""" This module implements Spice elements. """

####################################################################################################

from ..Tools.StringTools import join_list
from .Netlist import (Pin, Element, ElementWithValue,
                      TwoPinElement, TwoPinElementWithValue, TwoPortElementWithValue)

####################################################################################################

class Resistor(TwoPinElementWithValue):

    """

    Resistors::

        RXXXXXXX n+ n- value <ac=val> <m=val> <scale=val> <temp=val> <dtemp=val> <noisy=0|1>
    
    Semiconductor Resistors::

        RXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <temp=val> <dtemp=val> m=<val> <ac=val> <scale=val> <noisy=0|1>
    
    Resistors, dependent on expressions (behavioral resistor)::

        Rxxxxxxx n+ n- R='expression' <tc1=value> <tc2=value>
        RXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>

    """

    prefix = 'R'

####################################################################################################

class Capacitor(TwoPinElementWithValue):

    """

    Capacitors::

        CXXXXXXX n+ n- <value> <mname> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
    
    Semiconductor Capacitors::

        CXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
    
    Capacitors, dependent on expressions (behavioral capacitor)::

        CXXXXXXX n+ n- C='expression' <tc1=value> <tc2=value>
        CXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>

    """

    prefix = 'C'

####################################################################################################

class Inductor(TwoPinElementWithValue):

    """

    Inductors::

        LYYYYYYY n+ n- <value> <mname> <nt=val> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
    
    Inductors, dependent on expressions (behavioral inductor)::

        LXXXXXXX n+ n- L='expression' <tc1=value> <tc2=value>
        LXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>

    """
    
    prefix = 'L'

####################################################################################################

class CoupledInductor(ElementWithValue):

    """ Coupled (Mutual) Inductors

    Spice syntax:

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

    """

    Spice syntax:

        SXXXXXXX N+ N- NC+ NC- MODEL <ON><OFF>

    """

    alias = 'VCS'
    prefix = 'S'

####################################################################################################

class CurrentControlledSwitch(TwoPinElementWithValue):

    """

    Spice syntax:

        WYYYYYYY N+ N- VNAM MODEL <ON><OFF>

    """

    alias = 'CCS'
    prefix = 'W'

####################################################################################################

class VoltageSource(TwoPinElement):

    """

    Independent Sources for Voltage::

        VXXXXXXX n+ n- <<dc> dc/tran value> <ac <acmag <acphase>>> <distof1 <f1mag <f1phase>>> <distof2 <f2mag <f2phase>>>

    """

    prefix = 'V'

####################################################################################################

class CurrentSource(TwoPinElement):

    """

    Independent Sources for Current::

       IYYYYYYY N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>> <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>

    """

    prefix = 'I'

####################################################################################################

class VoltageControlledVoltageSource(TwoPortElementWithValue):

    """

    Linear Voltage-Controlled Voltage Sources (VCVS)::

        EXXXXXXX N+ N- NC+ NC- VALUE

    """

    alias = 'VCVS'
    prefix = 'E'

####################################################################################################

class CurrentControlledCurrentSource(TwoPortElementWithValue):

    """

    Linear Current-Controlled Current Sources (CCCS)::

       FXXXXXXX N+ N- VNAM VALUE

    """

    alais = 'CCCS'
    prefix = 'F'

####################################################################################################

class VoltageControlledCurrentSource(TwoPortElementWithValue):

    """

    Linear Voltage-Controlled Current Sources (VCCS)::

        GXXXXXXX N+ N- NC+ NC- VALUE

    """

    alias = 'VCCS'
    prefix = 'G'

####################################################################################################

class CurrentControlledVoltageSource(TwoPortElementWithValue):

    """

    Linear Current-Controlled Voltage Sources (CCVS)::

        HXXXXXXX n+ n- vnam value

    """

    alias = 'CCVS'
    prefix = 'H'

####################################################################################################

class BehavorialSource(TwoPinElement):

    """ B source (ASRC)

    Spice syntax::

        BXXXXXXX n+ n- <i=expr> <v=expr> <tc1=value> <tc2=value> <temp=value> <dtemp=value>

    """

    prefix = 'B'

    ##############################################

    def __init__(self, name,
                 node_plus, node_minus,
                 current_expression=None, voltage_expression=None,
                 tc1=None, tc2=None,
                 temperature=None, dtemp=None):

        kwargs = {'i':current_expression, 'v':voltage_expression,
                  'tc1':tc1, 'tc2':tc2,
                  'temp':temperature, 'dtemp':dtemp,
                 }
        
        super(BehavorialSource, self).__init__(name, node_plus, node_minus, **kwargs)

####################################################################################################

class NonLinearVoltageSource(TwoPinElement):

    """

    Spice syntax::

        EXXXXXXX n+ n- vol='expr'
        EXXXXXXX n+ n- value={expr}
        Exxx n1 n2 TABLE {expression}=(x0,y0) (x1,y1) (x2,y2)
        EXXXX n+ n- ( POLY (nd) ) nc1+ nc1- ( nc2+ nc2- ... ) p0 ( p1 ... )
        Laplace

    """

    prefix = 'E'
    __dont_register_prefix__ = True

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

        spice_element = self.format_name_nodes()
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

    prefix = 'D'

####################################################################################################

class BipolarJunctionTransistor(Element):

    """ This class implements a bipolar junction transistor.

    Spice syntax::

         QXXXXXXX nc nb ne <ns> mname <area=val> <areac=val> <areab=val> <m=val> <off> <ic=vbe,vce> <temp=val> <dtemp=val>

    """

    # Fixme: off doesn't fit in kwargs !

    alias = 'BJT'
    prefix = 'Q'

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
