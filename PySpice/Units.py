####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

def tera(x):
    """ T Tera 1e12 """
    # return x*1e12
    return str(x) + 'T'

def giga(x):
    """ G Giga 1e9 """
    # return x*1e9
    return str(x) + 'G'

def mega(x):
    """ Meg Mega 1e6 """
    # return x*1e6
    return str(x) + 'Meg'

def kilo(x):
    """ K Kilo 1e3 """
    # return x*1e3
    return str(x) + 'k'

def mil(x):
    """ mil Mil 25.4e-6 """
    # return x*25.4e-6
    return str(x) + 'mil'

def milli(x):
    """ m milli 1e-3 """
    # return x*1e-3
    return str(x) + 'm'

def micro(x):
    """ u micro 1e-6 """
    # return x*1e-6
    return str(x) + 'u'

def nano(x):
    """ n nano 1e-9 """
    # return x*1e-9
    return str(x) + 'n'

def pico(x):
    """ p pico 1e-12 """
    # return x*1e-12
    return str(x) + 'p'

def femto(x):
    """ f femto 1e-15 """
    # return x*1e-15
    return str(x) + 'f'

####################################################################################################
# 
# End
# 
####################################################################################################
