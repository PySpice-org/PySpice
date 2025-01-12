#!/usr/bin/env python3

from abc import ABC, abstractmethod
from .common import i_format

#################################################################

# Top-Level Classes for Strategy Pattern #

class EqnStrStrategy(ABC):
    """
    Abstract class that represents a simulations strategy (e.g. operating
    point, transient, etc.). Class contains methods for generating
    equations for the given strategy.
    """

    @abstractmethod
    def gen_eqn_from_branch(self, _b, _n):
        """
        Generate formatted equation string for the given circuit branch.

        @param _b: Branch dictionary
        @param _n: List of node numbers.
        @return: Formatted equation string.
        """
        pass

    def gen_eqns(self, branch_dicts, nodes):
        """
        Generate list of formatted equation strings. First portion of list is
        branch equations given by underlying Component classes. The second
        portion of list is KCL equations. KCL equations each represent all of
        the currents flowing into/out of a given node. So, there should be
        one KCL equation for each node and one branch equation for each branch.

        @param branch_dicts: List of branch dictionaries
        @param nodes: List of node numbers.
        @return: List of formatted equation strings.
        """
        return [self.gen_eqn_from_branch(_b, nodes) for _b in branch_dicts] + \
                self.gen_kcl_eqns(branch_dicts, nodes)

    def gen_kcl_eqns(self, branch_dicts, nodes):
        """
        Generate list of formatted equation strings for KCL equations.

        @param branch_dicts: List of branch dictionaries
        @param nodes: List of node numbers.
        @return: List of formatted equation strings.
        """
        kcl_dict = dict(zip(nodes, [[]] * len(nodes)))
        for b in branch_dicts:
            if b["node_plus"] != "0":
                l_plus  = len(kcl_dict[b["node_plus"]])
                other_l = [len(kcl_dict[n]) for n in kcl_dict.keys() \
                                                  if n != b["node_plus"]]
                kcl_dict[b["node_plus"]]  = kcl_dict[b["node_plus"]] + \
                        ["-({})".format(i_format(b["branch_idx"],  nodes))]
                assert len(kcl_dict[b["node_plus"]])  == l_plus  + 1
                assert [len(kcl_dict[n]) for n in kcl_dict.keys() \
                                         if n != b["node_plus"]] == other_l
            if b["node_minus"] != "0":
                l_minus = len(kcl_dict[b["node_minus"]])
                other_l = [len(kcl_dict[n]) for n in kcl_dict.keys() \
                                                  if n != b["node_minus"]]
                kcl_dict[b["node_minus"]] = kcl_dict[b["node_minus"]] + \
                       ["+({})".format(i_format(b["branch_idx"],  nodes))]
                assert len(kcl_dict[b["node_minus"]]) == l_minus + 1
                assert [len(kcl_dict[n]) for n in kcl_dict.keys() \
                                         if n != b["node_minus"]] == other_l
        return ["".join(v) for v in kcl_dict.values()]

#################################################################

# Strategies #

class EqnStrOpPtStrategy(EqnStrStrategy):
    """
    Strategy class for operating point simulations.
    """

    def __init__(self):
        """
        Empty initializer method.
        """
        pass

    def gen_eqn_from_branch(self, _b, _n):
        """
        Generate formatted equation string for the given circuit branch.

        @param _b: Branch dictionary
        @param _n: List of node numbers.
        @return: Formatted equation string.
        """
        return _b["component"].op_pt_eqn(_b, _n)

class EqnStrTransientStrategy(EqnStrStrategy):
    """
    Strategy class for transient simulations.
    """

    def __init__(self):
        """
        Empty initializer method.
        """
        pass

    def gen_eqn_from_branch(self, _b, _n):
        """
        Generate formatted equation string for the given circuit branch.

        @param _b: Branch dictionary
        @param _n: List of node numbers.
        @return: Formatted equation string.
        """
        return _b["component"].trans_eqn(_b, _n)

def gen_eqns_top(parse_dict):
    """
    Generate formatted equation string for the given circuit.

    @param parse_dict: Dictionary from parser
    @return: List of formatted equation strings.
    """
    # TODO need to support multiple test types?
    # TODO disable ic if uic arg is not provided to trans
    # TODO wrap logic in a context type
    if   parse_dict["ctrl"][0]["test_type"] == "op_pt":
        return EqnStrOpPtStrategy().gen_eqns(parse_dict["branches"], \
                                             parse_dict["nodes"])
    elif parse_dict["ctrl"][0]["test_type"] == "tran" :
        return EqnStrTransientStrategy().gen_eqns(parse_dict["branches"], \
                                                  parse_dict["nodes"])
    else:
        assert False

#################################################################

if __name__ == "__main__":
    import netlist
    # with open("op_pt.cir", "r") as f:
    #     print(gen_eqns_top(netlist.parse(f.read())))
    # with open("tran.cir", "r") as f:
    #     print(gen_eqns_top(netlist.parse(f.read())))
    with open("op_pt_divider.cir", "r") as f:
        txt = f.read()
        print(gen_eqns_top(netlist.parse(txt)))
