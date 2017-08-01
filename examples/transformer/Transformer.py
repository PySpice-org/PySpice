####################################################################################################

from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit import *

####################################################################################################

class Transformer(SubCircuitFactory):

    __name__ = 'Transformer'
    __nodes__ = ('input_plus', 'input_minus',
                 'output_plus', 'output_minus')

    ##############################################

    def __init__(self,
                 turn_ratio,
                 primary_inductance=1@u_H,
                 copper_resistance=1@u_Ω,
                 leakage_inductance=1@u_mH,
                 winding_capacitance=20@u_pF,
                 coupling=.999,
             ):

        super().__init__()

        # For an ideal transformer you can reduce the values for the flux leakage inductances, the
        # copper resistors and the winding capacitances. But
        if copper_resistance <= 0:
            raise ValueError("copper resistance must be > 0")
        if leakage_inductance <= 0:
            raise ValueError("leakage inductance must be > 0")

        # primary_turns =
        # secondary_turns =
        # turn_ratio = primary_turns / secondary_turns
        # primary_inductance =
        # primary_inductance / secondary_inductance = turn_ratio**2
        secondary_inductance = primary_inductance / float(turn_ratio**2)

        # Primary
        self.C('primary', 'input_plus', 'input_minus', winding_capacitance)
        self.L('primary_leakage', 'input_plus', 1, leakage_inductance)
        primary_inductor = self.L('primary', 1, 2, primary_inductance)
        self.R('primary', 2, 'output_minus', copper_resistance)

        # Secondary
        self.C('secondary', 'output_plus', 'output_minus', winding_capacitance)
        self.L('secondary_leakage', 'output_plus', 3, leakage_inductance)
        secondary_inductor = self.L('secondary', 3, 4, secondary_inductance)
        self.R('secondary', 4, 'output_minus', copper_resistance)

        # Coupling
        self.CoupledInductor('coupling', primary_inductor.name, secondary_inductor.name, coupling)
