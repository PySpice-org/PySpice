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

from pathlib import Path
import os
import subprocess
import sys
import tempfile

from invoke import task

####################################################################################################

_ = sys.platform
on_linux = _.startswith('linux')
on_osx = _.startswith('darwin')
on_windows = _.startswith('win')
if not (on_linux or on_osx or on_windows):
    raise NotImplementedError

####################################################################################################

PYSPICE_SOURCE_PATH = Path(__file__).resolve().parents[1]
EXAMPLES_PATH = PYSPICE_SOURCE_PATH.joinpath('examples')

####################################################################################################

def is_example(root, filename):
    if filename.suffix == '.py' and str(filename).islower():
        path = root.joinpath(filename)
        with open(path) as fh:
            for line in fh.readlines()[:2]:
                line = line.strip()
                if line == '#skip#':
                    return None
        return path
    return None

####################################################################################################

def example_iter():

    for root, _, filenames in os.walk(EXAMPLES_PATH):
        root = Path(root)
        for filename in filenames:
            filename = Path(filename)
            path = is_example(root, filename)
            if path is not None:
                yield path

####################################################################################################

def run_example(path):

    with tempfile.NamedTemporaryFile(dir=path.parent) as tmp_fh:

        tmp_path = tmp_fh.name

        with open(path) as fh:
            content = fh.read()
        content = content.replace('plt.show()', '#plt.show()')
        tmp_fh.write(content.encode('utf-8'))
        tmp_fh.seek(0)
        # print(tmp_fh.read())

        print('Run {}'.format(path))
        # print('Run {}'.format(tmp_path))
        # subprocess.call(('cat', tmp_path))
        # subprocess.check_call((sys.executable, tmp_path))
        process = subprocess.run((sys.executable, tmp_path), capture_output=True)
        if process.returncode:
            print(process.stdout.decode('utf-8'))
            print(process.stderr.decode('utf-8'))
            return False
        else:
            return True

####################################################################################################

def on_linux(path):
    return run_example(path)

####################################################################################################

def on_osx(path):

    if path.name in (
            'external-source.py',
    ):
        print('Skip {}'.format(path))
        return 'skipped'

    return run_example(path)

####################################################################################################

def on_windows(path):

    if path.name in (
            'internal-device-parameters.py',
    ):
        print('Skip {}'.format(path))
        return 'skipped'

    return run_example(path)

####################################################################################################

@task()
def run_examples(ctx):

    # os.environ['PySpiceLibraryPath'] = str(EXAMPLES_PATH.joinpath('libraries'))

    # for topic in os.listdir(examples_path):
    #     python_files = glob.glob(str(examples_path.joinpath(topic, '*.py')))

    succeed = []
    failed = []
    skipped = []

    examples = sorted(example_iter(), key=lambda _: str(_))
    for path in examples:
        if on_linux:
            rc = on_linux(path)
        elif on_osx:
            rc = on_osx(path)
        elif on_windows:
            rc = on_windows(path)

        if rc == 'skipped':
            skipped.append(path)
        elif rc:
            succeed.append(path)
        else:
            failed.append(path)

    print()
    for path in skipped:
        print('SKIPPED', path)
    print()
    for path in succeed:
        print('SUCCEED', path)
    print()
    for path in failed:
        print('FAILED', path)
    print()

    if failed:
        raise NameError('Some tests failed')
