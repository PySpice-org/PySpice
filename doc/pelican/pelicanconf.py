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

from datetime import datetime
from pathlib import Path

####################################################################################################

# source_path = Path(__file__).parent

# global SITEURL
# def site_url(url):
#     print('site_url', SITEURL, url)
#     return SITEURL + url

####################################################################################################
#
# Basic Settings
#

# When you don’t specify a category in your post metadata, set this setting to True, and organize
# your articles in subfolders, the subfolder will become the category of your post. If set to False,
# DEFAULT_CATEGORY will be used as a fallback.
USE_FOLDER_AS_CATEGORY = True

# The default category to fall back on.
DEFAULT_CATEGORY = 'misc'

# Whether to display pages on the menu of the template. Templates may or may not honor this setting.
DISPLAY_PAGES_ON_MENU = False
# Whether to display categories on the menu of the template. Templates may or not honor this setting.
DISPLAY_CATEGORIES_ON_MENU = False

# Extra configuration settings for the docutils publisher (applicable only to reStructuredText). See
# Docutils Configuration settings for more details.
DOCUTILS_SETTINGS = {}

# Delete the output directory, and all of its contents, before generating new files. This can be
# useful in preventing older, unnecessary files from persisting in your output. However, this is a
# destructive setting and should be handled with extreme care.
DELETE_OUTPUT_DIRECTORY = False # dev only

# A list of filenames that should be retained and not deleted from the output directory. One use
# case would be the preservation of version control data.
OUTPUT_RETENTION = ['.git']

# A dictionary of custom Jinja2 filters you want to use. The dictionary should map the filtername to
# the filter function.
JINJA_ENVIRONMENT = {
    'trim_blocks': True,
    'lstrip_blocks': True,
    'extensions': ['jinja2.ext.i18n'],
}

# A list of tuples containing the logging level (up to warning) and the message to be ignored.
LOG_FILTER = []

# A dictionary of file extensions / Reader classes for Pelican to process or ignore.
# For example, to avoid processing .html files, set:
# READERS = {'html': None}
# To add a custom reader for the foo extension, set:
# READERS = {'foo': FooReader}
READERS = {}

# A list of glob patterns. Files and directories matching any of these patterns will be ignored by
# the processor. For example, the default ['.#*'] will ignore emacs lock files, and ['__pycache__']
# would ignore Python 3’s bytecode caches.
IGNORE_FILES = ['.#*']

# Extra configuration settings for the Markdown processor. Refer to the Python Markdown
# documentation’s Options section for a complete list of supported options. The extensions option
# will be automatically computed from the extension_configs option.
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}

# Where to output the generated files.
OUTPUT_PATH = 'output/'

# Path to content directory to be processed by Pelican. If undefined, and content path is not
# specified via an argument to the pelican command, Pelican will use the current working directory.
PATH = 'content'

# A list of directories and files to look at for pages, relative to PATH.
PAGE_PATHS = ['pages']

# A list of directories to exclude when looking for pages in addition to ARTICLE_PATHS.
PAGE_EXCLUDES = []

# A list of directories and files to look at for articles, relative to PATH.
ARTICLE_PATHS = ['']

# A list of directories to exclude when looking for articles in addition to PAGE_PATHS.
ARTICLE_EXCLUDES = []

# Set to True if you want to copy the articles and pages in their original format (e.g. Markdown or reStructuredText) to the specified OUTPUT_PATH.
OUTPUT_SOURCES = False

# Controls the extension that will be used by the SourcesGenerator. Defaults to .text. If not a valid string the default value will be used.
OUTPUT_SOURCES_EXTENSION = '.text'

# The list of plugins to load. See Plugins.
PLUGINS = [
    # 'i18n_subsites',
]
# A list of directories where to look for plugins. See Plugins
PLUGIN_PATHS = [
    'pelican-plugins',
]

# Your site name
SITENAME = 'PySpice'

