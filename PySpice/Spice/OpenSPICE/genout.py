#!/usr/bin/env python3

from datetime import datetime
from array    import array

def gen_out_txt(raw_fname, title, test_type, soln, sorted_nodes):
    """
    Dump an output file with the simulation results. The output file only
    contains node voltage solutions and not currents, though soln contains
    currents as well.

    @param raw_fname: name of file that contains simulation results
    @param title: simulation title
    @param test_type: the type of simulation run (e.g. "tran" or "op_pt")
    @param soln: simulation results; should contain one entry for each timestep
                 for transient simulations and one entry for operating point
                 simulations. Each entry contains a list whose initial entry
                 is the simulation time (for transient sims only).
                 The next entries are the node voltages
                 in order, and the final entries are the branch currents in
                 order.
    @param sorted_nodes: List of nodes from smallest to greatest (e.g.
                         ["1", "2", "4"])
    """
    assert len(soln) > 0
    assert all([len(_) == len(soln[i-1]) for i,_ in enumerate(soln) if i != 0])
    assert len(soln[0]) > len(sorted_nodes)
    spice_raw_file_txt  = "Title: {}\n".format(title)
    spice_raw_file_txt += "Date: {}\n".format(datetime.today().strftime('%c'))
    spice_raw_file_txt += "Plotname: {}\n".format("Transient Analysis" \
                if test_type == "tran" else "Operating Point")
    spice_raw_file_txt += "Flags: {}\n".format("real")
    spice_raw_file_txt += "No. Variables: {}\n".format((test_type == "tran") +\
                len(sorted_nodes))
    spice_raw_file_txt += "No. Points: {}\n".format(len(soln))
    spice_raw_file_txt += "Variables:\n"
    spice_raw_file_txt += "\t0\ttime\ttime\n" if test_type == "tran" else ""
    spice_raw_file_txt += "".join(["\t{}\t{}\tvoltage\n".format(\
                (test_type == "tran")+i,"V({})".format(v)) \
                for i,v in enumerate(sorted_nodes)])
    spice_raw_file_txt += "Binary:\n"
    with open(raw_fname, "wb") as spice_raw_file:
        spice_raw_file.write(bytes(spice_raw_file_txt, "UTF-8"))
    with open(raw_fname, "ab") as spice_raw_file:
        [spice_raw_file.write(array('d', s).tobytes()) for s in soln]
