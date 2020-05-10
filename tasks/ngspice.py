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

from invoke import task

####################################################################################################

import PySpice.Spice.NgSpice as NgSpice

####################################################################################################

PYSPICE_SOURCE_PATH = Path(__file__).resolve().parents[1]

BASE_URL = 'https://sourceforge.net/projects/ngspice/files'
RELEASE_URL = BASE_URL + '/ng-spice-rework/'
RELEASE_NOTE_URL = RELEASE_URL + '/{}/ReleaseNotes.txt/download'
MANUAL_URL = RELEASE_URL + '/{0}/ngspice-{0}-manual.pdf/download'
LATEST_URL = BASE_URL + '/latest/download' # zip
TAR_URL = RELEASE_URL + '/{0}/ngspice-{0}.tar.gz'
OSX_URL = RELEASE_URL + '/{0}/ngspice-{0}.pkg'
WINDOWS_URL = RELEASE_URL + '/{0}/ngspice-{0}_64.zip'
WINDOWS_DLL_URL = RELEASE_URL + '/{0}/ngspice-{0}_dll_64.zip'

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

####################################################################################################

@task()
def get_last_version(ctx):
    from bs4 import BeautifulSoup
    import requests
    response = requests.get(RELEASE_URL)
    assert(response.status_code == requests.codes.ok)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('tr', attrs={'class': 'folder'})
    for div in divs:
        if 'title' in div.attrs:
            version = div.attrs['title']
            try:
                version = int(version)
                if not hasattr(ctx, 'ngspice_last_version'):
                    ctx.ngspice_last_version = version
                date = div.find('td', attrs={'headers': 'files_date_h'}).get_text()
                print('version {} on {}'.format(version, date))
            except:
                # raise NameError('Bad version {}'.format(version))
                pass

####################################################################################################

@task(get_last_version)
def get_last_release_note(ctx):
    import requests
    url = RELEASE_NOTE_URL.format(ctx.ngspice_last_version)
    print('Get {} ...'.format(url))
    response = requests.get(url, allow_redirects=True)
    assert(response.status_code == requests.codes.ok)
    print(response.text)

####################################################################################################

def donwload_file(url, dst_path):
    import requests
    print('Get {} ... -> {}'.format(url, dst_path))
    response = requests.get(url, allow_redirects=True)
    assert(response.status_code == requests.codes.ok)
    with open(dst_path, mode='wb') as fh:
        fh.write(response.content)

####################################################################################################

@task(get_last_version)
def get_source(ctx):
    url = LATEST_URL.format(ctx.ngspice_last_version)
    dst_path = 'ngspice-{}.zip'.format(ctx.ngspice_last_version)
    donwload_file(url, dst_path)

####################################################################################################

@task(get_last_version)
def get_manual(ctx):
    url = MANUAL_URL.format(ctx.ngspice_last_version)
    dst_path = 'ngspice-manual-{}.pdf'.format(ctx.ngspice_last_version)
    donwload_file(url, dst_path)

####################################################################################################

@task(get_last_version)
def get_osx(ctx):
    url = OSX_URL.format(ctx.ngspice_last_version)
    dst_path = 'ngspice-{}.pkg'.format(ctx.ngspice_last_version)
    donwload_file(url, dst_path)

####################################################################################################

@task(get_last_version)
def get_windows(ctx):
    url = WINDOWS_URL.format(ctx.ngspice_last_version)
    dst_path = 'ngspice-{}_64.zip'.format(ctx.ngspice_last_version)
    donwload_file(url, dst_path)

####################################################################################################

@task(get_last_version)
def get_windows_dll(ctx):
    # version = ctx.ngspice_last_version
    version = NgSpice.NGSPICE_SUPPORTED_VERSION
    url = WINDOWS_DLL_URL.format(version)
    dst_path = 'ngspice-{}_dll_64.zip'.format(version)
    donwload_file(url, dst_path)