# Base URL of your web site. Not defined by default, so it is best to specify your SITEURL; if you
# do not, feeds will not be generated with properly-formed URLs. If your site is available via
# HTTPS, this setting should begin with https:// — otherwise use http://. Then append your domain,
# with no trailing slash at the end. Example: SITEURL = 'https://example.com'
SITEURL = '' # dev only

# A list of directories (relative to PATH) in which to look for static files. Such files will be
# copied to the output directory without modification. Articles, pages, and other content source
# files will normally be skipped, so it is safe for a directory to appear both here and in
# PAGE_PATHS or ARTICLE_PATHS. Pelican’s default settings include the “images” directory here.
STATIC_PATHS = [
    'images',
]

# A list of directories to exclude when looking for static files.
STATIC_EXCLUDES = []
# If set to False, content source files will not be skipped when copying files found in
# STATIC_PATHS. This setting is for backward compatibility with Pelican releases before version
# 3.5. It has no effect unless STATIC_PATHS contains a directory that is also in ARTICLE_PATHS or
# PAGE_PATHS. If you are trying to publish your site’s source files, consider using the
# OUTPUT_SOURCES setting instead.
STATIC_EXCLUDE_SOURCES = True

# Create links instead of copying files. If the content and output directories are on the same
# device, then create hard links. Falls back to symbolic links if the output directory is on a
# different filesystem. If symlinks are created, don’t forget to add the -L or --copy-links option
# to rsync when uploading your site.
STATIC_CREATE_LINKS = False

# If set to True, and STATIC_CREATE_LINKS is False, compare mtimes of content and output files,
# and only copy content files that are newer than existing output files.
STATIC_CHECK_IF_MODIFIED = False

# If set to True, several typographical improvements will be incorporated into the generated HTML
# via the Typogrify library, which can be installed via: pip install typogrify
TYPOGRIFY = False

# A list of tags for Typogrify to ignore. By default Typogrify will ignore pre and code tags. This
# requires that Typogrify version 2.0.4 or later is installed
TYPOGRIFY_IGNORE_TAGS = []

# When creating a short summary of an article, this will be the default length (measured in words)
# of the text created. This only applies if your content does not otherwise specify a
# summary. Setting to None will cause the summary to be a copy of the original content.
SUMMARY_MAX_LENGTH = 50

# If disabled, content with dates in the future will get a default status of draft. See Reading only
# modified content for caveats.
WITH_FUTURE_DATES = True

# Regular expression that is used to parse internal links. Default syntax when linking to internal
# files, tags, etc., is to enclose the identifier, say filename, in {} or ||. Identifier between {
# and } goes into the what capturing group. For details see Linking to internal content.
INTRASITE_LINK_REGEX = '[{|](?P<what>.*?)[|}]'

# A list of default Pygments settings for your reStructuredText code blocks. See Syntax highlighting
# for a list of supported options.
PYGMENTS_RST_OPTIONS = []

# Specifies where you want the slug to be automatically generated from. Can be set to title to use
# the ‘Title:’ metadata tag or basename to use the article’s file name when creating the slug.
SLUGIFY_SOURCE = 'title'

# If True, saves content in caches. See Reading only modified content for details about caching.
CACHE_CONTENT = False

# If set to 'reader', save only the raw content and metadata returned by readers. If set to
# 'generator', save processed content objects.
CONTENT_CACHING_LAYER = 'reader'

#  Directory in which to store cache files.
CACHE_PATH = 'cache'

# If True, use gzip to (de)compress the cache files.
GZIP_CACHE = True

# Controls how files are checked for modifications.
CHECK_MODIFIED_METHOD = 'mtime'

# If True, load unmodified content from caches.
LOAD_CONTENT_CACHE = False

# If this list is not empty, only output files with their paths in this list are written. Paths
# should be either absolute or relative to the current Pelican working directory. For possible use
# cases see Writing only selected content.
WRITE_SELECTED = []

