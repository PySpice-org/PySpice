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
is_linux = _.startswith('linux')
is_osx = _.startswith('darwin')
is_windows = _.startswith('win')
if not (is_linux or is_osx or is_windows):
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

    # tempfile must be closed on Windows
    # c:\python38\python.exe: can't open file
    #  'C:\Users\travis\build\FabriceSalvaire\PySpice\examples\...\tmpgx3uzlad.py':
    #  [Errno 13] Permission denied

    # Comment plt.show()
    #  annoying on Linux but works on Travis
    #  hang on OWX
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.py', delete=False) as tmp_fh:
        tmp_path = Path(tmp_fh.name)
        with open(path) as fh:
            content = fh.read()
        content = content.replace('plt.show()', '#plt.show()')
        tmp_fh.write(content.encode('utf-8'))

    print('Run {}'.format(path))
    # _ = path
    _ = tmp_path
    process = subprocess.run((sys.executable, _), capture_output=True)
    tmp_path.unlink()
    if process.returncode:
        # on Windows
        #   UnicodeEncodeError: 'charmap' codec can't encode character '\u03a9' in position ...:
        #   character maps to <undefined>
        print(process.stdout)  # .decode('utf-8'))
        print(process.stderr)  # .decode('utf-8'))
        return False
    else:
        return True

####################################################################################################

def on_linux(path):

    return run_example(path)

####################################################################################################

def on_osx(path):

    # Run examples/ngspice-shared/external-source.py
    #
    # Error on line 2 :
    #   vinput input 0 dc 0 external
    #   parameter value out of range or the wrong type
    #
    # Traceback (most recent call last):
    #     analysis = simulator.transient(step_time=period/200, end_time=period*2)
    #   File "/usr/local/lib/python3.7/site-packages/PySpice/Spice/Simulation.py", line 1166, in transient
    #     return self._run('transient', *args, **kwargs)
    #   File "/usr/local/lib/python3.7/site-packages/PySpice/Spice/NgSpice/Simulation.py", line 117, in _run
    #     self._ngspice_shared.load_circuit(str(self))
    #   File "/usr/local/lib/python3.7/site-packages/PySpice/Spice/NgSpice/Shared.py", line 1145, in load_circuit
    #     raise NgSpiceCircuitError('')

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
        if is_linux:
            rc = on_linux(path)
        elif is_osx:
            rc = on_osx(path)
        elif is_windows:
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
