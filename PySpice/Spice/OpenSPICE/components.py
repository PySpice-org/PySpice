#!/usr/bin/env python3

from abc import ABC, abstractmethod
from .common import v_format, i_format, dv_format, di_format

class Component(ABC):
    """
    Abstract class that represents an electrical component. Class contains
    methods for formatting equation strings for use in the final system
    of equations solved at each simulation timestep.
    """

    @staticmethod
    @abstractmethod
    def op_pt_eqn(branch, node):
        """
        Return an equation string for the component. The equation string is
        the left hand side of f(x) = 0, where x is an array. The initial
        elements of the array are the node voltages. The latter portion of the
        array is a list of the branch currents in the circuit. A system of
        these equation strings is solved at each timestep so we can acquire the
        voltages and currents.

        f(x) usually represents the IV characteristic of a component.
        For instance, if g(I) = V for the component of interest,
        f(x) = g(I) - V = 0 is a valid equation string. It would usually be
        represented in the form g(I) - V. Similarly, h(V) = I -->
        f(x) = h(V) - I = 0 would also work. It is usually just some condition
        that must hold by definition for this component.

        As of now, only components with two terminals are considered.

        op_pt_eqn in particular focuses only on operating point simulations.
        So, users are advised to avoid using any x_prev expressions.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        pass
    @staticmethod
    @abstractmethod
    def trans_eqn(branch, node):
        """
        Same as op_pt_eqn except for transient simulations. Feel free
        to use x_prev in these.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        pass

class Resistor(Component):
    """
    Class that represents a resistor. Class contains
    methods for formatting equation strings for use in the final system
    of equations solved at each simulation timestep.
    """

    @staticmethod
    def op_pt_eqn(branch, node):
        """
        Generate op point equation for resistor.

        Equation format: ((x[node_plus voltage index] -
                          (x[node_minus voltage index])) -
                          ((x[branch current])*(resistance)))

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "(({})-({}))-(({})*({}))".format(v_format(branch["node_plus"], \
                                                         node),
                                                v_format(branch["node_minus"],\
                                                         node),
                                                i_format(branch["branch_idx"],\
                                                         node),
                                                         branch["value"])
    @staticmethod
    def trans_eqn(branch, node):
        """
        Generate transient equation for resistor.

        Equation format: ((x[node_plus voltage index] -
                          (x[node_minus voltage index])) -
                          ((x[branch current])*(resistance)))

        Note: Equation is the same as op point case.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "(({})-({}))-(({})*({}))".format(v_format(branch["node_plus"], \
                                                         node),
                                                v_format(branch["node_minus"],\
                                                         node),
                                                i_format(branch["branch_idx"],\
                                                         node),
                                                         branch["value"])

class Capacitor:
    """
    Class that represents a capacitor. Class contains
    methods for formatting equation strings for use in the final system
    of equations solved at each simulation timestep.
    """

    @staticmethod
    def op_pt_eqn(branch, node):
        """
        Generate op point equation for capacitor.

        Equation format: ((x[branch current]) - (0.00))

        Note: At steady state, capacitors act as open circuits. Therefore,
        the current must be 0.00.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "(({})-({}))".format(i_format(branch["branch_idx"],\
                                             node), 0.00)
    @staticmethod
    def trans_eqn(branch, node):
        """
        Generate transient equation for the capacitor.

        There are two cases. The first case is t = 0.00, the simulation start
        point. Here, the equation string is as follows:

        "(((x[node_plus index])-(x[node_minus index]))-(initial voltage))"

        This is the initial condition. The second case is t != 0.00, or the
        "else" case:

        "(((x[branch current])*dt)-((capacitance value)*
            ((dv[node_plus index])-(dv[node_minus index]))))"

        This is a rearrangement of the differential equation I = CdV/dt -->
        Idt - CdV = 0.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        if "ic" in branch.keys():
            # TODO: modify to support nonzero start times
            prefix = "((({})-({}))-({})) if t == 0.00 else ".format(\
                                    v_format(branch["node_plus"],  node),\
                                    v_format(branch["node_minus"], node),\
                                    branch["ic"])
        else:
            prefix = ""
        return prefix + "((({})*dt)-(({})*(({})-({}))))".format(\
                                    i_format(branch["branch_idx"], node),\
                                             branch["value"],\
                                    dv_format(branch["node_plus"],  node),\
                                    dv_format(branch["node_minus"], node))