# A list of metadata fields containing reST/Markdown content to be parsed and translated to HTML.
FORMATTED_FIELDS = ['summary']

# The TCP port to serve content from the output folder via HTTP when pelican is run with –listen
PORT = 8000

# The IP to which to bind the HTTP server.
BIND = ''

####################################################################################################
#
# URL settings
#

# Defines whether Pelican should use document-relative URLs or not. Only set this to True when
# developing/testing and only if you fully understand the effect it can have on links/feeds.
RELATIVE_URLS = False# dev only

# The URL to refer to an article.
ARTICLE_URL = '{slug}.html'

# The place where we will save an article.
ARTICLE_SAVE_AS = '{slug}.html'

# The URL to refer to an article which doesn’t use the default language.
ARTICLE_LANG_URL = '{slug}-{lang}.html'

# The place where we will save an article which doesn’t use the default language.
ARTICLE_LANG_SAVE_AS = '{slug}-{lang}.html'

# The URL to refer to an article draft.
DRAFT_URL = 'drafts/{slug}.html'

# The place where we will save an article draft.
DRAFT_SAVE_AS = 'drafts/{slug}.html'

# The URL to refer to an article draft which doesn’t use the default language.
DRAFT_LANG_URL = 'drafts/{slug}-{lang}.html'

# The place where we will save an article draft which doesn’t use the default language.
DRAFT_LANG_SAVE_AS = 'drafts/{slug}-{lang}.html'

# The URL we will use to link to a page.
PAGE_URL = 'pages/{slug}.html'

# The location we will save the page. This value has to be the same as PAGE_URL or you need to use a
# rewrite in your server config.
PAGE_SAVE_AS = 'pages/{slug}.html'

# The URL we will use to link to a page which doesn’t use the default language.
PAGE_LANG_URL = 'pages/{slug}-{lang}.html'

# The location we will save the page which doesn’t use the default language.
PAGE_LANG_SAVE_AS = 'pages/{slug}-{lang}.html'

# The URL used to link to a page draft.
DRAFT_PAGE_URL = 'drafts/pages/{slug}.html'

# The actual location a page draft is saved at.
DRAFT_PAGE_SAVE_AS = 'drafts/pages/{slug}.html'

# The URL used to link to a page draft which doesn’t use the default language.
DRAFT_PAGE_LANG_URL = 'drafts/pages/{slug}-{lang}.html'

# The actual location a page draft which doesn’t use the default language is saved at.
DRAFT_PAGE_LANG_SAVE_AS = 'drafts/pages/{slug}-{lang}.html'

# The URL to use for an author.
AUTHOR_URL = 'author/{slug}.html'

# The location to save an author.
AUTHOR_SAVE_AS = 'author/{slug}.html'

# The URL to use for a category.
CATEGORY_URL = 'category/{slug}.html'

# The location to save a category.
CATEGORY_SAVE_AS = 'category/{slug}.html'

# The URL to use for a tag.
TAG_URL = 'tag/{slug}.html'

# The location to save the tag page.
TAG_SAVE_AS = 'tag/{slug}.html'

# The URL to use for per-year archives of your posts. Used only if you have the {url} placeholder in PAGINATION_PATTERNS.
YEAR_ARCHIVE_URL = ''

# The location to save per-year archives of your posts.
YEAR_ARCHIVE_SAVE_AS = ''

# The URL to use for per-month archives of your posts. Used only if you have the {url} placeholder in PAGINATION_PATTERNS.
MONTH_ARCHIVE_URL = ''

# The location to save per-month archives of your posts.
MONTH_ARCHIVE_SAVE_AS = ''

# The URL to use for per-day archives of your posts. Used only if you have the {url} placeholder in PAGINATION_PATTERNS.
DAY_ARCHIVE_URL = ''

# The location to save per-day archives of your posts.
DAY_ARCHIVE_SAVE_AS = ''

# The location to save the article archives page.
ARCHIVES_SAVE_AS = 'archives.html'

