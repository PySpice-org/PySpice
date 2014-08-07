####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

""" This module implements a generator of RST files for examples.
"""

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

    """ This function is called from example to save a figure. """

    figure_format = os.path.splitext(figure_filename)[1][1:] # foo.png -> png
    figure_path = os.path.join(FIGURE_DIRECTORY, figure_filename)
    print "Save figure", figure_path
    figure.savefig(figure_path,
                   format=figure_format,
                   dpi=150,
                   orientation='landscape', papertype='a4',
                   transparent=True, frameon=False,
    )

####################################################################################################

def timestamp(path):
    return os.stat(path).st_ctime

####################################################################################################

class Chunk(object):

    """ This class represents a chunk of lines in the source. """

    ##############################################

    def __init__(self):

        self._lines = []

    ##############################################

    def append(self, line):

        self._lines.append(line)
 
####################################################################################################

class RstChunk(Chunk):

    """ This class represents a RST content. """

    ##############################################

    def __nonzero__(self):

        return bool(self._lines)

    ##############################################

    def __str__(self):

        return ''.join(self._lines)

####################################################################################################

class CodeChunk(Chunk):

    """ This class represents a code block. """

    ##############################################

    def append_head(self, line):

        self._lines.insert(1, line)

    ##############################################

    def __nonzero__(self):

        for line in self._lines:
            if line.strip():
                return True
        return False

    ##############################################

    def __str__(self):

        if bool(self):
            source = ''.join(['    ' + line for line in self._lines])
            return '\n.. code-block:: python\n\n' + source + '\n'
        else:
            return ''

####################################################################################################

class ImageChunk(Chunk):

    """ This class represents an image block for a figure. """

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

