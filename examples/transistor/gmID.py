# Adapted and modified from https://github.com/tclarke/sky130radio/tree/4eca853b7e4fd6bc0d69998f65c04f97e73bee84/utils
# Thanks to T Clarke https://github.com/tclarke

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import matplotlib.pyplot as plt
import numpy as np
import os.path
import csv
import h5py
import sys
import pandas as pd
import argparse
# Set Logging
logger = Logging.setup_logging()
# Set Defaults If you want to adapt for different technologies
_SKY130_defaults = {
    'w': 1,
    'l': 0.15,
    'nf': 1
}
_plot_defaults = {
    'id_W_vs_gm_id': ['gm_id', 'id_W'],
    'ft_vs_gm_id': ['gm_id', 'ft'],
    'gm_gds_vs_gm_id': ['gm_id', 'gm_gds'],
    'gm_id_vs_vgg': ['v-sweep', 'gm_id'],
}


def create_test_circuit(libpath, fet_typ='sky130_fd_pr__nfet_01v8', w=1, l=0.15, nf=1, corner='tt'):
    """
    Create the test gmID circuit and instantiate the liberty file in a particular corner
    Fet W and L are instantiated
    """
    ckt =Circuit('gm_id')
    ckt.lib(libpath, section=corner)

    # create the circuit
    ckt.V('gg', 1, ckt.gnd, 0@u_V)
    ckt.V('dd', 2, ckt.gnd, 1.8@u_V)
    ckt.X('M1', fet_typ, 2, 1, ckt.gnd, ckt.gnd, L=l, W=w, nf=1)
    return ckt


def run_sim(c, iparam, w, l):
    """
     Simulation Method which runs DC sim to get the values needed for gm-ID analysis
        Parameters id, gm, gds and cgg
    :param c: Circuit Object
    :param iparam: Mosfet identifier string
    :param w:
    :return: Values of gm_id, ft, id_W, gm_gds, vgs, gm, id, cgg, gds
    """
    sim = c.simulator()
    sim.save_internal_parameters(iparam%'gm', iparam%'id', iparam%'gds', iparam%'cgg')
    # run the dc simulation
    an = sim.dc(Vgg=slice(0, 1.8, 0.01))
#     calculate needed values..need as_ndarray() since most of these have None as the unit and that causes an error
    gm = an.internal_parameters[iparam%'gm'].as_ndarray()
    id = an.internal_parameters[iparam%'id'].as_ndarray()
    gm_id = gm / id
    cgg = an.internal_parameters[iparam%'cgg'].as_ndarray()
    ft = gm / cgg
    id_W = id / w
    gds = an.internal_parameters[iparam%'gds'].as_ndarray()
    gm_gds = gm / gds
    w_arr, l_arr = np.empty(len(gm)), np.empty(len(gm))
    for i in range(len(gm)):
        w_arr[i] = w
        l_arr[i] = l
    gmid_dict = {
        'w': list(w_arr),
        'l': list(l_arr),
        'id_W': list(id_W),
        'gm_id': list(gm_id),
        'ft': list(ft),
        'gm_gds': list(gm_gds),
        'v-sweep': list(an.nodes['v-sweep']),
        'gm': list(gm),
        'id': list(id),
        'cgg': list(cgg),
        'gds': list(gds),
    }
    return gmid_dict
#    #return id_W, gm_id, ft, gm_gds, an.nodes['v-sweep'], gm, id, cgg, gds


def init_plots():
    '''
    Plot the figures with the given
    :return:
    '''
    figs, plts = [], []
    for loopnum, plotname in enumerate(_plot_defaults.keys()):
        figs.append(plt.figure())
        plts.append(figs[loopnum].subplots())
        figs[loopnum].suptitle(plotname)
        plts[loopnum].set_xlabel(_plot_defaults[plotname][0])
        plts[loopnum].set_ylabel(_plot_defaults[plotname][1])
    return plts, figs
#    #figs = [plt.figure(), plt.figure(), plt.figure(), plt.figure()]
#    #plts = [f.subplots() for f in figs]
#    #figs[0].suptitle('Id/W vs gm/Id')
#    #plts[0].set_xlabel("gm/Id")
#    #plts[0].set_ylabel("Id/W")
#    #figs[1].suptitle('fT vs gm/Id')
#    #plts[1].set_xlabel("gm/Id")
#    #plts[1].set_ylabel("f_T")
#    #figs[2].suptitle('gm/gds vs gm/Id')
#    #plts[2].set_xlabel("gm/Id")
#    #plts[2].set_ylabel("gm/gds")
#    #figs[3].suptitle('gm/Id vs Vgg')
#    #plts[3].set_xlabel("Vgg")
#    #plts[3].set_ylabel("gm/Id")
#    #return figs, plts


# def gen_plots(gm_id, id_W, ft, gm_gds, vsweep, fet_W, fet_L, plts):
def gen_plots(df_gmid, plts):
    # plot some interesting things
    for loopnum, plotname in enumerate(_plot_defaults.keys()):
        for (w, l) in np.unique(df_gmid.index.values):
            curr_x = df_gmid.loc[(w, l)][_plot_defaults[plotname][0]]
            curr_y = df_gmid.loc[(w, l)][_plot_defaults[plotname][1]]
            plts[loopnum].plot(curr_x, curr_y, label= f'W_{w} x L_{l}')
