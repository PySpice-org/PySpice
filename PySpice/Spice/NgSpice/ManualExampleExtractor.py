####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Extractor']

####################################################################################################

import hashlib
import os
from collections.abc import Iterable
from pathlib import Path

from bs4 import BeautifulSoup

####################################################################################################

type PathStr = Path | str

LINESEP = os.linesep

####################################################################################################

class Extractor:

    ##############################################

    def __init__(self, input_: PathStr, output: PathStr) -> None:
        self._input = Path(input_)
        self._output = Path(output)

        html_doc = self._input.read_text()

        parser = 'html.parser'
        # parser = 'lxml'
        soup = BeautifulSoup(html_doc, parser)
        # print(soup.prettify())

        self._digests = {}

        with open(self._output, 'w') as fh:
            self._fh = fh
            self._write_line(f"# Examples extracted from {self._input}")
            # for item in soup.find_all('div', 'lyx_code_item'):
            for tag in soup.find_all(self._selector):
                if tag.name.startswith('h'):
                    self._handle_h(tag)
                else:
                    self._handle_pre(tag)

    ##############################################

    @staticmethod
    def _selector(tag: BeautifulSoup.Tag) -> BeautifulSoup.Tag:
        return tag.name in ('h1', 'h2') or (
            tag.name == 'div' and tag.has_attr('class') and tag.attrs['class'][0] == "lyx_code_item"
        )

    ##############################################

    def _write_line(self, line: str) -> None:
        self._fh.write(line + LINESEP)

    def _write_lines(self, lines: Iterable[str]) -> None:
        self._fh.write(LINESEP.join(lines) + LINESEP)

    ##############################################

    def _handle_h(self, tag: BeautifulSoup.Tag) -> None:
        RULE = '#' * 100
        text = []
        for _ in tag.text.splitlines():
            _ = _.strip()
            if _:
                text.append(f"# {_}")
            else:
                text.append("#")
        self._write_line('')
        self._write_line(RULE)
        self._write_line('#')
        self._write_lines(text)
        self._write_line('#')
        # self._write_line(RULE)

    ##############################################

    def _handle_pre(self, tag: BeautifulSoup.Tag) -> None:
        TRIPLE_QUOTE = '"' * 3
        for pre in tag.find_all('pre', 'listings'):
            text = pre.text
            if text:
                text = LINESEP.join([line.rstrip() for line in text.splitlines()])
                digest = hashlib.sha1(text.encode('utf-8')).hexdigest()
                digest = digest[:4]
                if digest not in self._digests:
                    self._digests[digest] = text
                elif self._digests[digest] == text:
                    print("duplicated {digest}")
                    continue
                else:
                    print(f"too short digest {digest}")
                    digest += '-too-short'
                lines = [
                    '',
                    '#' * 50,
                    f'# @{pre.sourceline}',
                    '',
                    f's{digest} = {TRIPLE_QUOTE}',
                    text,
                    TRIPLE_QUOTE
                ]
                self._write_lines(lines)

####################################################################################################

if __name__ == '__main__':
    import argparse
    argument_parser = argparse.ArgumentParser(
        description='Extract examples from ngspice HTML manual'
    )
    # .../ngspice-manuals-git/build_html/manual.html
    argument_parser.add_argument(
        'input', metavar="MANUAL.HTML",
        help='html manual path'
    )
    argument_parser.add_argument(
        'output', metavar="OUTPUT",
        help='output'
    )
    args = argument_parser.parse_args()

    Extractor(args.input, args.output)
