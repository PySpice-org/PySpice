####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2019 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

from pathlib import Path
import os
import shutil
import sys

from invoke import task

####################################################################################################

from PySpice.Spice import NgSpice

####################################################################################################

PYSPICE_SOURCE_PATH = Path(__file__).resolve().parents[1]

BASE_URL = 'https://sourceforge.net/projects/ngspice/files'
RELEASE_URL = BASE_URL + '/ng-spice-rework'
RELEASE_NOTE_URL = RELEASE_URL + '/{}/ReleaseNotes.txt/download'
MANUAL_URL = RELEASE_URL + '/{0}/ngspice-{0}-manual.pdf/download'
CURRENT_MANUAL_URL = 'https://ngspice.sourceforge.io/docs/ngspice-manual.pdf'
# LATEST_URL = BASE_URL + '/latest/download' # zip
TAR_URL = RELEASE_URL + '/{0}/ngspice-{0}.tar.gz'
# OSX_URL = RELEASE_URL + '/{0}/ngspice-{0}.pkg'
WINDOWS_URL = RELEASE_URL + '/{0}/ngspice-{0}_64.zip'
WINDOWS_DLL_URL = RELEASE_URL + '/{0}/ngspice-{0}_dll_64.zip'

####################################################################################################

@task()
def get_last_version(ctx):
    from bs4 import BeautifulSoup
    import requests
    response = requests.get(RELEASE_URL, timeout=10)
    assert response.status_code == requests.codes.ok
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
                print(f'version {version} on {date}')
            except:
                # raise NameError('Bad version {}'.format(version))
                pass

####################################################################################################

@task(get_last_version)
def get_last_release_note(ctx):
    import requests
    url = RELEASE_NOTE_URL.format(ctx.ngspice_last_version)
    print(f'Get {url} ...')
    response = requests.get(url, allow_redirects=True, timeout=10)
    assert response.status_code == requests.codes.ok
    print(response.text)

####################################################################################################

def donwload_file(url, dst_path):
    import requests
    print(f'Get {url} ... -> {dst_path}')
    response = requests.get(url, allow_redirects=True, timeout=10)
    assert response.status_code == requests.codes.ok
    with open(dst_path, mode='wb') as fh:
        fh.write(response.content)

####################################################################################################

def init(ctx):
    if hasattr(ctx, 'ctx.ngspice_base_path'):
        return

    ctx.ngspice_base_path = PYSPICE_SOURCE_PATH.joinpath(f'ngspice-{ctx.ngspice_last_version}')

    ctx.ngspice_source_path = Path(str(ctx.ngspice_base_path) + '-src')
    print('ngspice source path', ctx.ngspice_source_path)

    ctx.ngspice_build_path = Path(str(ctx.ngspice_base_path) + '-build')
    print('ngspice source build', ctx.ngspice_build_path)

    # ctx.install_path = Path('/usr', 'local', 'stow', 'ngspice-{}'.format(ctx.ngspice.version))
    ctx.install_path = ctx.ngspice_base_path
    print('ngspice install path', ctx.install_path)

####################################################################################################

def remove_directories(ctx):
    init(ctx)
    for path in (
            ctx.ngspice_source_path,
            ctx.ngspice_build_path,
            ctx.install_path,
    ):
        rc = input(f'remove {path} ? [n]/y ')
        if rc == 'y':
            shutil.rmtree(path, ignore_errors=True)

####################################################################################################

@task(get_last_version)
def get_source(ctx, extract=True):
    init(ctx)
    if ctx.ngspice_source_path.exists():
        return
    # remove_directories(ctx)
    url = TAR_URL.format(ctx.ngspice_last_version)
    dst_path = f'ngspice-{ctx.ngspice_last_version}.tar.gz'
    donwload_file(url, dst_path)
    if extract:
        import tarfile
        with tarfile.open(dst_path) as tar_file:
            tar_file.extractall()
        ctx.ngspice_base_path.rename(ctx.ngspice_source_path)

####################################################################################################

@task
def configure(ctx):
    init(ctx)
    configure_path = ctx.ngspice_source_path.joinpath('configure')
    command = [
        str(configure_path),
        f'--prefix={ctx.install_path}',
        '--with-ngshared',
        '--enable-xspice',
        '--enable-cider',
        '--enable-openmp',
        '--disable-debug',
    ]
    if not ctx.ngspice_build_path.exists():
        os.mkdir(ctx.ngspice_build_path)
    with ctx.cd(str(ctx.ngspice_build_path)):
        ctx.run(' '.join(command))

####################################################################################################

@task
def build(ctx):
    init(ctx)
    with ctx.cd(str(ctx.ngspice_build_path)):
        ctx.run('make -j4')

####################################################################################################

@task
def clean(ctx):
    init(ctx)
    with ctx.cd(str(ctx.ngspice_build_path)):
        ctx.run('make clean')

####################################################################################################

@task(get_source, configure, clean, build)
def install(ctx):
    """Compile and install Ngspice library in the PySpice source, e.g. pyspice-source/ngspice-34

    Run a test using:

        LD_LIBRARY_PATH=$PWD/ngspice-34/lib:$LD_LIBRARY_PATH ./bin/pyspice-post-installation --check-install
    """
    if sys.platform != 'linux':
        return
    init(ctx)
    with ctx.cd(str(ctx.ngspice_build_path)):
        ctx.run('make install')

####################################################################################################

@task(get_last_version)
def get_manual(ctx):
    url = MANUAL_URL.format(ctx.ngspice_last_version)
    dst_path = f'ngspice-manual-{ctx.ngspice_last_version}.pdf'
    donwload_file(url, dst_path)

@task()
def open_manual(ctx):
    ctx.run(f'xdg-open {CURRENT_MANUAL_URL}')

####################################################################################################

# @task(get_last_version)
# def get_osx(ctx):
#     url = OSX_URL.format(ctx.ngspice_last_version)
#     dst_path = 'ngspice-{}.pkg'.format(ctx.ngspice_last_version)
#     donwload_file(url, dst_path)

####################################################################################################

@task(get_last_version)
def get_windows(ctx):
    url = WINDOWS_URL.format(ctx.ngspice_last_version)
    dst_path = f'ngspice-{ctx.ngspice_last_version}_64.zip'
    donwload_file(url, dst_path)

####################################################################################################

@task(get_last_version)
def get_windows_dll(ctx):
    # version = ctx.ngspice_last_version
    version = NgSpice.NGSPICE_SUPPORTED_VERSION
    url = WINDOWS_DLL_URL.format(version)
    dst_path = f'ngspice-{version}_dll_64.zip'
    donwload_file(url, dst_path)

####################################################################################################

@task()
def extract_examples(ctx, input, output):
    from PySpice.Spice.NgSpice.ManualExampleExtractor import Extractor
    Extractor(input, output)
