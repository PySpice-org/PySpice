####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
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

from PySpice.Config import ConfigInstall

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
