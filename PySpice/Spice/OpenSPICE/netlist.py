#!/usr/bin/env python3

from arpeggio import ZeroOrMore, EOF, Optional, OneOrMore, RegExMatch, ParserPython, Terminal, NonTerminal
from .components import Resistor, Capacitor, Inductor, VSource, ISource
from .common import v_format, i_format
from abc import ABC, abstractmethod
from re import search

#######################################################################################

# Constants

DEFAULT_TITLE   = "My Circuit"
SI_PREFIXES     = {'Y' : 1e24, 'Z' : 1e21, 'E' : 1e18, 'P' : 1e15, 'T' : 1e12,
                   'G' : 1e9,  'M' : 1e6,  'k' : 1e3,  'h' : 1e2,  'da': 1e1,
                   'd' : 1e-1, 'c' : 1e-2, 'm' : 1e-3, 'u' : 1e-6, 'n' : 1e-9,
                   'p' : 1e-12,'f' : 1e-15,'a' : 1e-18,'z' : 1e-21,'y' : 1e-24}
SI_PREFIX_REGEX = "[" + "|".join(SI_PREFIXES.keys()) + "]"

#######################################################################################

# Top-Level Netlist Rules #

# TODO shouldn't have newline rule, use separator instead: https://textx.github.io/Arpeggio/2.0/configuration/
def netlist():
    return Optional(RegExMatch(".title"), title), OneOrMore(newline), \
           OneOrMore([branch], sep='\n'), OneOrMore(newline), \
           OneOrMore(options, sep='\n'), OneOrMore(newline), \
           [ctrl, tran, op_pt], OneOrMore(newline), end

def branch():
    return [resistor, capacitor, inductor, vsource, isource, extvsource, extisource,
            vccssource, vcvssource, ccvssource, cccssource, behavisource, behavvsource]

def ctrl():
    return control, ZeroOrMore(newline), [op_pt, tran], ZeroOrMore(newline), end

#######################################################################################

# Control Rules #

def control():
    return RegExMatch('.control')

def op_pt():
    return RegExMatch('.op')

def tran():
    return RegExMatch('.tran'), tstep, tstop, Optional(tstart, Optional(tmax)), Optional(uic)

def tstep():
    return _float()

def tstop():
    return _float()

def tstart():
    return _float()

def tmax():
    return _float()

def uic():
    return RegExMatch("uic")

def end():
    return RegExMatch(".end")

def options():
    return RegExMatch(".options"), RegExMatch('.*$')

def _float():
    # Need to account for units, which are parsed later
    # https://stackoverflow.com/questions/336210/regular-expression-for-alphanumeric-and-underscores
    return RegExMatch("[0-9][a-zA-Z0-9_\.]*")

def _int():
    # https://stackoverflow.com/questions/9043551/regex-that-matches-integers-in-between-whitespace-or-start-end-of-string-only
    return RegExMatch(r'\d+')

#######################################################################################

# Text Formatting Classes #

class TextFmt(ABC):
    """
    Abstract class used to generate values for components.
    """
    @abstractmethod
    def gen_txt_str(self, nodes):
        """
        @param node: List of node numbers.
        @return: string (or float) representing component value;
                 may be an equation
        """
        pass

class ResistorTextFmt(TextFmt):
    """
    Resistor class inheriting TextFmt
    """
    def __init__(self, value):
        self.value = value
    def gen_txt_str(self, nodes):
        return unit_parse(self.value)

class CapacitorTextFmt(TextFmt):
    """
    Capacitor class inheriting TextFmt
    """
    def __init__(self, value):
        self.value = value
    def gen_txt_str(self, nodes):
        return unit_parse(self.value)

class InductorTextFmt(TextFmt):
    """
    Inductor class inheriting TextFmt
    """
    def __init__(self, value):
        self.value = value
    def gen_txt_str(self, nodes):
        return unit_parse(self.value)

