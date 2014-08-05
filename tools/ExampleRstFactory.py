####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

import logging
import os
import subprocess
import sys
import tempfile

####################################################################################################

PYSPICE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURE_DIRECTORY = None

####################################################################################################

def save_figure(figure, 
                figure_filename,
            ):

    figure_format = os.path.splitext(figure_filename)[1][1:]
    figure_path = os.path.join(FIGURE_DIRECTORY, figure_filename)
    figure.savefig(figure_path,
                   format=figure_format,
                   dpi=150,
                   orientation='landscape', papertype='a4',
                   transparent=True, frameon=False,
    )

####################################################################################################

class Chunk(object):

    ##############################################

    def __init__(self):

        self._lines = []

    ##############################################

    def __nonzero__(self):

        return bool(self._lines)

    ##############################################

    def append(self, line):

        self._lines.append(line)
 
####################################################################################################

class RstChunk(Chunk):

    ##############################################

    def __str__(self):

        return ''.join([line[4:] for line in self._lines])

####################################################################################################

class CodeChunk(Chunk):

    ##############################################

    def append_head(self, line):

        self._lines.insert(1, line)

    ##############################################

    def has_content(self):

        for line in self._lines:
            if line.strip():
                return True
        return False

    ##############################################

    def __str__(self):

        if self.has_content():
            source = ''.join(['    ' + line for line in self._lines])
            return '\n.. code-block:: python\n' + source + '\n'
        else:
            return ''

####################################################################################################

class ImageChunk(Chunk):

    ##############################################

    def __init__(self, line, figure_directory=''):

        # weak ...
        figure_filename = line[line.rindex(", '")+3:line.rindex("')")]
        self._figure_path = os.path.join(figure_directory, figure_filename)

    ##############################################

    def __str__(self):

            return '''
.. image:: {}
'''.format(self._figure_path) 

####################################################################################################

class Chunks(list):
    pass

####################################################################################################

class Example(object):

    ##############################################

    def __init__(self, example_path, rst_directory, make_figure=True):

        self._source_path = os.path.realpath(example_path)
        self._rst_path = self.make_hierarchy(rst_directory)

        with open(example_path) as f:
            self._source = f.readlines()

        if make_figure:
            self.make_figure()
        self.make_rst()

    ##############################################

    def example_hierarchy(self):

        file_path_as_list = os.path.dirname(self._source_path).split(os.path.sep)
        i = file_path_as_list.index('examples')
        return file_path_as_list[i+1:]

    ##############################################

    def make_hierarchy(self, path):

        example_hierarchy = self.example_hierarchy()
        for i in xrange(len(example_hierarchy) +1):
            directory = os.path.join(path, *example_hierarchy[:i])
            if not os.path.exists(directory):
                os.mkdir(directory)
        return directory

    ##############################################

    def make_figure(self):

        tmp_file = tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), prefix='PySpice-', suffix='.py')
        line_index = 0
        if self._source[0].startswith('# -*- coding: utf-8 -*-'):
            tmp_file.write(self._source[0])
            tmp_file.write('\n')
            line_index += 1
        tmp_file.write('import ExampleRstFactory\n')
        tmp_file.write('from ExampleRstFactory import save_figure\n')
        tmp_file.write('ExampleRstFactory.FIGURE_DIRECTORY = "{}"\n'.format(self._rst_path))
        tmp_file.write('\n')
        for line in self._source[line_index:]:
            if line.startswith('#f# '):
                tmp_file.write(line[4:])
            elif not line.startswith('pylab.show'):
                tmp_file.write(line)
            
        tmp_file.flush()
        subprocess.call((sys.executable, tmp_file.name))

    ##############################################

    def _append_rst_chunck(self):

        self._chuncks.append(self._rst_chunck)
        self._rst_chunck = RstChunk()

    ##############################################

    def _append_code_chunck(self):

        self._chuncks.append(self._code_chunck)
        self._code_chunck = CodeChunk()

    ##############################################

    def make_rst(self):

        self._chuncks = Chunks()
        self._rst_chunck = RstChunk()
        self._code_chunck = CodeChunk()

        line_index = 0
        if self._source[0].startswith('# -*- coding: utf-8 -*-'):
            has_coding = True
            line_index += 1
        else:
            has_coding = False

        footer_index = -6

        for line in self._source[line_index:footer_index]:
            if line.startswith('#f# '):
                if self._rst_chunck:
                    self._append_rst_chunck()
                elif self._code_chunck:
                    self._append_code_chunck()
                self._chuncks.append(ImageChunk(line))
            elif line.startswith('#d# '):
                if self._code_chunck:
                    self._append_code_chunck()
                self._rst_chunck.append(line)
            else:
                if line.startswith('pylab.show()'):
                    continue
                if self._rst_chunck:
                    self._append_rst_chunck()
                self._code_chunck.append(line)
        if self._rst_chunck:
            self._append_rst_chunck()
        elif self._code_chunck:
            self._append_code_chunck()

        if has_coding :
            for chunck in self._chuncks:
                if isinstance(chunck, CodeChunk) and chunck.has_content():
                    chunck.append_head(self._source[0] + '\n')
                    break

        rst_filename = os.path.basename(self._source_path).replace('.py', '.rst')
        rst_path = os.path.join(self._rst_path, rst_filename)
        print "Create RST file", rst_path
        with open(rst_path, 'w') as f:
            title = os.path.splitext(rst_filename)[0].replace('-', ' ').title()
            f.write("""
==========
 {}
==========
""".format(title))
            for chunck in self._chuncks:
                f.write(str(chunck))

####################################################################################################

class ExampleRstFactory(object):

    ##############################################

    def __init__(self, examples_path, rst_directory):

        self._rst_directory = os.path.realpath(rst_directory)
        self._examples_path = os.path.realpath(examples_path)

        print "RST API Path:    ", self._rst_directory
        print "Examples Path:", self._examples_path

        if not os.path.exists(self._rst_directory):
            os.mkdir(self._rst_directory)

        self._process_recursively()

    ##############################################

    def _process_recursively(self):

        for current_path, sub_directories, files in os.walk(self._examples_path, followlinks=True):
            for filename in files:
                if filename[0].islower() and filename.endswith('.py'):
                    Example(os.path.join(current_path, filename), self._rst_directory, make_figure=False)

        for current_path, sub_directories, files in os.walk(self._rst_directory, followlinks=True):
            if sub_directories or files:
                index_path = os.path.join(current_path, 'index.rst')
                print 'Create TOC', index_path
                title = os.path.basename(current_path).replace('-', ' ').title()
                with open(index_path, 'w') as f:
                    f.write("""
==========
 {}
==========

.. toctree::
  :maxdepth: 1

""".format(title))
                    for directory in sub_directories:
                        f.write('  {}/index.rst\n'.format(directory))
                    for filename in files:
                        if filename.endswith('.rst') and filename != 'index.rst':
                            f.write('  {}\n'.format(filename))

####################################################################################################
# 
# End
# 
####################################################################################################
