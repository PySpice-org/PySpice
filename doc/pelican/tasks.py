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

import os
import shutil
import sys

from invoke import task
from invoke.util import cd
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file

####################################################################################################

SETTINGS_FILE_BASE = 'pelicanconf.py'
SETTINGS = {}
SETTINGS.update(DEFAULT_CONFIG)
LOCAL_SETTINGS = get_settings_from_file(SETTINGS_FILE_BASE)
SETTINGS.update(LOCAL_SETTINGS)

CONFIG = {
    'settings_base': SETTINGS_FILE_BASE,
    'settings_publish': 'publishconf.py',
    # Output path. Can be absolute or relative to tasks.py. Default: 'output'
    'deploy_path': SETTINGS['OUTPUT_PATH'],
    # Port for `serve`
    'port': 8000,
}

from SECRET_CONFIG import SSH_CONFIG
CONFIG.update(SSH_CONFIG)

####################################################################################################

@task
def clean(ctx):
    """Remove generated files"""
    if os.path.isdir(CONFIG['deploy_path']):
        shutil.rmtree(CONFIG['deploy_path'])
        os.makedirs(CONFIG['deploy_path'])

####################################################################################################

@task
def build(ctx, debug=False):
    """Build local version of site"""
    debug = '-D' if debug else ''
    ctx.run('pelican {debug} -s {settings_base}'.format(**CONFIG, debug=debug))

####################################################################################################

@task
def rebuild(ctx):
    """`build` with the delete switch"""
    ctx.run('pelican -d -s {settings_base}'.format(**CONFIG))

####################################################################################################

@task
def regenerate(ctx):
    """Automatically regenerate site upon file modification"""
    ctx.run('pelican -r -s {settings_base}'.format(**CONFIG))

####################################################################################################

@task
def serve(ctx):
    """Serve site at http://localhost:$PORT/ (default port is 8000)"""

    class AddressReuseTCPServer(RootedHTTPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        CONFIG['deploy_path'],
        ('', CONFIG['port']),
        ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {port} ...\n'.format(**CONFIG))
    server.serve_forever()

####################################################################################################

@task(build)
def reserve(ctx):
    """`build`, then `serve`"""
    serve(ctx)

####################################################################################################

@task
def preview(ctx):
    """Build production version of site"""
    ctx.run('pelican -s {settings_publish}'.format(**CONFIG))

####################################################################################################

@task(build)
def livereload(ctx):
    """Automatically reload browser tab upon file modification."""
    from livereload import Server
    server = Server()
    # Watch the base settings file
    server.watch(CONFIG['settings_base'], lambda: build(ctx))
    # Watch content source files
    content_file_extensions = ['.md', '.rst']
    for extension in content_file_extensions:
        content_blob = '{0}/**/*{1}'.format(SETTINGS['PATH'], extension)
        server.watch(content_blob, lambda: build(ctx))
    # Watch the theme's templates and static assets
    theme_path = SETTINGS['THEME']
    server.watch('{}/templates/*.html'.format(theme_path), lambda: build(ctx))
    static_file_extensions = ['.css', '.js']
    for extension in static_file_extensions:
        static_file = '{0}/static/**/*{1}'.format(theme_path, extension)
        server.watch(static_file, lambda: build(ctx))
    # Serve output path on configured port
    server.serve(port=CONFIG['port'], root=CONFIG['deploy_path'])

####################################################################################################

@task(preview)
def publish(ctx):
    """Publish to production via rsync"""
    command_template = (
        'rsync'
        ' --delete -pthrvz -c'
        ' --exclude ".DS_Store"'
        ' --filter "protect releases/"'
        ' -e "ssh -p {ssh_port}" {src_path} {ssh_user}@{ssh_host}:{ssh_path}'
    )
    ctx.run(command_template.format(
        src_path=CONFIG['deploy_path'].rstrip('/') + '/',
        **CONFIG))
