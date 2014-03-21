####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

import logging
import subprocess

####################################################################################################

from .RawFile import RawFile

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SpiceServer(object):

    _logger = _module_logger.getChild('SpiceServer')

    ##############################################

    def __init__(self, spice_command='ngspice'):

        self._spice_command = spice_command

    ##############################################

    def __call__(self, desk):

        self._logger.info("Start server")

        process = subprocess.Popen((self._spice_command, '-s'),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(str(desk))

        return RawFile(stdout, stderr)

####################################################################################################
# 
# End
# 
####################################################################################################