# The location to save the author list.
AUTHORS_SAVE_AS = 'authors.html'

# The location to save the category list.
CATEGORIES_SAVE_AS = 'categories.html'

# The location to save the tag list.
TAGS_SAVE_AS = 'tags.html'

# The location to save the list of all articles.
INDEX_SAVE_AS = 'index.html'

# Regex substitutions to make when generating slugs of articles and pages. Specified as a list of
# pairs of (from, to) which are applied in order, ignoring case. The default substitutions have the
# effect of removing non-alphanumeric characters and converting internal whitespace to dashes. Apart
# from these substitutions, slugs are always converted to lowercase ascii characters and leading and
# trailing whitespace is stripped. Useful for backward compatibility with existing URLs.
SLUG_REGEX_SUBSTITUTIONS = [
    (r'[^\w\s-]', ''), # remove non-alphabetical/whitespace/'-' chars
    (r'(?u)\A\s*', ''), # strip leading whitespace
    (r'(?u)\s*\Z', ''), # strip trailing whitespace
    (r'[-\s]+', '-'), # reduce multiple whitespace or '-' to single '-'
]

# Regex substitutions for author slugs. Defaults to SLUG_REGEX_SUBSTITUTIONS.
AUTHOR_REGEX_SUBSTITUTIONS = SLUG_REGEX_SUBSTITUTIONS

# Regex substitutions for category slugs. Defaults to SLUG_REGEX_SUBSTITUTIONS.
CATEGORY_REGEX_SUBSTITUTIONS = SLUG_REGEX_SUBSTITUTIONS

# Regex substitutions for tag slugs. Defaults to SLUG_REGEX_SUBSTITUTIONS.
TAG_REGEX_SUBSTITUTIONS = SLUG_REGEX_SUBSTITUTIONS

####################################################################################################
#
# Time and Date
#

# The timezone used in the date information, to generate Atom and RSS feeds.
# If no timezone is defined, UTC is assumed. This means that the generated Atom and RSS feeds will contain incorrect date information if your locale is not UTC.
# Pelican issues a warning in case this setting is not defined, as it was not mandatory in previous versions.
# Have a look at the wikipedia page to get a list of valid timezone values.
TIMEZONE = 'Europe/Paris'

# The default date you want to use. If 'fs', Pelican will use the file system timestamp information
# (mtime) if it can’t get date information from the metadata. If given any other string, it will be
# parsed by the same method as article metadata. If set to a tuple object, the default datetime
# object will instead be generated by passing the tuple to the datetime.datetime constructor.
DEFAULT_DATE = None

# The default date format you want to use.
DEFAULT_DATE_FORMAT = '%a %d %B %Y'

# If you manage multiple languages, you can set the date formatting here.
DATE_FORMATS = {}

# If no DATE_FORMATS are set, Pelican will fall back to DEFAULT_DATE_FORMAT. If you need to maintain
# multiple languages with different date formats, you can set the DATE_FORMATS dictionary using the
# language name (lang metadata in your post content) as the key.

# In addition to the standard C89 strftime format codes that are listed in Python strftime
# documentation, you can use the - character between % and the format character to remove any
# leading zeros. For example, %d/%m/%Y will output 01/01/2014 whereas %-d/%-m/%Y will result in
# 1/1/2014.

# It is also possible to set different locale settings for each language by using a (locale, format)
# tuple as a dictionary value which will override the LOCALE setting:
# DATE_FORMATS = {
# # 'en': ('en_US','%a, %d %b %Y'),
# # 'jp': ('ja_JP','%Y-%m-%d(%a)'),
# }

# Change the locale [1]. A list of locales can be provided here or a single string representing one
# locale. When providing a list, all the locales will be tried until one works.
# LOCALE =

####################################################################################################
#
# Template pages
#

# A mapping containing template pages that will be rendered with the blog entries. See Template pages.
# If you want to generate custom pages besides your blog entries, you can point any Jinja2 template
# file with a path pointing to the file and the destination path for the generated file.
# TEMPLATE_PAGES = cf. supra

