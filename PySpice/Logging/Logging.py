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

"""This module setups the logging for PySpice.

"""

####################################################################################################

import yaml
import logging
import logging.config
import os
import sys

####################################################################################################

import PySpice.Config.ConfigInstall as ConfigInstall

####################################################################################################

def setup_logging(
        application_name='PySpice',
        config_file=ConfigInstall.Logging.default_config_file,
        logging_level=None,
):

    """Setup the logging.

    Logging configuration is set by a YAML file given by *config_file*.

    Alternatively we can set the logging level using the environment variable 'PySpiceLogLevel' or
    using *logging_level*, level can be a integer or a string.  The logging level is set by
    precedence using :

    * `logging_level` parameter if not `None`
    * 'PySpiceLogLevel' environment variable set to: CRITICAL, ERROR, WARNING, INFO, DEBUG
    * else :file:`logging.yml` file settings

    Note: logging level `NOTSET = 0`

    """

    logging_config_file_name = ConfigInstall.Logging.find(config_file)
    logging_config = yaml.load(open(logging_config_file_name, 'r'), Loader=yaml.SafeLoader)

    # YAML fixes

    # Fixme: \033 is not interpreted in YAML
    if ConfigInstall.OS.on_linux:
        formatter_config = logging_config['formatters']['ansi']['format']
        logging_config['formatters']['ansi']['format'] = formatter_config.replace('<ESC>', '\033')

    # Use "simple" formatter for Windows and OSX
    # and "ansi" for Linux
    if ConfigInstall.OS.on_windows or ConfigInstall.OS.on_osx:
        formatter = 'simple'
    else:
        formatter = 'ansi'
    logging_config['handlers']['console']['formatter'] = formatter

    # Load YAML settings
    logging.config.dictConfig(logging_config)

    # Customise logging level
    logger = logging.getLogger(application_name)
    if logging_level is None and 'PySpiceLogLevel' in os.environ:
        level_name = os.environ['PySpiceLogLevel']
        try:
            logging_level = getattr(logging, level_name.upper())
        except AttributeError:
            sys.exit(f'PySpiceLogLevel environment variable is set to an invalid logging level "{level_name}"')
    if logging_level:
        # level can be int or string
        logger.setLevel(logging_level)
    # else use logging.yml

    return logger
