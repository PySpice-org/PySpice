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
