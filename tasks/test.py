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
# import glob
import os
import subprocess
import sys

from invoke import task

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

def run_example(path):
    print('Run {}'.format(path))
    subprocess.check_call((sys.executable, path))

####################################################################################################

def on_linux(path):
    run_example(path)

####################################################################################################

def on_osx(path):

    if path.name in (
            'external-source.py',
    ):
        print('Skip {}'.format(path))
        return

    with open(path) as fh:
        content = fh.read()
    content = content.replace('plt.show()', '#plt.show()')
    with open(path, 'w') as fh:
        fh.write(content)

####################################################################################################

def on_windows(path):

    if path.name in (
            'internal-device-parameters.py',
    ):
        print('Skip {}'.format(path))
        return

    run_example(path)

####################################################################################################

@task()
def run_examples(ctx):

    # for topic in os.listdir(examples_path):
    #     python_files = glob.glob(str(examples_path.joinpath(topic, '*.py')))

    for root, _, filenames in os.walk(EXAMPLES_PATH):
        root = Path(root)
        for filename in filenames:
            filename = Path(filename)
            path = is_example(root, filename)
            if path is not None:
                if sys.platform.startswith('linux'):
                    on_linux(path)
                if sys.platform.startswith('darwin'):
                    on_osx(path)
                if sys.platform.startswith('win'):
                    on_windows(path)