# The extensions to use when looking up template files from template names.
TEMPLATE_EXTENSIONS = ['.html']

# List of templates that are used directly to render content. Typically direct templates are used to
# generate index pages for collections of content (e.g., category and tag index pages).
# DIRECT_TEMPLATES are searched for over paths maintained in THEME_TEMPLATES_OVERRIDES.
DIRECT_TEMPLATES = [
    'index',
    'authors',
    'categories',
    'tags',
    'archives',
]

####################################################################################################
#
# Metadata
#

# Default author (usually your name).
AUTHOR = 'Fabrice SALVAIRE'

# The default metadata you want to use for all articles and pages.
DEFAULT_METADATA = {}

# The regexp that will be used to extract any metadata from the filename. All named groups that are
# matched will be set in the metadata object. The default value will only extract the date from the
# filename.
FILENAME_METADATA = r'(?P<date>d{4}-d{2}-d{2}).*'

# For example, to extract both the date and the slug:
# FILENAME_METADATA = r'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'
# See also SLUGIFY_SOURCE.

# Like FILENAME_METADATA, but parsed from a page’s full path relative to the content source directory.
PATH_METADATA = ''

# Extra metadata dictionaries keyed by relative path. Relative paths require correct OS-specific
# directory separators (i.e. / in UNIX and \ in Windows) unlike some other Pelican file
# settings. Paths to a directory apply to all files under it. The most-specific path wins conflicts.
EXTRA_PATH_METADATA = {}

# Not all metadata needs to be embedded in source file itself. For example, blog posts are often
# named following a YYYY-MM-DD-SLUG.rst pattern, or nested into YYYY/MM/DD-SLUG directories. To
# extract metadata from the filename or path, set FILENAME_METADATA or PATH_METADATA to regular
# expressions that use Python’s group name notation (?P<name>…). If you want to attach additional
# metadata but don’t want to encode it in the path, you can set EXTRA_PATH_METADATA:

# EXTRA_PATH_METADATA = {
# 'relative/path/to/file-1': {
# 'key-1a': 'value-1a',
# 'key-1b': 'value-1b',
# },
# 'relative/path/to/file-2': {
# 'key-2': 'value-2',
# },
# }

# This can be a convenient way to shift the installed location of a particular file:

# Take advantage of the following defaults
# STATIC_SAVE_AS = '{path}'
# STATIC_URL = '{path}'
# STATIC_PATHS = [
# 'static/robots.txt',
# ]
# EXTRA_PATH_METADATA = {
# 'static/robots.txt': {'path': 'robots.txt'},
# }

####################################################################################################
#
# Feed settings
#

# By default, Pelican uses Atom feeds. However, it is also possible to use RSS feeds if you prefer.

# Pelican generates category feeds as well as feeds for all your articles. It does not generate
# feeds for tags by default, but it is possible to do so using the TAG_FEED_ATOM and TAG_FEED_RSS
# settings:

# The domain prepended to feed URLs. Since feed URLs should always be absolute, it is highly
# recommended to define this (e.g., “https://feeds.example.com”). If you have already explicitly
# defined SITEURL (see above) and want to use the same domain for your feeds, you can just set:
# FEED_DOMAIN = SITEURL.
# FEED_DOMAIN = None # i.e. base URL is '/'

# The location to save the Atom feed.
FEED_ATOM = None # i.e. no Atom feed

# Relative URL of the Atom feed. If not set, FEED_ATOM is used both for save location and URL.
# FEED_ATOM_URL = None

# The location to save the RSS feed.
FEED_RSS = None # i.e. no RSS

# Relative URL of the RSS feed. If not set, FEED_RSS is used both for save location and URL.
# FEED_RSS_URL = None

