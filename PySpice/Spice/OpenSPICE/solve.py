#!/usr/bin/env python3

from abc import ABC, abstractmethod
from scipy.optimize import root
from functools import partial

# TODO remove globals. Need a cleaner way of implementing these functions.

get_vsrc_data = None
get_isrc_data = None
send_data     = None

def set_get_vsrc(x):
    """
    Set the get_vsrc_data function, which is ultimately called by
    get_vsrc for use in external voltage sources.

    @param x: A function that takes 4 arguments. The first argument is
    a list with a single float entry. This entry will be overwritten
    by the function x. After x returns, it will be an array of one element,
    the external voltage value. The second argument is a float representing
    the simulation time. The final two arguments are hardcoded to zeros
    for now.
    """
    global get_vsrc_data
    get_vsrc_data = x

def set_get_isrc(x):
    """
    Set the get_isrc_data function, which is ultimately called by
    get_isrc for use in external voltage sources.

    @param x: A function that takes 4 arguments. The first argument is
    a list with a single float entry. This entry will be overwritten
    by the function x. After x returns, it will be an array of one element,
    the external current value. The second argument is a float representing
    the simulation time. The final two arguments are hardcoded to zeros
    for now.
    """
    global get_isrc_data
    get_isrc_data = x

def set_send_data(x):
    """
    Set the send_data function. This function is used to relay data back
    to PySpice.

    @param x: A function that takes 3 arguments. The first argument is
    a dictionary. This format of the dictionary varies depending on the
    simulation. For operating point sims, dictionary maps 'V(*)', where *
    is a node name, and 'i(*)', where * is a branch index, to the simulation
    solution. Transient sims are the same except the first entry in dictionary
    is "t" mapping to the given timestep. send_data function would be called
    once per timestep.
    The second argument is the length of that dictionary. The last argument
    is hardcoded to zero for now.
    """
    global send_data
    send_data = x

def get_vsrc(t):
    """
    Get voltage from external voltage source.

    @param t: simulation timestep
    @return: External voltage source value at timestep t as a float
    """
    # TODO - support all get_vsrc_data args
    global get_vsrc_data
    voltage = [0.0]
    get_vsrc_data(voltage, t, 0, 0)
    return voltage[0]

def get_isrc(t):
    """
    Get current from external current source.

    @param t: simulation timestep
    @return: External current source value at timestep t as a float
    """
    # TODO - support all get_vsrc_data args
    global get_isrc_data
    current = [0.0]
    get_isrc_data(current, t, 0, 0)
    return current[0]

#################################################################

# Top-Level Classes for Strategy Pattern #

class SolverStrategy(ABC):
    """
    Abstract class used to implement a "strategy" for solving system of
    equations for given simulation type.
    """
    @abstractmethod
    def solve_eqns(self):
        """
        Implement this function in subclasses to solve equations. Should
        call send_data if defined to relay data back to PySpice.

        @return: solution for equations 
        """
        pass

class OpPtSolverStrategy(SolverStrategy):
    """
    Operating point solver strategy subclass
    """
    def __init__(self, eqns, nodes):
        """
        Initializer function.

        @param eqns: list of equation strings containing x[*] list entries
        @param nodes: list of nodes
        """
        self.eqns  = eqns
        self.nodes = nodes
    def solve_eqns(self):
        """
        Solve equations.

        @return: solution array; first entries are node voltages; the latter
        entries are branch currents
        """
        # https://bugs.python.org/issue4831
        ldict = locals()
        s = "y = lambda x : [" + ",".join(self.eqns) + "]"
        exec(s, globals(), ldict)
        y = ldict['y']
        # t = 0.00
        # TODO Why does this not work?
        soln = [root(y, [1.00] * len(self.eqns)).x.tolist()]
        # TODO need more proper send_data call
        if send_data:
            send_data(dict(zip(['V({})'.format(n) for n in self.nodes] + \
                               ['i({})'.format(l) for l in range(len(self.eqns) - len(self.nodes))], soln[0])), len(soln[0]), 0)
        return soln

class TransientSolverStrategy(SolverStrategy):
    """
    Transient solver strategy subclass
    """
    def __init__(self, eqns, ctrl, nodes):
        """
        Initializer function.

        @param eqns: list of equation strings containing x[*] list entries
        @param nodes: list of nodes
        """
        self.eqns  = eqns
        self.ctrl  = ctrl
        self.nodes = nodes
    def solve_eqns(self):
        """
        Solve equations.

        @return: solution array; first entries are node voltages; the latter
        entries are branch currents
        """
        # https://bugs.python.org/issue4831
        ldict = locals()
        s = "y = lambda x , x_prev , t , dt : [" + ",".join(self.eqns) + "]"
        exec(s, globals(), ldict)
        y = ldict['y']
        soln = []
        seed = []
        x_soln = [0.00] * len(self.eqns)
        t     = float(self.ctrl["tstart"])
        dt    = float(self.ctrl["tstep"])
        tstop = float(self.ctrl["tstop"])
        while t < tstop:
            _y = lambda x : partial(y, x_prev=x_soln, t=t, dt=dt)(x)
            tmp_soln = root(_y, [1.00] * len(self.eqns))
            x_soln = tmp_soln.x.tolist()
            # TODO: Replace tolerance check with value found in options
            # assert all([abs(z) < 1e-3 for z in _y(x_soln)])
            seed = [t] + x_soln
            data_dict_keys = ['time'] + ['V({})'.format(n) for n in self.nodes] + \
                                        ['i({})'.format(l) for l in range(len(self.eqns) - len(self.nodes))]
            assert len(data_dict_keys) == len(seed)
            data_dict = dict(zip(data_dict_keys, seed))
            if send_data:
                send_data(data_dict, len(seed), 0)
            soln.append(seed)
            t += dt
        return soln

if __name__ == "__main__":
    import netlist
    import eqnstr
    with open("op_pt_divider.cir", "r") as f:
        txt = f.read()
        n = netlist.parse(txt)
        eqn = eqnstr.gen_eqns_top(n)
        strat = OpPtSolverStrategy(eqn)
    with open("tran.cir", "r") as f:
        txt = f.read()
        n = netlist.parse(txt)
        eqn = eqnstr.gen_eqns_top(n)
        # TODO need to support multiple test types?
        strat = TransientSolverStrategy(eqn, n["ctrl"][0])
