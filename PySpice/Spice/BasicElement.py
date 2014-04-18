####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

""" This module implements Spice elements. """

####################################################################################################

from .Netlist import TwoPortElement, TwoPortElementWithValue

####################################################################################################

class Resistor(TwoPortElementWithValue):

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

class Capacitor(TwoPortElementWithValue):

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

class Inductor(TwoPortElementWithValue):

    """

    Inductors::

        LYYYYYYY n+ n- <value> <mname> <nt=val> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
    
    Inductors, dependent on expressions (behavioral inductor)::

        LXXXXXXX n+ n- L='expression' <tc1=value> <tc2=value>
        LXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>

    """
    
    prefix = 'L'

####################################################################################################

class Diode(TwoPortElement):

    """

    Junction Diodes::

        DXXXXXXX n+ n- mname <area=val> <m=val> <pj=val> <off> <ic=vd> <temp=val> <dtemp=val>

    """

    prefix = 'D'

####################################################################################################

class VoltageSource(TwoPortElement):

    """

    Independent Sources for Voltage::

        VXXXXXXX n+ n- <<dc> dc/tran value> <ac <acmag <acphase>>> <distof1 <f1mag <f1phase>>> <distof2 <f2mag <f2phase>>>

    """

    prefix = 'V'

####################################################################################################
# 
# End
# 
####################################################################################################