# The location to save the all-posts Atom feed: this feed will contain all posts regardless of their language.
# FEED_ALL_ATOM = 'feeds/all.atom.xml'
# FEED_ALL_ATOM = None # dev only

# Relative URL of the all-posts Atom feed. If not set, FEED_ALL_ATOM is used both for save location and URL.
# FEED_ALL_ATOM_URL = None

# The location to save the the all-posts RSS feed: this feed will contain all posts regardless of their language.
FEED_ALL_RSS = None # i.e. no all-posts RSS

# Relative URL of the all-posts RSS feed. If not set, FEED_ALL_RSS is used both for save location and URL.
# FEED_ALL_RSS_URL = None

# The location to save the category Atom feeds. [2]
# CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
# CATEGORY_FEED_ATOM = None # dev only

# Relative URL of the category Atom feeds, including the {slug} placeholder. [2] If not set,
# CATEGORY_FEED_ATOM is used both for save location and URL.
# CATEGORY_FEED_ATOM_URL = None

# The location to save the category RSS feeds, including the {slug} placeholder. [2]
CATEGORY_FEED_RSS = None # i.e. no RSS

# Relative URL of the category RSS feeds, including the {slug} placeholder. [2] If not set,
# CATEGORY_FEED_RSS is used both for save location and URL.
# CATEGORY_FEED_RSS_URL = None

# The location to save the author Atom feeds. [2]
# AUTHOR_FEED_ATOM = 'feeds/{slug}.atom.xml'
# AUTHOR_FEED_ATOM = None

# Relative URL of the author Atom feeds, including the {slug} placeholder. [2] If not set,
# AUTHOR_FEED_ATOM is used both for save location and URL.
# AUTHOR_FEED_ATOM_URL = None

# The location to save the author RSS feeds. [2]
# AUTHOR_FEED_RSS = 'feeds/{slug}.rss.xml'
# AUTHOR_FEED_RSS = None

# Relative URL of the author RSS feeds, including the {slug} placeholder. [2] If not set,
# AUTHOR_FEED_RSS is used both for save location and URL.
# AUTHOR_FEED_RSS_URL = None

# The location to save the tag Atom feed, including the {slug} placeholder. [2]
TAG_FEED_ATOM = None # i.e. no tag feed

# Relative URL of the tag Atom feed, including the {slug} placeholder. [2]
# TAG_FEED_ATOM_URL = None

# Relative URL to output the tag RSS feed, including the {slug} placeholder. If not set,
# TAG_FEED_RSS is used both for save location and URL.
TAG_FEED_RSS = None # i.e. no RSS tag feed

# Maximum number of items allowed in a feed. Feed item quantity is unrestricted by default.
# FEED_MAX_ITEMS =

# Only include item summaries in the description tag of RSS feeds. If set to False, the full content
# will be included instead. This setting doesn’t affect Atom feeds, only RSS ones.
# RSS_FEED_SUMMARY_ONLY = True

# If you don’t want to generate some or any of these feeds, set the above variables to None.

####################################################################################################
#
# Pagination
#

# The default behaviour of Pelican is to list all the article titles along with a short description
# on the index page. While this works well for small-to-medium sites, sites with a large quantity of
# articles will probably benefit from paginating this list.

# You can use the following settings to configure the pagination.

# The minimum number of articles allowed on the last page. Use this when you don’t want the last page to only contain a handful of articles.
DEFAULT_ORPHANS = 0

# The maximum number of articles to include on a page, not including orphans. False to disable pagination.
# DEFAULT_PAGINATION = False
DEFAULT_PAGINATION = 10

# The templates to use pagination with, and the number of articles to include on a page. If this
# value is None, it defaults to DEFAULT_PAGINATION.
PAGINATED_TEMPLATES = {
    'index': None,
    'tag': None,
    'category': None,
    'author': None,
}

# A set of patterns that are used to determine advanced pagination output.
PAGINATION_PATTERNS = (
    (1, '{name}{extension}', '{name}{extension}'),
    (2, '{name}{number}{extension}', '{name}{number}{extension}'),
)

