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

on_azure = os.environ.get('CI', None) == 'azure'

####################################################################################################

if is_windows:
    # Windows uses CP1252 encoding for io
    # $env:PYTHONIOENCODING="utf_8"
    import locale
    print(sys.getdefaultencoding())
    print(locale.getpreferredencoding())

####################################################################################################

PYSPICE_SOURCE_PATH = Path(__file__).resolve().parents[1]
EXAMPLES_PATH = PYSPICE_SOURCE_PATH.joinpath('examples')

####################################################################################################

def make_path(*args):
    return str(Path(EXAMPLES_PATH, *args))

####################################################################################################

def is_example(root, filename):
    if filename.suffix == '.py' and str(filename).islower():
        path = root.joinpath(filename)
        if path.is_symlink():
            return None
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
                # Windows: check file is not a Git symlink
                with open(path) as fh:
                    content = fh.readlines()
                if not (len(content) == 1 and content[0].strip().endswith('.py')):
                    yield path

####################################################################################################

def run_example(path):

    # Windows: tempfile must be closed else
    # c:\python38\python.exe: can't open file
    #  'C:\Users\travis\build\FabriceSalvaire\PySpice\examples\...\tmpgx3uzlad.py':
    #  [Errno 13] Permission denied

    # Comment plt.show()
    #  annoying on a Linux terminal but works on Travis
    #  hang on OSX
    #  Windows ???
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.py', delete=False) as tmp_fh:
        tmp_path = Path(tmp_fh.name)
        with open(path, encoding='utf-8') as fh:
            content = fh.read()
        content = content.replace('plt.show()', '#plt.show()')
        tmp_fh.write(content.encode('utf-8'))

    print('Run {}'.format(path))
    # _ = path
    _ = tmp_path
    command = (sys.executable, str(_)) # else TypeError: argument of type 'WindowsPath' is not iterable
    process = subprocess.run(command, capture_output=True, encoding='utf-8')
    tmp_path.unlink()
    if process.returncode:
        print(process.stdout)
        print(process.stderr)
        return False
    else:
        return True

####################################################################################################

def on_linux(path):

    skipped_files = [
        make_path('operational-amplifier', 'astable.py'),   # doAnalyses: Too many iterations without convergence
    ]

    if str(path) in skipped_files:
        print('Skip {}'.format(path))
        return 'skipped'

    return run_example(path)

####################################################################################################

def on_osx(path):

    skipped_files = [
        make_path('ngspice-shared', 'external-source.py'),
    ]

    if on_azure:
        skipped_files += [
            # Error: ngspice.dll cannot recover and awaits to be detached
            make_path('ngspice-shared', 'ngspice-interpreter.py'),
        ]

    if str(path) in skipped_files:
        print('Skip {}'.format(path))
        return 'skipped'

    return run_example(path)

####################################################################################################

def on_windows(path):

    skipped_files = []

    print('on_azure', on_azure, os.environ.get('CI', None))
    # if on_azure:
    # %SRC_DIR%\examples\switched-power-supplies\buck-converter.py
    skipped_files += [
        make_path('basic-usages', 'unit.py'),
        make_path('switched-power-supplies', 'buck-converter.py'),
        make_path('operational-amplifier', 'astable.py'),   # doAnalyses: Too many iterations without convergence
    ]

    if str(path) in skipped_files:
        print('Skip {}'.format(path))
        return 'skipped'

    return run_example(path)

####################################################################################################

@task()
def run_examples(ctx):

    # subprocess capture_output requires 3.7
    if sys.version_info.minor < 7:
        print('WARNING: Skip tests because Python < 3.7')
        return

    # os.environ['PySpiceLibraryPath'] = str(EXAMPLES_PATH.joinpath('libraries'))

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
