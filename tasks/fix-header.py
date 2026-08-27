#! /usr/bin/env python3
# -*- python -*-

####################################################################################################

import argparse
import os
from enum import IntEnum, auto
from pathlib import Path

####################################################################################################

argument_parser = argparse.ArgumentParser(description='Fix header')

argument_parser.add_argument(
    'source_path',
    help='root path'
)

args = argument_parser.parse_args()

####################################################################################################

class State(IntEnum):
    BEFORE_LICENSE = auto()
    IN_LICENSE = auto()
    AFTER_LICENSE = auto()

####################################################################################################

NEW_LICENSE = """
# SPDX-License-Identifier: AGPL-3.0-or-later
""".strip()

####################################################################################################

def process_file(file_path: Path) -> None:
    print(f"> {file_path}")
    state = State.BEFORE_LICENSE
    lines = []
    old_content = file_path.read_text()
    if not old_content:
        return
    for line in old_content.splitlines():
        match state:
            case State.BEFORE_LICENSE:
                if line.startswith('# Copyright'):
                    # print("IN_LICENSE")
                    lines.append(line)
                    state = State.IN_LICENSE
                    lines.append(NEW_LICENSE)
                else:
                    lines.append(line)
            case State.IN_LICENSE:
                if line.strip().endswith('://www.gnu.org/licenses/>.'):
                    # print("AFTER_LICENSE")
                    state = State.AFTER_LICENSE
            case State.AFTER_LICENSE:
                lines.append(line)
    content = '\n'.join(lines) + '\n'
    # print(content)
    file_path.rename(str(file_path) + '~')
    file_path.write_text(content)

####################################################################################################

def is_py_file(file_name: Path) -> bool:
    # return True
    return file_name.suffix in ('.py',)

####################################################################################################

def walk(source_path: Path) -> None:
    for path, _, files in os.walk(source_path):
        path = Path(path)
        for file_name in files:
            file_name = Path(file_name)
            if is_py_file(file_name):
                file_path = path.joinpath(file_name)
                process_file(file_path)

####################################################################################################

if args.source_path:
    source_path = Path(args.source_path).absolute()
    if source_path.exists():
        print(source_path)
        if source_path.is_dir():
            walk(source_path)
        elif is_py_file(source_path):
            process_file(source_path)