class Inductor:
    """
    Class that represents an inductor. Class contains
    methods for formatting equation strings for use in the final system
    of equations solved at each simulation timestep.
    """

    @staticmethod
    def op_pt_eqn(branch, node):
        """
        Generate op point equation for inductor.

        Equation format: (((x[node_plus index]) - (x[node_minus index])) -
                           (0.00))

        Note: At steady state, inductors act as short circuits. Therefore,
        the branch voltage drop must be 0.00.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "((({})-({}))-({}))".format(v_format(branch["node_plus"], \
                                                    node),
                                           v_format(branch["node_minus"], \
                                                    node), 0.00)
    @staticmethod
    def trans_eqn(branch, node):
        """
        Generate transient equation for the inductor.

        There are two cases. The first case is t = 0.00, the simulation start
        point. Here, the equation string is as follows:

        "((x[branch current])-(initial current value))"

        This is the initial condition. The second case is t != 0.00, or the
        "else" case:

        "((((x[node_plus index])-(x[node_minus index]))*dt)-
           ((inductance value)*((di))))"

        This is a rearrangement of the differential equation V = Ldi/dt -->
        Vdt - Ldi = 0.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        if "ic" in _b.keys():
            # TODO: modify to support nonzero start times
            prefix = "(({})-({})) if t == 0.00 else ".format(\
                                i_format(branch["branch_idx"], node), \
                                branch["ic"])
        else:
            prefix = ""
        return prefix + "(((({})-({}))*dt)-(({})*(({}))))".format(\
                                v_format(branch["node_plus"],  node), \
                                v_format(branch["node_minus"], node), \
                                         branch["value"], \
                                di_format(branch["branch_idx"], node))

class VSource:
    """
    Class that represents a voltage source. Class contains
    methods for formatting equation strings for use in the final system
    of equations solved at each simulation timestep.
    """

    @staticmethod
    def op_pt_eqn(branch, node):
        """
        Generate op point equation for voltage source.

        Equation format: (((x[node_plus index]) - (x[node_minus index])) -
                           (voltage value))

        In other words, the branch voltage drop must be the source's voltage
        value.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "((({})-({}))-({}))".format(v_format(branch["node_plus"], \
                                                    node),
                                           v_format(branch["node_minus"],\
                                                    node),
                                                    branch["value"])
    @staticmethod
    def trans_eqn(branch, node):
        """
        Generate op point equation for voltage source.

        Equation format: (((x[node_plus index]) - (x[node_minus index])) -
                           (voltage value))

        In other words, the branch voltage drop must be the source's voltage
        value.
        
        Note: Equation is the same as op point case.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "((({})-({}))-({}))".format(v_format(branch["node_plus"], \
                                                    node),
                                           v_format(branch["node_minus"],\
                                                    node),
                                                    branch["value"])

class ISource:
    """
    Class that represents a current source. Class contains
    methods for formatting equation strings for use in the final system
    of equations solved at each simulation timestep.
    """

    @staticmethod
    def op_pt_eqn(branch, node):
        """
        Generate op point equation for current source.

        Equation format: ((x[branch current]) - (current value))

        In other words, the branch current must be the source's current
        value.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "(({})-({}))".format(i_format(branch["branch_idx"], node),
                                             branch["value"])
    @staticmethod
    def trans_eqn(branch, node):
        """
        Generate op point equation for current source.

        Equation format: ((x[branch current]) - (current value))

        In other words, the branch current must be the source's current
        value.

        Note: Equation is the same as op point case.

        @param branch: Branch dictionary for the component's branch.
        @param node: List of node numbers.
        @return: Formatted equation string.
        """
        return "(({})-({}))".format(i_format(branch["branch_idx"], node),
                                             branch["value"])
