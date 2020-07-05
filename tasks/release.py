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
import re
import shutil

from invoke import task

####################################################################################################

STANDARD_PACKAGES = (
    'argparse',
    'atexit',
    'datetime',
    'glob',
    'hashlib',
    'importlib',
    'json',
    'logging',
    'operator',
    'os',
    'pathlib',
    'shutil',
    'signal',
    'stat',
    'subprocess',
    'sys',
    'time',
    'traceback',
)

@task()
def show_import(ctx):
    package = ctx.Package
    with ctx.cd(package):
        result = ctx.run("grep -r -h -E  '^(import|from) [a-zA-Z]' . | sort | uniq", hide='out')
    imports = set()
    for line in result.stdout.split('\n'):
        if line.startswith('from'):
            position = line.find('import')
            line = line[5:position]
        elif line.startswith('import'):
            line = line[7:]
        # print('|{}|'.format(line))
        position = line.find('.')
        if position != -1:
            line = line[:position]
        line = line.strip()
        if line:
            imports.add(line)
    imports -= set(STANDARD_PACKAGES)
    imports -= set((package,))
    for item in sorted(imports):
        print(item)

@task
def find_package(ctx, name):
    ctx.run('pip freeze | grep -i {}'.format(name))

####################################################################################################

@task()
def update_git_sha(ctx):
    # Fixme: wrong workflow, must tag the last commit
    result = ctx.run('git describe --tags --abbrev=0 --always', hide='out')
    tag = result.stdout.strip()
    if tag.startswith('v'):
        version = tag[1:]
    else:
        version = tag
    if not re.match('\d+(\.\d+(\.\d+)?)?', version):
        raise ValueError('Invalid version {}'.format(version))
    result = ctx.run('git rev-parse HEAD', hide='out')
    sha = result.stdout.strip()
    print(sha)
    print(tag)
    print(version)
    filename = Path(ctx.Package, '__init__.py')
    with open(str(filename), 'r') as fh:
        lines = fh.readlines()
    with open(filename, 'w') as fh:
        for line in lines:
            if line.startswith('__version__'):
                line = "__version__ = '{}'\n".format(version)
            if line.startswith('__git_tag__'):
                line = "__git_tag__ = '{}'\n".format(tag)
            if line.startswith('__git_sha__'):
                line = "__git_sha__ = '{}'\n".format(sha)
            fh.write(line)

####################################################################################################

@task()
def clean(ctx):
    for directory in ('build', 'dist', 'PySpice.egg-info'):
        shutil.rmtree(directory, ignore_errors=True)

@task()
def show_python_site(ctx):
    ctx.run('python3 -m site')

@task(update_git_sha)
def build(ctx):
    ctx.run('python3 setup.py build')

@task(build)
def install(ctx):
    ctx.run('python3 setup.py install')

# @task(clean, build)
# def sdist(ctx):
#     ctx.run('python3 setup.py sdist')

# @task(clean, build)
# def bdist(ctx):
#     ctx.run('python3 setup.py bdist')

@task(clean, build)
def wheel(ctx):
    ctx.run('python3 setup.py sdist')
    ctx.run('python3 setup.py bdist_wheel')

@task(wheel)
def upload(ctx):
    # Twine documentation: https://pypi.org/project/twine/
    # ctx.run('twine register dist/*whl')
    # Sign using
    #   BA24CE0F65CB8C67 Fabrice SALVAIRE <gpg AT fabrice-salvaire.fr>
    #   registered on key servers: hkps://hkps.pool.sks-keyservers.net hkp://pgp.mit.edu
    ctx.run('gpg --detach-sign --armor dist/*tar.gz')
    ctx.run('gpg --detach-sign --armor dist/*whl')
    ctx.run('twine upload dist/*')

def _get_pipy_json():
    import requests
    response = requests.get('https://pypi.org/pypi/PySpice/json')
    assert(response.status_code == requests.codes.ok)
    return response.json()

@task()
def get_pypi_json(ctx):
    import json
    print(json.dumps(_get_pipy_json(), sort_keys=True, indent=4))

@task()
def get_wheel(ctx):
    # https://dzone.com/articles/package-signing-in-pip-it-works-in-a-roundabout-so
    data = _get_pipy_json()
    version = data['info']['version']
    filename = data['urls'][0]['filename']
    wheel_url = data['urls'][0]['url']
    print('Get version {}'.format(version))
    ctx.run('curl --output {} {}'.format(filename, wheel_url))
    asc_suffix = '.asc'
    filename_asc = filename + asc_suffix
    ctx.run('curl --output {} {}'.format(filename_asc, wheel_url + asc_suffix))
    # ctx.run('gpg --keyserver pgp.mit.edu --search-keys {}'.format(key_id))
    ctx.run('gpg --verify {} {}'.format(filename_asc, filename))

####################################################################################################

@task()
def get_github_tar_sha(ctx):
    # Fixme: check git sha
    result = ctx.run('git describe --tags --abbrev=0 --always', hide='out')
    tag = result.stdout.strip()
    url = 'https://github.com/FabriceSalvaire/PySpice/archive/{}.tar.gz'.format(tag)
    print('Get', url)
    import hashlib
    import requests
    response = requests.get(url, allow_redirects=True)
    assert(response.status_code == requests.codes.ok)
    sha = hashlib.sha256(response.content)
    print(sha.hexdigest())