####################################################################################################
#
# Translations
#

# Pelican offers a way to translate articles. See the Content section for more information.

# The default language to use.
DEFAULT_LANG = 'en'

I18N_TEMPLATES_LANG = 'en'

# The metadata attribute(s) used to identify which articles are translations of one another. May be
# a string or a collection of strings. Set to None or False to disable the identification of
# translations.
ARTICLE_TRANSLATION_ID = 'slug'

# The metadata attribute(s) used to identify which pages are translations of one another. May be a
# string or a collection of strings. Set to None or False to disable the identification of
# translations.
PAGE_TRANSLATION_ID = 'slug'

# The location to save the Atom feed for translations. [3]
# TRANSLATION_FEED_ATOM = 'feeds/all-{lang}.atom.xml'
TRANSLATION_FEED_ATOM = None

# Relative URL of the Atom feed for translations, including the {lang} placeholder. [3] If not set,
# TRANSLATION_FEED_ATOM is used both for save location and URL.
TRANSLATION_FEED_ATOM_URL = None

# Where to put the RSS feed for translations.
TRANSLATION_FEED_RSS = None # i.e. no RSS

# Relative URL of the RSS feed for translations, including the {lang} placeholder. [3] If not set,
# TRANSLATION_FEED_RSS is used both for save location and URL.
TRANSLATION_FEED_RSS_URL = None

####################################################################################################
#
# Ordering content
#

# Order archives by newest first by date. (False: orders by date with older articles first.)
NEWEST_FIRST_ARCHIVES = True

# Reverse the category order. (True: lists by reverse alphabetical order; default lists alphabetically.)
REVERSE_CATEGORY_ORDER = False

# Defines how the articles (articles_page.object_list in the template) are sorted. Valid options
# are: metadata as a string (use reversed- prefix the reverse the sort order), special option
# 'basename' which will use the basename of the file (without path) or a custom function to extract
# the sorting key from articles. The default value, 'reversed-date', will sort articles by date in
# reverse order (i.e. newest article comes first).
ARTICLE_ORDER_BY = 'reversed-date'

# Defines how the pages (pages variable in the template) are sorted. Options are same as
# ARTICLE_ORDER_BY. The default value, 'basename' will sort pages by their basename.
PAGE_ORDER_BY = 'basename'

####################################################################################################
#
# Themes
#

# Creating Pelican themes is addressed in a dedicated section (see Creating themes). However, here
# are the settings that are related to themes.

# Theme to use to produce the output. Can be a relative or absolute path to a theme folder, or the
# name of a default theme or a theme installed via pelican-themes (see below).
# THEME = './pelican-themes/pelican-bootstrap3'
THEME = 'theme'

# Destination directory in the output path where Pelican will place the files collected from THEME_STATIC_PATHS. Default is theme.
THEME_STATIC_DIR = 'theme'

# Static theme paths you want to copy. Default value is static, but if your theme has other static
# paths, you can put them here. If files or directories with the same names are included in the
# paths defined in this settings, they will be progressively overwritten.
THEME_STATIC_PATHS = ['static']

# A list of paths you want Jinja2 to search for templates before searching the theme’s templates/
# directory. Allows for overriding individual theme template files without having to fork an
# existing theme. Jinja2 searches in the following order: files in THEME_TEMPLATES_OVERRIDES first,
# then the theme’s templates/.
THEME_TEMPLATES_OVERRIDES = []

# You can also extend templates from the theme using the {% extends %} directive utilizing the
# !theme prefix as shown in the following example:
# {% extends '!theme/article.html' %}

# Specify the CSS file you want to load.
CSS_FILE = 'main.css'

# A subtitle to appear in the header.
# SITESUBTITLE =

# Pelican can handle Disqus comments. Specify the Disqus sitename identifier here.
# DISQUS_SITENAME =