class VSourceTextFmt(TextFmt):
    """
    VSource class inheriting TextFmt
    """
    def __init__(self, value, srctype="passiveValue"):
        self.value   = value
        self.srctype = srctype
    def gen_txt_str(self, nodes):
        if self.srctype == "passiveValue":
            return unit_parse(self.value)
        elif self.srctype == "pulse":
            # TODO: Include pulse sources with optional
            # parameters. Need to source defaults from
            # ctrl dict
            valarr = self.value.split("|")
            assert len(valarr) >= 9
            assert len(valarr) <= 10
            _v1    = unit_parse(valarr[1])
            _v2    = unit_parse(valarr[2])
            _td    = unit_parse(valarr[3])
            _tr    = unit_parse(valarr[4])
            _tf    = unit_parse(valarr[5])
            _pw    = unit_parse(valarr[6])
            _per   = unit_parse(valarr[7])
            _phase = 0.0 if len(valarr) == 9 else unit_parse(valarr[8])
            cond0 = "t<=(({}))".format(_td)
            cond1 = "(({}))<t<=((({}))+(({})))".format(_td, _td, _tr)
            cond2 = "((({}))+(({})))<t<=((({}))+(({}))+(({})))".format(_td, _tr, _td, _tr, _pw)
            cond3 = "((({}))+(({}))+(({})))<t<=((({}))+(({}))+(({}))+(({})))".format(
                _td, _tr, _pw, _td, _tr, _pw, _tf)
            cond4 = "((({}))+(({}))+(({}))+(({})))<t".format(_td, _tr, _pw, _tf)
            state0 = "(({}))".format(_v1)
            state1 = "((((({}))-(({})))*t)+(((({}))+(({})))*(({})))-((({}))*(({}))))/(({}))".format(
                _v2, _v1, _tr, _td, _v1, _td, _v2, _tr) if _tr != 0.0 else "0"
            state2 = "(({}))".format(_v2)
            state3 = "((((({}))-(({})))*t)+((({}))*(({})))-(((({}))-(({})))*((({}))+(({}))+(({})))))/(({}))".format(
                _v1, _v2, _v2, _tf, _v1, _v2, _td, _tr, _pw, _tf) if _tf != 0.0 else "0"
            state4 = "(({}))".format(_v1)
            return "(({})*({}))+(({})*({}))+(({})*({}))+(({})*({}))+(({})*({}))".format(
                cond0, state0, cond1, state1, cond2, state2, cond3, state3, cond4, state4)
        else:
            assert False

class ISourceTextFmt(TextFmt):
    """
    ISource class inheriting TextFmt
    """
    def __init__(self, value):
        self.value = value
    def gen_txt_str(self, nodes):
        return unit_parse(self.value)

class ExtVSourceTextFmt(TextFmt):
    """
    ExtVSource class inheriting TextFmt
    """
    def __init__(self):
        pass
    def gen_txt_str(self, nodes):
        """
        @return: Returns the string "(get_vsrc(t))". Function defined in
                 solve.py. Used to get value from external voltage source.
        """
        return "(get_vsrc(t))"

class ExtISourceTextFmt(TextFmt):
    """
    ExtISource class inheriting TextFmt
    """
    def __init__(self):
        pass
    def gen_txt_str(self, nodes):
        """
        @return: Returns the string "(get_isrc(t))". Function defined in
                 solve.py. Used to get value from external current source.
        """
        return "(get_isrc(t))"

class VCCSSourceTextFmt(TextFmt):
    """
    VCCSSource class inheriting TextFmt
    """
    def __init__(self, value, node_plus, node_minus):
        self.value = value
        self.node_plus = node_plus
        self.node_minus = node_minus
    def gen_txt_str(self, nodes):
        return "(({})*(({})-({})))".format(self.value, v_format(self.node_plus,  nodes),
                                                       v_format(self.node_minus, nodes))

class VCVSSourceTextFmt(TextFmt):
    """
    VCVSSource class inheriting TextFmt
    """
    def __init__(self, value, node_plus, node_minus):
        self.value = value
        self.node_plus = node_plus
        self.node_minus = node_minus
    def gen_txt_str(self, nodes):
        return "(({})*(({})-({})))".format(self.value, v_format(self.node_plus,  nodes),
                                                       v_format(self.node_minus, nodes))

