#!/usr/bin/env python3

def v_format(s, n, prev=False):
    """
    Return a string of the form "(x[i])", where i is the index of x
    corresponding to the node number s. (ex: n = ['3', '1', '7'].
    If s is '7', then the return value will be "(x[2])"). "x[i]" corresponds
    to the voltage at node s (whose index in list n is i).

    @param s: Node number as a string
    @param n: List of node numbers.
    @param prev: Optional argument defaulted to False. If set to True,
                 then string will be of the form "(x_prev[i])" instead of
                 "(x[i])". This refers to the voltage in the previous timestep
                 as opposed to the current.
    @return: Formatted string "(x[i])", where i is s's positional index in n.
             This will represent the voltage at node s in the final formatted
             equations.
    """
    outer = "x" if not prev else "x_prev"
    return "({}[{}])".format(outer, n.index(s)) if s != "0" else "(0.00)"

def i_format(s, n, prev=False):
    """
    Return a string of the form "(x[i])", where i is the index of x
    corresponding to the branch number s. (ex: n = ['3', '1', '7'].
    If s is '1', then the return value will be "(x[4])").

    The first len(n) entries of x are the node voltages. The subsequent
    entries are the branch currents. s is considered to be an index of
    the second portion of the list x, which contains the branch currents.

    @param s: Branch index as a string
    @param n: List of node numbers.
    @param prev: Optional argument defaulted to False. If set to True,
                 then string will be of the form "(x_prev[i])" instead of
                 "(x[i])". This refers to the current in the previous timestep
                 as opposed to the current.
    @return: Formatted string "(x[i])".
             This will represent the current at branch s in the final formatted
             equations.
    """
    outer = "x" if not prev else "x_prev"
    return "({}[{}])".format(outer, len(n) + int(s))

def dv_format(s, n):
    """
    Return a string of the form "((x[i])-(x_prev[i]))". This represents an
    incremental change in voltage at node s from one timestep to the next.

    @param s: Node number as a string
    @param n: List of node numbers.
    @return: Formatted string "((x[i])-(x_prev[i]))", where i is s's positional
             index in n.
    """
    return "(({})-({}))".format(v_format(s, n, prev=False),
                                v_format(s, n, prev=True ))


def di_format(s, n):
    """
    Return a string of the form "((x[i])-(x_prev[i]))". This represents an
    incremental change in current at branch s from one timestep to the next.

    @param s: Node number as a string
    @param n: List of node numbers.
    @return: Formatted string "((x[i])-(x_prev[i]))".
    """
    return "(({})-({}))".format(i_format(s, n, prev=False),
                                i_format(s, n, prev=True ))
