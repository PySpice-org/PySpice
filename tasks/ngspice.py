####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2019 Fabrice Salvaire
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

from pathlib import Path
import os
import subprocess

from invoke import task

####################################################################################################

PYSPICE_SOURCE_PATH = Path(__file__).resolve().parents[1]

####################################################################################################

def init(ctx):

    if hasattr(ctx, 'install_path'):
        return

    ctx.ngspice_source_path = PYSPICE_SOURCE_PATH.joinpath(
        *ctx.ngspice.directory[:-1],
        ctx.ngspice.directory[-1].format(ctx.ngspice.version)
    )
    ctx.ngspice_source_build = Path(str(ctx.ngspice_source_path) + '-build')
    ctx.install_path = Path('/usr', 'local', 'stow', 'ngspice-{}'.format(ctx.ngspice.version))
    print('ngspice source path', ctx.ngspice_source_path)
    print('ngspice source build', ctx.ngspice_source_build)
    print('ngspice install path', ctx.install_path)

####################################################################################################

@task
def configure(ctx):
    init(ctx)
    configure_path = ctx.ngspice_source_path.joinpath('configure')
    command = [
        str(configure_path),
        '--prefix={}'.format(ctx.install_path),
    	'--disable-debug',
	'--enable-cider',
	'--enable-openmp',
	'--enable-xspice',
	'--with-readline=yes',
	'--with-ngshared',
    ]
    if not ctx.ngspice_source_build.exists():
        os.mkdir(ctx.ngspice_source_build)
    with ctx.cd(str(ctx.ngspice_source_build)):
        ctx.run(' '.join(command))

####################################################################################################

@task
def build(ctx):
    init(ctx)
    with ctx.cd(str(ctx.ngspice_source_build)):
        ctx.run('make -j4')

####################################################################################################

@task
def clean(ctx):
    init(ctx)
    with ctx.cd(str(ctx.ngspice_source_build)):
        ctx.run('make clean')

####################################################################################################

@task(configure, clean, build)
def install(ctx):
    init(ctx)
    with ctx.cd(str(ctx.ngspice_source_build)):
        ctx.run('make install')