class CCVSSourceTextFmt(TextFmt):
    """
    CCVSSource class inheriting TextFmt
    """
    def __init__(self, value, branch_plus, branch_minus):
        self.value = value
        self.branch_plus = branch_plus
        self.branch_minus = branch_minus
    def gen_txt_str(self, nodes):
        return "(({})*(({})-({})))".format(self.value, i_format(self.branch_plus,  nodes),
                                                       i_format(self.branch_minus, nodes))

class CCCSSourceTextFmt(TextFmt):
    """
    CCCSSource class inheriting TextFmt
    """
    def __init__(self, value, branch_plus, branch_minus):
        self.value = value
        self.branch_plus = branch_plus
        self.branch_minus = branch_minus
    def gen_txt_str(self, nodes):
        return "(({})*(({})-({})))".format(self.value, i_format(self.branch_plus,  nodes),
                                                       i_format(self.branch_minus, nodes))

class BehavISourceTextFmt(TextFmt):
    """
    BehavISource class inheriting TextFmt
    """
    def __init__(self, value):
        self.value = value
    def gen_txt_str(self, nodes):
        val = self.value
        for n in nodes:
            val = val.replace('v({})'.format(n), v_format(n, nodes))
        # TODO does ngspice support i(*) notation? I don't think so.
        return "({})".format(val)

class BehavVSourceTextFmt(TextFmt):
    """
    BehavVSource class inheriting TextFmt
    """
    def __init__(self, value):
        self.value = value
    def gen_txt_str(self, nodes):
        val = self.value
        for n in nodes:
            val = val.replace('v({})'.format(n), v_format(n, nodes))
        # TODO does ngspice support i(*) notation? I don't think so.
        return "({})".format(val)

#######################################################################################

# Component Rules #

def inductor():
    return lcomponent, node, node, passiveValue, Optional(ic)

def capacitor():
    return ccomponent, node, node, passiveValue, Optional(ic)

def resistor():
    return rcomponent, node, node, passiveValue

def vsource():
    return vcomponent, node, node, Optional(dc, _float), [pulse, passiveValue]

def isource():
    return icomponent, node, node, passiveValue

def extvsource():
    return vcomponent, node, node, dc, _float, external

def extisource():
    return icomponent, node, node, dc, _float, external

def vccssource():
    return vccscomponent, node, node, node, node, passiveValue

def vcvssource():
    return vcvscomponent, node, node, node, node, passiveValue

def ccvssource():
    return ccvscomponent, node, node, node, node, passiveValue

def cccssource():
    return cccscomponent, node, node, node, node, passiveValue

def behavisource():
    return behavsrccomponent, node, node, iequalsbehav

def behavvsource():
    return behavsrccomponent, node, node, vequalsbehav

#######################################################################################

# Generic Branch Rules #

def node():
    return RegExMatch(r'[a-zA-Z0-9_]+')

def passiveValue():
    return RegExMatch(r'[0-9\.][a-zA-Z0-9_\.]*')

def stateVarValue():
    # Need to account for units, which are parsed later
    # https://stackoverflow.com/questions/336210/regular-expression-for-alphanumeric-and-underscores
    return RegExMatch("[a-zA-Z0-9_\.]*")

def newline():
    return RegExMatch(r'\n')

def ic():
    return RegExMatch(r'ic='), stateVarValue

def dc():
    return RegExMatch(r'dc|DC')

def external():
    return RegExMatch(r'external')

def iequalsbehav():
    return RegExMatch(r'i='), behavexpr

def vequalsbehav():
    return RegExMatch(r'v='), behavexpr

def behavexpr():
    # TODO
    return RegExMatch('.*$')

#######################################################################################

# VSource Rules #

def pulse():
    return RegExMatch("PULSE\("), _float(), _float(), Optional(_float()), \
           Optional(_float()), Optional(_float()), Optional(_float()), \
           Optional(_float()), Optional(_float()), RegExMatch("\)")

#######################################################################################

# Component Identifier Rules #

def ccomponent():
    return RegExMatch(r'C[a-zA-Z0-9_]*')

