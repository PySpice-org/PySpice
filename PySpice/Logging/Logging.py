####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import yaml
import logging
import logging.config
import os

####################################################################################################

import PySpice.Config.ConfigInstall as ConfigInstall

####################################################################################################

def setup_logging(application_name='PySpice',
                  config_file=ConfigInstall.Logging.default_config_file,
                  logging_level=None):

    """Setup the logging.

    Logging configuration is set by a YAML file given by *config_file*.  Alternatively we can set
    the logging level using the environment variable 'PySpiceLogLevel' or using *logging_level*,
    level can be a integer or a string

    """

    logging_config_file_name = ConfigInstall.Logging.find(config_file)
    logging_config = yaml.load(open(logging_config_file_name, 'r'), Loader=yaml.SafeLoader)

    if ConfigInstall.OS.on_linux:
        # Fixme: \033 is not interpreted in YAML
        formatter_config = logging_config['formatters']['ansi']['format']
        logging_config['formatters']['ansi']['format'] = formatter_config.replace('<ESC>', '\033')

    if ConfigInstall.OS.on_windows or ConfigInstall.OS.on_osx:
        formatter = 'simple'
    else:
        formatter = 'ansi'
    logging_config['handlers']['console']['formatter'] = formatter

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(application_name)
    if logging_level:
        logger.setLevel(logging_level)
    if 'PySpiceLogLevel' in os.environ: # used by tools/make-examples
        level = getattr(logging, os.environ['PySpiceLogLevel'].upper(), None)
        logger.setLevel(level) # level can be int or string

    return logger
