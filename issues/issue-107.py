####################################################################################################

from PySpice.Spice.Netlist import Circuit, SubCircuitFactory, SubCircuit

####################################################################################################

# class PI(SubCircuitFactory):
class PI(SubCircuit):

    __name__ = 'PI'
    __nodes__ = ('In+', 'In-', 'Out')

    ##############################################

    def __init__(self, name, K, KI, AWG, MINV, MAXV):

        # super().__init__()
        SubCircuit.__init__(self, name, *self.__nodes__)

        self.BehavioralSource(
            'Vprop',
            'prop', self.gnd,
            voltage_expression='{}*(V(In+)-V(In-))'.format(K),
        )
        self.BehavioralSource(
            'Vsum',
            'sum', self.gnd,
            voltage_expression='V(prop)+V(integ)',
        )
        self.BehavioralSource(
            'Vdiffclip',
            'overfl', self.gnd,
            voltage_expression='{}*(V(Out)-V(sum))'.format(AWG),
        )
        self.BehavioralSource(
            'Vsum2',
            'antiwind', self.gnd,
            voltage_expression='V(overfl)+V(prop)',
        )
        self.BehavioralSource(
            'VClip',
            'Out', self.gnd,
            voltage_expression='V(sum)< {0} ? {0} : V(sum) > {1} ? {1} : V(sum)'.format(MINV, MAXV),
        )

        # integrator part - fixme with int model from NGSpice ?
        self.VoltageControlledCurrentSource(
            'I_Int',
            'antiwind', self.gnd, self.gnd,
            'integ', multiplier=KI,
        )
        self.C('i', 'integ', self.gnd, 1)
        self.R('i', 'integ', self.gnd, 1000000)

####################################################################################################

circuit = Circuit('Issue 107')

KG1, KIG1, AWG1, MING1, MAXG1 = range(5)
circuit.subcircuit(PI('PI1', KG1, KIG1, AWG1, MING1, MAXG1))
circuit.X('PI_sensor', 'PI', 'CCDSetPoint', 'L3_CCD', 'HeaterCtrl')

KG2, KIG2, AWG2, MING2, MAXG2 = range(5)
circuit.subcircuit(PI('PI2', KG2, KIG2, AWG2, MING2, MAXG2))
circuit.X('PI2_sensor', 'PI', 'PlateSetPoint', 'CryoPlate', 'PlateCtrl')

print(circuit)