def rcomponent():
    return RegExMatch(r'R[a-zA-Z0-9_]*')

def lcomponent():
    return RegExMatch(r'L[a-zA-Z0-9_]*')

def vcomponent():
    return RegExMatch(r'V[a-zA-Z0-9_]*')

def icomponent():
    return RegExMatch(r'I[a-zA-Z0-9_]*')

def vccscomponent():
    return RegExMatch(r'G[a-zA-Z0-9_]*')

def vcvscomponent():
    return RegExMatch(r'E[a-zA-Z0-9_]*')

def ccvscomponent():
    return RegExMatch(r'H[a-zA-Z0-9_]*')

def cccscomponent():
    return RegExMatch(r'F[a-zA-Z0-9_]*')

def behavsrccomponent():
    return RegExMatch(r'B[a-zA-Z0-9_]*')


#######################################################################################

# Misc. Rules

def title():
    # https://stackoverflow.com/questions/336210/regular-expression-for-alphanumeric-and-underscores
    # TODO include accented characters, like in Thevenin
    return RegExMatch("[a-zA-Z0-9_' ]*")

#######################################################################################

# Unit Parsing

def oom(x):
    """
    @param x: string of SI unit suffix
    @return: float representing SI order of magnitude (hence, "oom")
    """
    assert len(x) == 1
    # https://en.wikipedia.org/wiki/Metric_prefix
    return SI_PREFIXES[x]

def unit_parse(x):
    """
    @param x: string with SI unit suffix
    @return: value float
    """
    groups = search(r'(\d+\.*\d*)({})?([a-zA-z])*'.format(SI_PREFIX_REGEX), x).groups()
    return float(groups[0]) * 1.00 if not groups[1] or not groups[2] else float(groups[0]) * oom(groups[1])

#######################################################################################

# Parsing Functions #

def filter_terms(ptree):
    """
    Remove all newline terminals from Arpeggio parse tree.

    @param ptree: Arpeggio parse tree
    @return: list of parse tree nodes
    """
    return [_ for _ in ptree if _.value != "\n"]

# TODO: should we use explicit == as opposed to in?
def nonterm_is_tran(nonterm):
    """
    Check if nonterminal node in Arpeggio parse tree is a tran.

    @param nonterm: nonterminal node from Arpeggio parse tree
    @return: True/False boolean
    """
    return (type(nonterm) == NonTerminal) and ("tran" in nonterm.name)

def nonterm_is_branch(nonterm):
    """
    Check if nonterminal node in Arpeggio parse tree is a branch.

    @param nonterm: nonterminal node from Arpeggio parse tree
    @return: True/False boolean
    """
    return (type(nonterm) == NonTerminal) and ("branch" in nonterm.name)

def nonterm_is_ctrl(nonterm):
    """
    Check if nonterminal node in Arpeggio parse tree is a ctrl.

    @param nonterm: nonterminal node from Arpeggio parse tree
    @return: True/False boolean
    """
    return (type(nonterm) == NonTerminal) and ("ctrl" in nonterm.name)

def nonterm_is_title(nonterm):
    """
    Check if nonterminal node in Arpeggio parse tree is a title.

    @param nonterm: nonterminal node from Arpeggio parse tree
    @return: True/False boolean
    """
    return (type(nonterm) == NonTerminal) and ("title" in nonterm.name)

