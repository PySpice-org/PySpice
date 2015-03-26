####################################################################################################
# 
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

""" This module implements a generator of RST files for examples.
"""

####################################################################################################

import glob
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

class IncludeChunk(Chunk):

    """ This class represents a litteral include block. """

    ##############################################

    def __init__(self, example, line):

        self._include_path = line.replace('#i# ', '').strip()
        source = os.path.relpath(example.topic.join_path(self._include_path), example.topic.rst_path)
        target = example.topic.join_rst_path(self._include_path)
        if not os.path.exists(target):
            os.symlink(source, target)

    ##############################################

    def __str__(self):

            return '''
.. getthecode:: {}
  :language: python

'''.format(self._include_path) 

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

    def __init__(self, topic, filename):

        self._topic = topic
        self._basename = os.path.splitext(filename)[0]

        path = topic.join_path(filename)
        self._is_link = os.path.islink(path)
        self._path = os.path.realpath(path)

        if self._is_link:
            factory = self._topic.factory
            path = factory.join_rst_example_path(os.path.relpath(self._path, factory.examples_path))
            self._rst_path = os.path.splitext(path)[0] + '.rst'
        else:
            self._rst_path = self._topic.join_rst_path(self.rst_filename)

    ##############################################

    @property
    def topic(self):
        return self._topic

    @property
    def basename(self):
        return self._basename

    @property
    def rst_filename(self):
        return self._basename + '.rst'

    @property
    def rst_inner_path(self):
        return os.path.sep + os.path.relpath(self._rst_path, self._topic.factory.rst_source_directory)

    ##############################################

    @property
    def is_link(self):
        return self._is_link

    ##############################################

    def read(self):

        with open(self._path) as f:
            self._source = f.readlines()
        self._parse_source()

    ##############################################

    @property
    def source_timestamp(self):

        return timestamp(self._path)

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
        tmp_file.write('ExampleRstFactory.FIGURE_DIRECTORY = "{}"\n'.format(self._topic.rst_path))
        tmp_file.write('\n')
        for line in self._source[line_index:]:
            if line.startswith('#fig# '):
                tmp_file.write(line[len('#fig# '):])
            elif not line.startswith('pylab.show') and not line.startswith('plt.show'):
                tmp_file.write(line)
            
        tmp_file.flush()
        dev_null = open(os.devnull, 'w')
        try:
            print "Run example", self._path
            # if 'diode-characteristic-curve' in self._path:
            #     subprocess.check_call(('/bin/cat', tmp_file.name))
            subprocess.check_call((sys.executable, tmp_file.name), stdout=dev_null, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print "Failed to run example", self._path

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
            elif line.startswith('#i# '):
                self._chuncks.append(IncludeChunk(self, line))
            elif line.startswith('#fig# ') or line.startswith('#cm# '):
                if self._rst_chunck:
                    self._append_rst_chunck()
                elif self._code_chunck:
                    self._append_code_chunck()
                if line.startswith('#fig# '):
                    self._chuncks.append(ImageChunk(line))
                else:
                    self._chuncks.append(CircuitMacrosImageChunk(line, self._topic.path, self._topic.rst_path))
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

        has_tile= False
        for chunck in self._chuncks:
            if isinstance(chunck, RstChunk):
                content = str(chunck)
                if '='*7 in content:
                    has_tile = True
                break

        if not has_tile:
            title = self._basename.replace('-', ' ').title()
            title_line = '='*(len(title)+2)
            template = """
{title_line}
 {title}
{title_line}

"""
            header = template.format(title=title, title_line=title_line)

        with open(self._rst_path, 'w') as f:
            if not has_tile:
                f.write(header)
            template = """
.. raw:: html

  <div class="getthecode">
    <div class="getthecode-header">
      <span class="getthecode-filename">RingModulator.py</span>
      <a href="../../_downloads/RingModulator.py"><span>RingModulator.py</span></a>
    </div>
  </div>
"""
            f.write(template)
            for chunck in self._chuncks:
                f.write(str(chunck))

####################################################################################################

class Topic(object):

    ##############################################

    def __init__(self, factory, relative_path):

        self._factory = factory
        self._relative_path = relative_path
        self._basename = os.path.basename(relative_path)

        self._path = self._factory.join_examples_path(relative_path)
        self._rst_path = self._factory.join_rst_example_path(relative_path)

        self._examples = []
        self._links = []
        python_files = [filename for filename in self._python_files_iterator()
                        if self._filter_python_files(filename)]
        if python_files:
            print 'Process Topic: {}'.format(relative_path)
            self._make_hierarchy()
            for filename in python_files:
                example = Example(self, filename)
                if example.is_link:
                    print '  found link: {}'.format(filename)
                    self._links.append(example)
                else:
                    print '  found: {}'.format(filename)
                    self._examples.append(example)

    ##############################################

    def __nonzero__(self):
        return os.path.exists(self._rst_path)
        # return bool(self._examples) or bool(self._links)

    ##############################################

    @property
    def factory(self):
        return self._factory

    @property
    def basename(self):
        return self._basename

    @property
    def path(self):
        return self._path

    @property
    def rst_path(self):
        return self._rst_path

    ##############################################

    def join_path(self, filename):
        return os.path.join(self._path, filename)

    def join_rst_path(self, filename):
        return os.path.join(self._rst_path, filename)

    ##############################################

    def _python_files_iterator(self):

        pattern = os.path.join(self._path, '*.py')
        for file_path in glob.glob(pattern):
            yield os.path.basename(file_path)

    ##############################################

    @staticmethod
    def _filter_python_files(filename):
        return filename[0].islower() and filename.endswith('.py') and 'flymake' not in filename

    ##############################################

    def _readme_path(self):
        return self.join_path('readme.rst')

    ##############################################

    def _has_readme(self):
        return os.path.exists(self._readme_path())

    ##############################################

    def _example_hierarchy(self):

        """ Return a list of directory corresponding to the file hierarchy after ``.../examples/`` """

        return self._relative_path.split(os.path.sep)

    ##############################################

    def _make_hierarchy(self):

        """ Create the file hierarchy. """

        example_hierarchy = self._example_hierarchy()
        for i in xrange(len(example_hierarchy) +1):
            directory = self._factory.join_rst_example_path(*example_hierarchy[:i])
            if not os.path.exists(directory):
                os.mkdir(directory)
        return directory

    ##############################################

    def process_examples(self, make_figure, make_circuit_figure, force):

        for example in self._examples:
            example.read()
            if force or example:
                print
                example.make_rst()
                if make_figure:
                    example.make_figure()
            if make_circuit_figure:
                example.make_circuit_figure(force)

    ##############################################

    def _retrieve_subtopics(self):

        if not self:
            return None

        subtopics = []
        for filename in os.listdir(self._rst_path):
            path = self.join_rst_path(filename)
            if os.path.isdir(path):
                if os.path.exists(os.path.join(path, 'index.rst')):
                    relative_path = os.path.relpath(path, self._factory.rst_example_directory)
                    topic = self._factory.topics[relative_path]
                    subtopics.append(topic)
        self._subtopics = subtopics

    ##############################################

    def make_toc(self):

        """ Create the TOC. """

        if not self:
            return

        toc_path = self.join_rst_path('index.rst')
        print 'Create TOC', toc_path

        title = self._basename.replace('-', ' ').title()
        title_line = '='*(len(title)+2)

        if not title:
            template = """
.. include:: ../examples.txt
"""
        else:
            template = """
{title_line}
 {title}
{title_line}
"""

        if self._has_readme():
            with open(self._readme_path(), 'r') as f:
                template += f.read()

        # Sort the TOC
        file_dict = {x.basename:x.rst_filename for x in self._examples}
        file_dict.update({x.basename:x.rst_inner_path for x in self._links})
        keys = sorted(file_dict.iterkeys())

        self._retrieve_subtopics()
        subtopics = [topic.basename for topic in self._subtopics]

        self._number_of_examples = len(self._examples) # don't count links twice
        number_of_links = len(self._links)
        number_of_examples = self._number_of_examples + sum([topic._number_of_examples
                                                             for topic in self._subtopics])
        counter_strings = []
        if self._subtopics:
            counter_strings.append('{} sub-topics'.format(len(self._subtopics)))
        if number_of_examples:
            counter_strings.append('{} examples'.format(number_of_examples))
        if number_of_links:
            counter_strings.append('{} related examples'.format(number_of_links))

        template += 'This section has '
        if len(counter_strings) == 1:
            template += counter_strings[0]
        elif len(counter_strings) == 2:
            template += counter_strings[0] + ' and ' + counter_strings[1]
        else:
            template += counter_strings[0] + ', ' + counter_strings[1] + ' and ' + counter_strings[2]
        template += '.\n'

        toc_template = """

.. toctree::
  :maxdepth: 1

"""

        with open(toc_path, 'w') as f:
            f.write((template + toc_template).format(title=title, title_line=title_line))
            for subtopic in sorted(subtopics):
                f.write('  {}/index.rst\n'.format(subtopic))
            for key in keys:
                filename = file_dict[key]
                f.write('  {}\n'.format(filename))

####################################################################################################

class ExampleRstFactory(object):

    """This class processes recursively the examples directory and generate figures and RST files."""

    ##############################################

    def __init__(self, examples_path, rst_source_directory, rst_example_directory):

        """
        Parameters:
        -----------

        examples_path: string
            path of the examples

        rst_source_directory: string
            path of the RST source directory

        rst_example_directory: string
            relative path of the examples in the RST sources
        """

        self._examples_path = os.path.realpath(examples_path)

        self._rst_source_directory = os.path.realpath(rst_source_directory)
        self._rst_example_directory = os.path.join(self._rst_source_directory, rst_example_directory)
        if not os.path.exists(self._rst_example_directory):
            os.mkdir(self._rst_example_directory)

        self._topics = {}

        print "Examples Path:", self._examples_path
        print "RST Path:", self._rst_example_directory
        print

    ##############################################

    @property
    def examples_path(self):
        return self._examples_path

    @property
    def rst_source_directory(self):
        return self._rst_source_directory

    @property
    def rst_example_directory(self):
        return self._rst_example_directory

    @property
    def topics(self):
        return self._topics

    ##############################################

    def join_examples_path(self, *args):
        return os.path.join(self._examples_path, *args)

    def join_rst_example_path(self, *args):
        return os.path.join(self._rst_example_directory, *args)
    
    ##############################################

    def process_recursively(self, make_figure=True, make_circuit_figure=True, force=False):

        """ Process recursively the examples directory. """

        # walk top down so as to generate the subtopics first
        self._topics.clear()
        for current_path, sub_directories, files in os.walk(self._examples_path,
                                                            topdown=False,
                                                            followlinks=True):
            relative_current_path = os.path.relpath(current_path, self._examples_path)
            if relative_current_path == '.':
                relative_current_path = ''
            topic = Topic(self, relative_current_path)
            self._topics[relative_current_path] = topic # collect the topics
            topic.process_examples(make_figure, make_circuit_figure, force)
            topic.make_toc()

####################################################################################################
# 
# End
# 
####################################################################################################
