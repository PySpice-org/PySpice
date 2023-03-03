#skip#

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.NgSpice.Shared import NgSpiceShared

####################################################################################################

class MyNgSpiceShared(NgSpiceShared):

    ##############################################

    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        voltage[0] = 1.
        return 0

    ##############################################

    def get_isrc_data(self, current, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_isrc_data @{} node {}'.format(ngspice_id, time, node))
        current[0] = 1.
        return 0

####################################################################################################

time_step = '1m'

# circuit = """ .title rc circuit
# * V1 1 0 1
# V1 1 0 dc 0 external
# R1 1 2 1
# C1 2 0 1 ic=0
# .tran {} 3 uic
# .end
# """.format(time_step)

circuit = """
.title Low-Pass RC Filter
Vinput in 0 DC 0V AC SIN(0V 1V 50Hz 0s 0)
Rf in out 1k
Cf out 0 1u
.options TNOM = 25
.options TEMP = 25
.ic
.ac dec 10 1 1Meg
.end
"""

ngspice_shared = MyNgSpiceShared(send_data=False)
ngspice_shared.load_circuit(circuit)
ngspice_shared.run()
print(ngspice_shared.plot_names)
# vectors = ngspice_shared.vectors('tran1')
# print(vectors)
# vectors = ngspice_shared.vectors('ac1')
# print(vectors)
# print(vectors['frequency'])
# print(ngspice_shared.plot('ac1'))
analysis = ngspice_shared.plot('ac1').to_analysis()

print(analysis.nodes)
print(analysis.branches)