def gen_dict_from_tran_node(tran_node):
    """
    Generate a control dictionary for transient simulations. The entries are
    the following:

    "test_type" key: maps to the string literal "tran"
    "tstep" key: maps to a float literal for the timestep size
    "tstop" key: maps to a float literal for the simulation end time
    "tstart" key: maps to a float literal for the simulation start time
    "tmax" key: maps to a float literal for the max timestep size; used
                for variable timestepping, which OpenSPICE currently does
                not support
    "uic" key: maps to the string literal "uic" if defined, excluded otherwise;
               tells the user whether
               initial conditions are to be used; currently unused and
               assumed to be "uic"

    @param tran_node: nonterminal node from Arpeggio parse tree
    @return: control dictionary for nonterm
    """
    assert nonterm_is_tran(tran_node)
    tran_node_rule_names = [n.rule_name for n in tran_node]
    tran_d = {"test_type" : "tran",
              "tstep"     : unit_parse(tran_node[1].value),
              "tstop"     : unit_parse(tran_node[2].value)}
    if "tstart" in tran_node_rule_names:
        tran_d["tstart"] = unit_parse(tran_node[3].value)
        if "tmax" in tran_node_rule_names:
            tran_d["tmax"] = unit_parse(tran_node[4].value)
            if "uic" in tran_node_rule_names:
                tran_d["uic"] = tran_node[5].value
        else:
            if "uic" in tran_node_rule_names:
                tran_d["uic"] = tran_node[4].value
    else:
        if "uic" in tran_node_rule_names:
            tran_d["uic"] = tran_node[3].value
    return tran_d

def gen_dict_from_ctrl(nonterm):
    """
    Generate a control dictionary. The entries vary depending on the
    type of test. For operating point simulations, there is only
    one key, "test_type", which maps to the string literal "op_pt".

    Please see gen_dict_from_tran_node for details on the control
    dictionary for transient simulations.

    @param nonterm: nonterminal node from Arpeggio parse tree
    @return: control dictionary for nonterm
    """
    assert nonterm_is_ctrl(nonterm)
    rule_names = [n.rule_name for n in nonterm]
    if "op_pt" in rule_names:
        return {"test_type" : "op_pt"}
    elif "tran" in rule_names:
        return gen_dict_from_tran_node(nonterm[rule_names.index("tran")])
    else:
        assert False