# Your GitHub URL (if you have one). It will then use this information to create a GitHub ribbon.
GITHUB_URL = 'https://github.com/FabriceSalvaire/PySpice'

# Set to UA-XXXXX-Y Property’s tracking ID to activate Google Analytics.
# GOOGLE_ANALYTICS =

# Set cookie domain field of Google Analytics tracking code. Defaults to auto.
# GA_COOKIE_DOMAIN =

# Set to ‘XXX-YYYYYY-X’ to activate GoSquared.
# GOSQUARED_SITENAME =

# A list of tuples (Title, URL) for additional menu items to appear at the beginning of the main menu.
# MENUITEMS = cf. supra

# URL to your Piwik server - without ‘http://‘ at the beginning.
# PIWIK_URL =

# If the SSL-URL differs from the normal Piwik-URL you have to include this setting too. (optional)
# PIWIK_SSL_URL =

# ID for the monitored website. You can find the ID in the Piwik admin interface > Settings > Websites.
# PIWIK_SITE_ID =

# A list of tuples (Title, URL) for links to appear on the header.
LINKS = (
    # ('Pelican', 'http://getpelican.com/'),
    # ('Python.org', 'http://python.org/'),
    # ('Jinja2', 'http://jinja.pocoo.org/'),
    # ('You can modify those links in your config file', '#'),
)

# A list of tuples (Title, URL) to appear in the “social” section.
# SOCIAL =

# Allows for adding a button to articles to encourage others to tweet about them. Add your Twitter username if you want this button to appear.
# TWITTER_USERNAME =

# Allows override of the name of the links widget. If not specified, defaults to “links”.
# LINKS_WIDGET_NAME =

# Allows override of the name of the “social” widget. If not specified, defaults to “social”.
# SOCIAL_WIDGET_NAME =

# In addition, you can use the “wide” version of the notmyidea theme by adding the following to your configuration:
# CSS_FILE = 'wide.css'

####################################################################################################

class TemplatePage:

    # 'src' is relative to 'theme/templates' !

    ##############################################

    def __init__(self, name, template_name, title=None):
        self.name = name
        self.title = title or name
        self.src = 'src/{}.html'.format(template_name)
        self.dst = 'pages/{}.html'.format(template_name)
        self.dst_url = '/' + self.dst # SITEURL +

    ##############################################

    @property
    def menu_item(self):
        return (self.title, self.dst_url)

####################################################################################################
#
# Customs Variables
#

META_DESCRIPTION = 'Simulate electronic circuit using Python and the Ngspice / Xyce simulators'

LOGO_URL = 'images/logo.svg'

COPYRIGHT_YEAR = datetime.now().year
COPYRIGHT_NAME = 'PySpice'

PYSPICE_FORUM = 'https://pyspice.discourse.group'
PYSPICE_BUGTRACKER = GITHUB_URL + '/issues'

RELEASES_URL = '/releases'
LAST_RELEASE = 'v1.4'
OLD_RELEASES = [
    'v1.3',
    'v1.2',
]

PAGE_LINKS  = {
    name: TemplatePage(name, template, title)
    for name, template, title in (
            ('legal_notice', 'legal-notice', 'Legal Notice'),
    )
}

TEMPLATE_PAGES_IN_MENU = {
    name: TemplatePage(name, template, title)
    for name, template, title in (
            ('help', 'get-help', '<i class="fas fa-users"></i> Help'),
            ('documentation', 'documentation', '<i class="fas fa-book"></i> Documentation'),
    )
}

PAGE_LINKS.update(TEMPLATE_PAGES_IN_MENU)

TEMPLATE_PAGES = {template.src: template.dst for template in TEMPLATE_PAGES_IN_MENU.values()}

MENUITEMS = [
    TEMPLATE_PAGES_IN_MENU['help'].menu_item,
    TEMPLATE_PAGES_IN_MENU['documentation'].menu_item,
    ('<i class="fab fa-github"></i> GitHub', GITHUB_URL),
]
