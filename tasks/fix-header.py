#! /usr/bin/env python3
# -*- python -*-

####################################################################################################

from pathlib import Path
import argparse
import os

####################################################################################################
#
# Options
#

argument_parser = argparse.ArgumentParser(description='Fix header')

argument_parser.add_argument(
    '--source-path',
    default=None,
    help='root path'
)

args = argument_parser.parse_args()

####################################################################################################

NEW_LICENSE = """
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
""".lstrip()

####################################################################################################

def process_file(absolut_file_name):
    print(f"> {absolut_file_name}")
    BEFORE_LICENSE = 0
    IN_LICENSE = 1
    AFTER_LICENSE = 2
    state = BEFORE_LICENSE
    lines = []
    with open(absolut_file_name, 'r') as fh:
        for line in fh.readlines():
            if state == BEFORE_LICENSE:
                if line.startswith('# This program'):
                    #print("IN_LICENSE")
                    state = IN_LICENSE
                    lines.append(NEW_LICENSE)
                    continue
            elif state == IN_LICENSE:
                if line.strip().endswith('://www.gnu.org/licenses/>.'):
                    state = AFTER_LICENSE
                    #print("AFTER_LICENSE")
                continue
            lines.append(line)
    content = ''.join(lines)
    # print(content)
    os.rename(absolut_file_name, str(absolut_file_name) + '~')
    with open(absolut_file_name, 'w') as fh:
            fh.write(content)

####################################################################################################

def is_py_file(file_name):
    # return True
    return file_name.suffix in ('.py',)

####################################################################################################

def walk(source_path):
    for path, directories, files in os.walk(source_path):
        path = Path(path)
        for file_name in files:
            file_name = Path(file_name)
            if is_py_file(file_name):
                absolut_file_name = path.joinpath(file_name)
                process_file(absolut_file_name)

####################################################################################################

if args.source_path:
    source_path = Path(args.source_path).absolute()
    if source_path.exists():
        print(source_path)
        if source_path.is_dir():
            walk(source_path)
        elif is_py_file(source_path):
            process_file(source_path)