class CircuitMacrosImageChunk(ImageChunk):

    """ This class represents an image block for a circuit macros figure. """

    ##############################################

    def __init__(self, line, source_directory, rst_directory):

        m4_filename = line[len('#cm# '):].strip()
        png_filename = m4_filename.replace('.m4', '.png')
        self._m4_path = os.path.join(source_directory, m4_filename)
        self._rst_directory = rst_directory
        self._figure_path = png_filename
        self._figure_real_path = os.path.join(rst_directory, png_filename)

        self._generator = os.path.join(PYSPICE_PATH, 'tools', 'circuit-macros-generator')

    ##############################################

    def __nonzero__(self):

        if os.path.exists(self._figure_real_path):
            return timestamp(self._m4_path) > timestamp(self._figure_real_path)
        else:
            return True

    ##############################################

    def make_figure(self):

        print "Make circuit figure", self._m4_path
        dev_null = open(os.devnull, 'w')
        try:
            subprocess.check_call((self._generator, self._m4_path, self._rst_directory),
                                  stdout=dev_null, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print "Failed to make circuit figure example", self._m4_path

####################################################################################################

class Chunks(list):
    pass

####################################################################################################

class Example(object):

    """ This class is responsible to process an example. """

    ##############################################

    def __init__(self, example_path, rst_directory):

        self._source_path = os.path.realpath(example_path)
        self._source_directory = os.path.dirname(self._source_path)

        self._basename = os.path.splitext(os.path.basename(example_path))[0]

        self._rst_directory = self._make_hierarchy(rst_directory)
        self._rst_path = os.path.join(self._rst_directory, self._basename + '.rst')

        with open(example_path) as f:
            self._source = f.readlines()
        self._parse_source()

    ##############################################

    def _example_hierarchy(self):

        """ Return a list of directory corresponding to the file hierarchy after ``.../examples/`` """

        file_path_as_list = os.path.dirname(self._source_path).split(os.path.sep)
        i = file_path_as_list.index('examples') # Fixme: cf. ExampleRstFactory._examples_path
        return file_path_as_list[i+1:]

    ##############################################

    def _make_hierarchy(self, path):

        """ Create the file hierarchy. """

        example_hierarchy = self._example_hierarchy()
        for i in xrange(len(example_hierarchy) +1):
            directory = os.path.join(path, *example_hierarchy[:i])
            if not os.path.exists(directory):
                os.mkdir(directory)
        return directory

    ##############################################

    @property
    def source_timestamp(self):

        return timestamp(self._source_path)

    ##############################################

    @property
    def rst_timestamp(self):

        if os.path.exists(self._rst_path):
            return timestamp(self._rst_path)
        else:
            return -1

    ##############################################

    def __nonzero__(self):

        return self.source_timestamp > self.rst_timestamp

    ##############################################

    def make_figure(self):

        """This function make a temporary copy of the example with calls to *save_figure* and run it.
        """

        tmp_file = tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), prefix='PySpice-', suffix='.py')
        line_index = 0
        if self._source[0].startswith('# -*- coding: utf-8 -*-'):
            tmp_file.write(self._source[0])
            tmp_file.write('\n')
            line_index += 1
        tmp_file.write('import ExampleRstFactory\n')
        tmp_file.write('from ExampleRstFactory import save_figure\n')
        tmp_file.write('ExampleRstFactory.FIGURE_DIRECTORY = "{}"\n'.format(self._rst_directory))
        tmp_file.write('\n')
        for line in self._source[line_index:]:
            if line.startswith('#fig# '):
                tmp_file.write(line[len('#fig# '):])
            elif not line.startswith('pylab.show') or not line.startswith('plt.show'):
                tmp_file.write(line)
            
        tmp_file.flush()
        dev_null = open(os.devnull, 'w')
        try:
            print "Run example", self._source_path
            # if 'diode-characteristic-curve' in self._source_path:
            #     subprocess.check_call(('/bin/cat', tmp_file.name))
            subprocess.check_call((sys.executable, tmp_file.name), stdout=dev_null, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print "Failed to run example", self._source_path

    ##############################################

    def make_circuit_figure(self, force):

        for chunck in self._chuncks:
            if isinstance(chunck, CircuitMacrosImageChunk):
                if force or chunck:
                    chunck.make_figure()

    ##############################################

    def _append_rst_chunck(self):

        self._chuncks.append(self._rst_chunck)
        self._rst_chunck = RstChunk()

    ##############################################

    def _append_code_chunck(self):

        self._chuncks.append(self._code_chunck)
        self._code_chunck = CodeChunk()

    ##############################################

    def _parse_source(self):
        
        """Parse the source and extract chunks of codes, RST contents, figures and circuit macros figures.
        RST content lines start with *#!#*, figures with *#fig#*, circuit macros figures with *#cm#*.

        Comment that must be skipped start with *#?#*.
        """

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
            if line.startswith('#?#'):
                continue
            elif line.startswith('#fig# ') or line.startswith('#cm# '):
                if self._rst_chunck:
                    self._append_rst_chunck()
                elif self._code_chunck:
                    self._append_code_chunck()
                if line.startswith('#fig# '):
                    self._chuncks.append(ImageChunk(line))
                else:
                    self._chuncks.append(CircuitMacrosImageChunk(line, self._source_directory, self._rst_directory))
            elif line.startswith('#!#'):
                if self._code_chunck:
                    self._append_code_chunck()
                self._rst_chunck.append(line.strip()[4:] + '\n') # hack to get blank line
            else:
                # if line.startswith('pylab.show()'):
                #     continue
                if line.startswith('#'*100):
                    continue
                if self._rst_chunck:
                    self._append_rst_chunck()
                self._code_chunck.append(line)
        if self._rst_chunck:
            self._append_rst_chunck()
        elif self._code_chunck:
            self._append_code_chunck()

        if has_coding :
            # Add the coding comment line in the first code block
            for chunck in self._chuncks:
                if isinstance(chunck, CodeChunk) and bool(chunck):
                    chunck.append_head(self._source[0] + '\n')
                    break

    ##############################################

    def make_rst(self):

        """ Generate the example RST file. """

        print "Create RST file", self._rst_path

        title = self._basename.replace('-', ' ').title()
        title_line = '='*(len(title)+2)
        template = """
{title_line}
 {title}
{title_line}

"""

        with open(self._rst_path, 'w') as f:
            f.write(template.format(title=title, title_line=title_line))
            for chunck in self._chuncks:
                f.write(str(chunck))

####################################################################################################

class ExampleRstFactory(object):

    """This class processes recursively the examples directory and generate figures and RST files."""

    ##############################################

    def __init__(self, examples_path, rst_directory):

        self._rst_directory = os.path.realpath(rst_directory)
        self._examples_path = os.path.realpath(examples_path)

        print "Examples Path:", self._examples_path
        print "RST API Path:", self._rst_directory
        print

        if not os.path.exists(self._rst_directory):
            os.mkdir(self._rst_directory)

    ##############################################

    def process_recursively(self, make_figure, make_circuit_figure, force):

        for current_path, sub_directories, files in os.walk(self._examples_path, followlinks=True):
            for filename in files:
                if filename[0].islower() and filename.endswith('.py') and 'flymake' not in filename:
                    example = Example(os.path.join(current_path, filename), self._rst_directory)
                    if force or example:
                        print
                        example.make_rst()
                        if make_figure:
                            example.make_figure()
                    if make_circuit_figure:
                        example.make_circuit_figure(force)

        print "\nGenerate TOC files:"
        for current_path, sub_directories, files in os.walk(self._rst_directory, followlinks=True):
            if sub_directories or files:
                self._process_directory(current_path, sub_directories, files)

    ##############################################

    def _process_directory(self, current_path, sub_directories, files):

        toc_path = os.path.join(current_path, 'index.rst')
        print 'Create TOC', toc_path

        title = os.path.basename(current_path).replace('-', ' ').title()
        title_line = '='*(len(title)+2)

        toc_template = """

.. toctree::
  :maxdepth: 1

"""

        if title == 'Examples':
            template = """
.. include:: ../examples.txt
"""
        else:
            template = """
{title_line}
 {title}
{title_line}
"""

        with open(toc_path, 'w') as f:
            f.write((template + toc_template).format(title=title, title_line=title_line))
            for directory in sorted(sub_directories):
                f.write('  {}/index.rst\n'.format(directory))
            for filename in sorted(files):
                if filename.endswith('.rst') and filename != 'index.rst':
                    f.write('  {}\n'.format(filename))

####################################################################################################
# 
# End
# 
####################################################################################################
