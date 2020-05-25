####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2020 Fabrice Salvaire
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

# This file is only used if you use `make publish` or explicitly specify it as your config file.

####################################################################################################

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

####################################################################################################

# Delete the output directory, and all of its contents, before generating new files.
DELETE_OUTPUT_DIRECTORY = True

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = 'https://pyspice.fabrice-salvaire.fr'
RELATIVE_URLS = False

# Atom
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