#    #plts[0].plot(gm_id, id_W, label=f'W {fet_W} x L {fet_L}')
#    #plts[1].plot(gm_id, ft, label=f'W {fet_W} x L {fet_L}')
#    #plts[2].plot(gm_id, gm_gds, label=f'W {fet_W} x L {fet_L}')
#    #plts[3].plot(vsweep, gm_id, label=f'W {fet_W} x L {fet_L}')


def read_bins(fname):
    r = csv.reader(open(fname, 'r'))
    return r


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--fet_types", required=True, help="Provide the FET Name list",nargs='+', default=[])
    parser.add_argument("--WL_csv", required=True, help="Provide the WL bin")
    parser.add_argument("--plot_dir", required=False, help="Provide the WL bin", default="gmid_plots")
    parser.add_argument("--hdf_db", required=True, help="hdf5 database", default="gmid_plots")
    parser.add_argument("--SingleW", required=False, help="Provide Single W for run on the W", default=None)
    parser.add_argument("--libpath", required=False, help="path to library",
                        default="/usr/bin/miniconda3/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice")
    parser.add_argument("--corner", required=False, help="Corner to run the sims on", default='tt')


    args = parser.parse_args()
#    #if len(sys.argv) < 4:
    #    print(f'{sys.argv[0]} <fet_type> <bins_csv> <out file> [width]')
    #    print('<out file> is a template with 1 \%s which will contain the plot name. 4 are generated per LxW combo.')
    #    print('If [width] is specified, only W/L pairs for that width are processed.')
    #    sys.exit(0)
    fet_types = args.fet_types
    bins_fname = args.WL_csv
    figname = args.plot_dir
    only_W = args.SingleW
    for fet_type in fet_types:
        print(f'Simulating {fet_type} with bins {bins_fname}')
        # Fet Identifier to pass
        iparam = f'@m.xm1.m{fet_type}[%s]'
        c = create_test_circuit(args.libpath, fet_type, 0.15, 1, args.corner)
        bins = read_bins(bins_fname)
        next(bins)
#        #figtitles = ['Id_w', 'fT', 'gm_gds', 'gm_id']
#        #figs, plts = init_plots()
#        #h5name = os.path.splitext(figname % 'data')[0] + '.h5'
        h5name = f'{fet_type}.h5'

        out = h5py.File(h5name, "w")
        bins_d = out.create_dataset('bins', (0, 2), maxshape=(None,2))
        gm_d = out.create_dataset('gm', (0, 0), maxshape=(None,None))
        id_d = out.create_dataset('id', (0, 0), maxshape=(None,None))
        cgg_d = out.create_dataset('cgg', (0, 0), maxshape=(None,None))
        gds_d = out.create_dataset('gds', (0, 0), maxshape=(None,None))
        vsweep_d = out.create_dataset('vsweep', (0,0), maxshape=(None,None))
        idx = 0
        # loop W and L
        run_dict = {}
        for dev, bin, fet_W, fet_L in bins:
            fet_W, fet_L = float(fet_W), float(fet_L)
            if only_W is not None and fet_W != only_W:
                continue
            print(f'{bin}: {dev}  W {fet_W} x L {fet_L}')
            # Update parameters in the loop before runing simulations
            c.element('XM1').parameters['W'] = fet_W
            c.element('XM1').parameters['L'] = fet_L
            # Run Simulations
#            #id_W, gm_id, ft, gm_gds, vsweep, gm, id, cgg, gds = run_sim(c, iparam, fet_W, fet_L)
            curr_dict = run_sim(c, iparam, fet_W, fet_L)
            for k, v in curr_dict.items():
                if k in run_dict.keys():
                    run_dict[k] = run_dict[k]+curr_dict[k]
                else:
                    run_dict[k] = v
            gmid_df = pd.DataFrame.from_dict(run_dict)
#            #if idx == 0:
#            #    gm_d.resize(len(gm_id), 1)
#            #    id_d.resize(len(id_W), 1)
#            #    cgg_d.resize(len(ft), 1)
#            #    gds_d.resize(len(gm_gds), 1)
#            #    vsweep_d.resize(len(vsweep), 1)
#            #bins_d.resize(idx+1, 0)
#            #gm_d.resize(idx+1, 0)
#            #id_d.resize(idx+1, 0)
#            #cgg_d.resize(idx+1, 0)
#            #gds_d.resize(idx+1, 0)
#            #vsweep_d.resize(idx+1, 0)
#            #bins_d[idx,:] = [fet_W, fet_L]
#            #gm_d[idx, :] = gm
#            #id_d[idx, :] = id
#            #cgg_d[idx, :] = cgg
#            #gds_d[idx, :] = gds
#            #vsweep_d[idx, :] = vsweep  # should be the same for every row
#            #idx += 1
        gmid_df.to_csv(f'{fet_type}.csv')
        gmid_df.set_index(['w', 'l'], inplace=True)
        plts, figs = init_plots()
        gen_plots(gmid_df, plts)
        for f, nm in zip(figs, _plot_defaults.keys()):
            f.legend()
            f.tight_layout()
            f.savefig(f'{fet_type}_{nm}')