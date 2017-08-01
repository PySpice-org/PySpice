####################################################################################################

from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit import *

####################################################################################################

class RingModulator(SubCircuitFactory):

    __name__ = 'RingModulator'
    __nodes__ = ('input_plus', 'input_minus',
                 'carrier_plus', 'carrier_minus',
                 'output_plus', 'output_minus')

    ##############################################

    def __init__(self,
                 outer_inductance,
                 inner_inductance,
                 coupling,
                 diode_model,
                ):

        super().__init__()

        input_inductor = self.L('input', 'input_plus', 'input_minus', outer_inductance)
        top_inductor = self.L('input_top', 'input_top', 'carrier_plus', inner_inductance)
        bottom_inductor = self.L('input_bottom', 'carrier_plus', 'input_bottom', inner_inductance)
        self.CoupledInductor('input_top', input_inductor.name, top_inductor.name, coupling)
        self.CoupledInductor('input_bottom', input_inductor.name, bottom_inductor.name, coupling)

        self.X('D1', diode_model, 'input_top', 'output_top')
        self.X('D2', diode_model, 'output_top', 'input_bottom')
        self.X('D3', diode_model, 'input_bottom', 'output_bottom')
        self.X('D4', diode_model, 'output_bottom', 'input_top')

        top_inductor = self.L('output_top', 'output_top', 'carrier_minus', inner_inductance)
        bottom_inductor = self.L('output_bottom', 'carrier_minus', 'output_bottom', inner_inductance)
        output_inductor = self.L('output', 'output_plus', 'output_minus', outer_inductance)
        self.CoupledInductor('output_top', output_inductor.name, top_inductor.name, coupling)
        self.CoupledInductor('output_bottom', output_inductor.name, bottom_inductor.name, coupling)