def gen_dict_from_branch(nonterm, branch_idx):
    """
    Generate a branch dictionary. The entries are:

    "component" key: maps to class of component on branch (ex: Resistor)
    "node_plus" key: maps to positive side node (ex: '1')
    "node_minus" key: maps to negative side node (ex: '11')
    "value" key: maps to component value (ex: 0.0); value can also be
                 an expression involving the x vector; the Python "exec"
                 function is used in solve.py to evaluate the equations,
                 so you could use arbitrary Python code here if you wanted to
                 do so. However, do so at your own risk.

                 These values are implemented using TextFmt
                 classes. Call their gen_txt_str method to get the string or
                 float value.
    "branch_idx" key: maps to component value (ex: 2)

    @param nonterm: nonterminal node from Arpeggio parse tree
    @param branch_idx: index for branch in circuit
    @return: branch dictionary for nonterm
    """
    assert nonterm_is_branch(nonterm)
    if   nonterm[0].rule_name == "resistor":
        assert len(nonterm[0]) == 4
        return {"component"  : Resistor,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : ResistorTextFmt(nonterm[0][3].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "capacitor":
        assert len(nonterm[0]) == 4 or len(nonterm[0]) == 5
        _cap = {"component"  : Capacitor,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : CapacitorTextFmt(nonterm[0][3].value),
                "branch_idx" : branch_idx}
        if len(nonterm[0]) == 5:
            _cap["ic"] = unit_parse(nonterm[0][4][1].value)
        return _cap
    elif nonterm[0].rule_name == "inductor":
        assert len(nonterm[0]) == 4 or len(nonterm[0]) == 5
        _ind = {"component"  : Inductor,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : InductorTextFmt(nonterm[0][3].value),
                "branch_idx" : branch_idx}
        if len(nonterm[0]) == 5:
            _ind["ic"] = unit_parse(nonterm[0][4][1].value)
        return _ind
    elif nonterm[0].rule_name == "vsource":
        assert len(nonterm[0]) == 4 or len(nonterm[0]) == 6
        vsrcvalidx = 3 if len(nonterm[0]) == 4 else 5
        return {"component"  : VSource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : VSourceTextFmt(nonterm[0][vsrcvalidx].value,
                                      srctype=nonterm[0][vsrcvalidx].rule_name),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "isource":
        assert len(nonterm[0]) == 4
        return {"component"  : ISource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : ISourceTextFmt(nonterm[0][3].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "extvsource":
        assert len(nonterm[0]) == 6
        return {"component"  : VSource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : ExtVSourceTextFmt(),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "extisource":
        assert len(nonterm[0]) == 6
        return {"component"  : ISource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : ExtISourceTextFmt(),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "vccssource":
        assert len(nonterm[0]) == 6
        return {"component"  : ISource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : VCCSSourceTextFmt(nonterm[0][5].value,
                                                 nonterm[0][3].value,
                                                 nonterm[0][4].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "vcvssource":
        assert len(nonterm[0]) == 6
        return {"component"  : VSource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : VCVSSourceTextFmt(nonterm[0][5].value,
                                                 nonterm[0][3].value,
                                                 nonterm[0][4].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "ccvssource":
        assert len(nonterm[0]) == 6
        return {"component"  : VSource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : CCVSSourceTextFmt(nonterm[0][5].value,
                                                 nonterm[0][3].value,
                                                 nonterm[0][4].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "cccssource":
        assert len(nonterm[0]) == 6
        return {"component"  : ISource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : CCCSSourceTextFmt(nonterm[0][5].value,
                                                 nonterm[0][3].value,
                                                 nonterm[0][4].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "behavisource":
        assert len(nonterm[0]) == 4
        return {"component"  : ISource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : BehavISourceTextFmt(nonterm[0][3][1].value),
                "branch_idx" : branch_idx}
    elif nonterm[0].rule_name == "behavvsource":
        assert len(nonterm[0]) == 4
        return {"component"  : VSource,
                "node_plus"  : nonterm[0][1].value,
                "node_minus" : nonterm[0][2].value,
                "value"      : BehavVSourceTextFmt(nonterm[0][3][1].value),
                "branch_idx" : branch_idx}
    else:
        assert False

def gen_data_dicts(ptree):
    """
    Consume parse tree and generate a data dictionary. The data dictionary
    takes on the following form:

    "branches" key: maps to a list of branch dictionaries, documented
    in the gen_dict_from_branch function

    "nodes" key: maps to a list of all the nodes in the circuit
    (ex: ['1', '2'])

    "ctrl" key: maps to a control dictionary, documented in the
    gen_dict_from_ctrl function

    "title" key: maps to the netlist title string

    @param ptree: array of nodes from Arpeggio parse tree for input
                  netlist
    @return: data dictionary for netlist
    """
    branches = [_ for _ in ptree if nonterm_is_branch(_)]
    branches = [gen_dict_from_branch(_, branch_idx) for branch_idx,_ in \
        enumerate(branches)]
    nodes    = sorted(set().union(*[{d["node_plus"], d["node_minus"]} for d \
        in branches]))
    assert "0" in nodes
    nodes.remove("0")
    [_.update({"value" : _["value"].gen_txt_str(nodes)}) for _ in branches]
    ctrl     = [gen_dict_from_ctrl(_) for _ in ptree if nonterm_is_ctrl(_)]
    if len(ctrl) == 0:
        # TODO: need a cleaner way of dealing with ctrl statements
        ctrl  = [{"test_type" : "op_pt"}    for _ in ptree if _.value == ".op"]
        ctrl += [gen_dict_from_tran_node(_) for _ in ptree if ".tran" \
            in _.value]
        # TODO support multiple test types?
        assert len(ctrl) == 1
    titles   = [_.value for _ in ptree if nonterm_is_title(_)]
    assert len(titles) == 1 or len(titles) == 0
    if len(titles) == 0:
        titles.append(DEFAULT_TITLE)
    return {"branches" : branches, "nodes" : nodes, "ctrl" : ctrl, \
            "title" : titles[0]}

def parse(txt):
    """
    Parse a SPICE netlist string and return a data dictionary.

    @param txt: string containing file contents of SPICE netlist
    @return: data dictionary for netlist
    """
    parser = ParserPython(netlist, ws='\t\r ')
    ptree = parser.parse(txt)
    return gen_data_dicts(filter_terms(ptree))

#######################################################################################

if __name__ == "__main__":
    with open("dep_sources.cir", "r") as f:
        print(parse(f.read()))
