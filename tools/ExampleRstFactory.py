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

""" This module implements a RST files generator for examples.
"""

####################################################################################################

import glob
import logging
import os
import subprocess
import sys
import tempfile

####################################################################################################

import CircuitMacrosGenerator
import TikzGenerator

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

from PySpice.Spice.Netlist import Pin

class MessageFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().contains('Node in is a Python keyword')

Pin._logger.addFilter(MessageFilter())

####################################################################################################

FIGURE_DIRECTORY = None

####################################################################################################

def remove_extension(filename):
    return os.path.splitext(filename)[0]

def file_extension(filename):
    return os.path.splitext(filename)[1]

####################################################################################################

def sublist_accumulator_iterator(iterable):
    """ From a list (1, 2, 3, ...) this generator yields (), (1,), (1, 2), (1, 2, 3), ... """
    for i in range(len(iterable) +1):
        yield iterable[:i]

####################################################################################################

def save_figure(figure,
                figure_filename):

    """ This function is called from example to save a figure. """

    figure_format = file_extension(figure_filename)[1:] # foo.png -> png
    figure_path = os.path.join(FIGURE_DIRECTORY, figure_filename)
    _module_logger.info("\nSave figure " + figure_path)
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

class Chunk:

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

    def __bool__(self):

        return bool(self._lines)

    ##############################################

    def __str__(self):

        return ''.join(self._lines)

    ##############################################

    def has_format(self):

        for line in self._lines:
            if '@<@' in line:
                return True
        return False

    ##############################################

    def to_rst_format_chunk(self, example, stdout_chunk_index):

        return RstFormatChunk(example, self, stdout_chunk_index)

####################################################################################################

class CodeChunk(Chunk):

    """ This class represents a code block. """

    ##############################################

    def append_head(self, line):

        self._lines.insert(1, line)

    ##############################################

    def __bool__(self):

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

    ##############################################

    def to_python(self):

        source = ''
        for line in self._lines:
            if not line.startswith('pylab.show') and not line.startswith('plt.show'):
                source += line
        return source

####################################################################################################

class HiddenCodeChunk(CodeChunk):

    """ This class represents a code block. """

    ##############################################

    def append(self, line):

        self._lines.append(line[len('#h# '):])

    ##############################################

    def __str__(self):

        return ''

####################################################################################################

class LitteralIncludeChunk(Chunk):

    """ This class represents a litteral include block. """

    ##############################################

    def __init__(self, example, line):

        # Fixme: duplicated code with figure etc. ???
        include_path = line.replace('#itxt# ', '').strip()
        self._include_filename = os.path.basename(include_path)
        source = example.topic.join_path(include_path)
        target = example.topic.join_rst_path(self._include_filename)
        if not os.path.exists(target):
            os.symlink(source, target)

    ##############################################

    def __str__(self):

        template = '''
.. literalinclude:: {}

'''
        return template.format(self._include_filename)

####################################################################################################

class PythonIncludeChunk(Chunk):

    """ This class represents a Python litteral include block. """

    ##############################################

    def __init__(self, example, line):

        self._include_path = line.replace('#i# ', '').strip()
        # Fixme: relpath right ?
        source = os.path.relpath(example.topic.join_path(self._include_path), example.topic.rst_path)
        target = example.topic.join_rst_path(self._include_path)
        if not os.path.exists(target):
            os.symlink(source, target)

    ##############################################

    def __str__(self):

        template = '''
.. getthecode:: {}
  :language: python

'''
        return template.format(self._include_path)

####################################################################################################

class ImageChunk(Chunk):

    ##############################################

    @staticmethod
    def parse_args(line):

        parts = [x for x in line.split(' ') if x]
        figure_path = parts[0]
        kwargs = {}
        for part in parts[1:]:
            if '=' in part:
                key, value = [x.strip() for x in part.split('=')]
                if key and value:
                    kwargs[key] = value
        return figure_path, kwargs

    ##############################################

    def __init__(self, figure_path, scale='', width='', height='', align=''):

        self._figure_path = figure_path
        self._scale = scale
        self._width = width
        self._height = height
        self._align = align

    ##############################################

    def __str__(self):

        template = '''
.. image:: {0._figure_path}
  :align: center
'''
        rst_code = template.format(self)
        for key in ('scale', 'width', 'height'):
            value = getattr(self, '_' + key)
            if value:
                rst_code += '  :{0}: {1}\n'.format(key, value)
        return rst_code + '\n'

####################################################################################################

class FigureChunk(ImageChunk):

    """ This class represents an image block for a saved figure. """

    ##############################################

    def __init__(self, line):

        # weak ...
        Chunk.__init__(self) # Fixme: better way ???
        self.append(line)
        figure_path = line[line.rindex(", '")+3:line.rindex("')")]
        super().__init__(figure_path)

    ##############################################

    def to_python(self):

        return self._lines[0][len('#fig# '):]

####################################################################################################

class LocaleFigureChunk(ImageChunk):

    """ This class represents an image block for a figure. """

    ##############################################

    def __init__(self, line, source_directory, rst_directory):

        figure_path, kwargs = ImageChunk.parse_args(line[len('#lfig# '):].strip())
        figure_filename = os.path.basename(figure_path)
        figure_absolut_path = os.path.join(source_directory, figure_path)
        link_path = os.path.join(rst_directory, figure_filename)
        super().__init__(figure_filename, **kwargs)

        if not os.path.exists(link_path):
            os.symlink(figure_absolut_path, link_path)

####################################################################################################

class CircuitMacrosImage:

    """ This class represents a circuit macros figure. """

    _logger = _module_logger.getChild('CircuitMacrosImage')

    ##############################################

    def __init__(self, m4_filename, source_directory, rst_directory):

        png_filename = m4_filename.replace('.m4', '.png')
        self._m4_path = os.path.join(source_directory, 'm4', m4_filename)
        self._rst_directory = rst_directory
        self._figure_path = png_filename
        self._figure_real_path = os.path.join(rst_directory, png_filename)

    ##############################################

    def __bool__(self):

        if os.path.exists(self._figure_real_path):
            return timestamp(self._m4_path) > timestamp(self._figure_real_path)
        else:
            return True

    ##############################################

    def make_figure(self):

        self._logger.info("\nMake circuit figure " + self._m4_path)
        try:
            CircuitMacrosGenerator.generate(self._m4_path, self._rst_directory)
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make circuit figure example", self._m4_path)

####################################################################################################

class CircuitMacrosImageChunk(CircuitMacrosImage, ImageChunk):

    """ This class represents an image block for a circuit macros figure. """

    ##############################################

    def __init__(self, line, source_directory, rst_directory):

        m4_filename, kwargs = ImageChunk.parse_args(line[len('#cm# '):].strip())
        ImageChunk.__init__(self, None, **kwargs) # Fixme: _figure_path
        CircuitMacrosImage.__init__(self, m4_filename, source_directory, rst_directory)

####################################################################################################

class TikzImage:

    """ This class represents a Tikz figure. """

    _logger = _module_logger.getChild('TikzImage')

    ##############################################

    def __init__(self, tex_filename, source_directory, rst_directory):

        svg_filename = tex_filename.replace('.tex', '.svg')
        self._tex_path = os.path.join(source_directory, 'tex', tex_filename)
        self._rst_directory = rst_directory
        self._figure_path = svg_filename
        self._figure_real_path = os.path.join(rst_directory, svg_filename)

    ##############################################

    def __bool__(self):

        if os.path.exists(self._figure_real_path):
            return timestamp(self._tex_path) > timestamp(self._figure_real_path)
        else:
            return True

    ##############################################

    def make_figure(self):

        self._logger.info("\nMake Tikz figure " + self._tex_path)
        try:
            TikzGenerator.generate(self._tex_path, self._rst_directory)
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make circuit figure example", self._tex_path)

####################################################################################################

class TikzImageChunk(TikzImage, ImageChunk):

    """ This class represents an image block for a Tikz figure. """

    ##############################################

    def __init__(self, line, source_directory, rst_directory):

        tex_filename, kwargs = ImageChunk.parse_args(line[len('#tz# '):].strip())
        ImageChunk.__init__(self, None, **kwargs) # Fixme: _figure_path
        TikzImage.__init__(self, tex_filename, source_directory, rst_directory)

####################################################################################################

class StdoutChunk(Chunk):

    """ This class represents an output block. """

    ##############################################

    def __init__(self, example, stdout_chunk_index):

        self._example = example
        self._stdout_chunk_index = stdout_chunk_index

    ##############################################

    @property
    def stdout_chunk_index(self):
        return self._stdout_chunk_index

####################################################################################################

class OutputChunk(StdoutChunk):

    ##############################################

    def __init__(self, example, line, stdout_chunk_index):

        StdoutChunk.__init__(self, example, stdout_chunk_index)
        self._line = line

    ##############################################

    def __str__(self):

        # Fixme: use content ???
        slice_, content = self._example.stdout_chunk(self._stdout_chunk_index)
        lower = slice_.start
        upper = slice_.stop -1
        # Sphynx count \f as newline
        if self._stdout_chunk_index:
            lower += self._stdout_chunk_index
            upper += self._stdout_chunk_index

        template = '''
.. literalinclude:: {}
    :lines: {}-{}

'''
        return template.format(os.path.basename(self._example.stdout_path), lower+1, upper+1)

    ##############################################

    def to_python(self):

        return 'print("\f #{}")\n'.format(self._stdout_chunk_index)

####################################################################################################

class RstFormatChunk(StdoutChunk):

    ##############################################

    def __init__(self, example, rst_chunk, stdout_chunk_index):

        StdoutChunk.__init__(self, example, stdout_chunk_index)
        self._lines = rst_chunk._lines

    ##############################################

    def __str__(self):

        slice_, content = self._example.stdout_chunk(self._stdout_chunk_index)
        return content

    ##############################################

    def to_python(self):

        rst = ''.join(self._lines)
        rst = rst.replace('{', '{{')
        rst = rst.replace('}', '}}')
        rst = rst.replace('@<@', '{')
        rst = rst.replace('@>@', '}')
        rst = rst.replace('@@<<@@', '@<@')
        rst = rst.replace('@@>>@@', '@>@')
        marker = "\f #{}".format(self._stdout_chunk_index)
        return 'print(r"""' + rst + '""".format(**locals()))\n' + 'print("' + marker + '")\n'

####################################################################################################

class Chunks(list):
    pass

####################################################################################################

class Example:

    """ This class is responsible to process an example. """

    _logger = _module_logger.getChild('Example')

    ##############################################

    def __init__(self, topic, filename):

        self._topic = topic
        self._basename = remove_extension(filename)

        path = topic.join_path(filename)
        self._is_link = os.path.islink(path)
        self._path = os.path.realpath(path)

        if self._is_link:
            factory = self._topic.factory
            path = factory.join_rst_example_path(os.path.relpath(self._path, factory.examples_path))
            self._rst_path = remove_extension(path) + '.rst'
        else:
            self._rst_path = self._topic.join_rst_path(self.rst_filename)

        self._stdout = None

        self._stdout_chunck_counter = -1

    ##############################################

    @property
    def topic(self):
        return self._topic

    @property
    def path(self):
        return self._path

    @property
    def basename(self):
        return self._basename

    @property
    def rst_filename(self):
        return self._basename + '.rst'

    @property
    def rst_inner_path(self):
        return os.path.sep + os.path.relpath(self._rst_path, self._topic.factory.rst_source_directory)

    @property
    def stdout_path(self):
        # return remove_extension(self._rst_path) + '.stdout'
        return self._topic.join_rst_path(self._basename + '.stdout')

    @property
    def stderr_path(self):
        # return remove_extension(self._rst_path) + '.stdout'
        return self._topic.join_rst_path(self._basename + '.stderr')

    ##############################################

    def increment_stdout_chunk_counter(self):
        self._stdout_chunck_counter += 1
        return self._stdout_chunck_counter

    def stdout_chunk(self, i):
        return self._stdout_chunks[i]

    ##############################################

    @property
    def is_link(self):
        return self._is_link

    ##############################################

    def read(self):

        # Must be called first !

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

    def __bool__(self):

        return self.source_timestamp > self.rst_timestamp

    ##############################################

    def make_figure(self):

        """This function make a temporary copy of the example with calls to *save_figure* and run it.
        """

        working_directory = os.path.dirname(self._path)

        # tmp_file = tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), prefix='PySpice-', suffix='.py', mode='w')
        tmp_file = tempfile.NamedTemporaryFile(dir=working_directory,
                                               prefix='__example_rst_factory__', suffix='.py', mode='w')
        tmp_file.write('import ExampleRstFactory\n')
        tmp_file.write('from ExampleRstFactory import save_figure\n')
        tmp_file.write('ExampleRstFactory.FIGURE_DIRECTORY = "{}"\n'.format(self._topic.rst_path))
        tmp_file.write('\n')
        for chunck in self._chuncks:
            if isinstance(chunck, (CodeChunk, FigureChunk, OutputChunk, RstFormatChunk)):
                tmp_file.write(chunck.to_python())
        tmp_file.flush()

        self._logger.info("\nRun example " + self._path)
        # with open(tmp_file.name, 'r') as f:
        #     print(f.read())
        with open(self.stdout_path, 'w') as stdout:
            with open(self.stderr_path, 'w') as stderr:
                env = dict(os.environ)
                env['PySpiceLogLevel'] = 'WARNING'
                process = subprocess.Popen((sys.executable, tmp_file.name),
                                           stdout=stdout,
                                           stderr=stderr,
                                           cwd=working_directory,
                                           env=env)
                rc = process.wait()
                if rc:
                    self._logger.error("Failed to run example " + self._path)
                    self._topic.factory.register_failure(self)

    ##############################################

    def make_circuit_figure(self, force):

        for chunck in self._chuncks:
            if isinstance(chunck, (CircuitMacrosImageChunk, TikzImageChunk)):
                if force or chunck:
                    chunck.make_figure()

    ##############################################

    def _append_rst_chunck(self):

        # if self._rst_chunck:
        chunk = self._rst_chunck
        if chunk.has_format():
            chunk = chunk.to_rst_format_chunk(self, self.increment_stdout_chunk_counter())
        self._chuncks.append(chunk)
        self._rst_chunck = RstChunk()

    ##############################################

    def _append_code_chunck(self, hidden=False):

        if self._code_chunck:
            self._chuncks.append(self._code_chunck)
        if hidden:
            self._code_chunck = HiddenCodeChunk()
        else:
            self._code_chunck = CodeChunk()

    ##############################################

    def _parse_source(self):

        """Parse the Python source code and extract chunks of codes, RST contents, plot, circuit macros and
        Tikz figures.  The source code is annoted using comment lines starting with special
        directives of the form *#directive name#*.  RST content lines start with *#!#*.  We can
        include a figure using *#lfig#*, a figure generated by matplotlib using the directive
        *#fig#*, circuit macros figure using *#cm#*, tikz figure using *#tz#* and the content of a
        file using *#itxt#* and *#i#* for Python source.  Comment that must be skipped start with
        *#?#*.  Hidden Python code start with *#h#*.  The directive *#o#* is used to split the
        output and to instruct to include the previous chunk.  RST content can be formatted with
        variable from the locals dictionary using *@<@...@>@* instead of *{...}*.

        """

        self._chuncks = Chunks()
        self._rst_chunck = RstChunk()
        self._code_chunck = CodeChunk()

        # Use a while loop trick to remove consecutive blank lines
        number_of_lines = len(self._source)
        i = 0
        while i < number_of_lines:
            line = self._source[i]
            i += 1
            remove_next_blanck_line = True
            if (line.startswith('#?#')
                or line.startswith('#'*10)
                or line.startswith(' '*4 + '#'*10)):
                pass # these comments
            elif (line.startswith('#fig# ')
                  or line.startswith('#lfig# ')
                  or line.startswith('#cm# ')
                  or line.startswith('#tz# ')
                  or line.startswith('#i# ')
                  or line.startswith('#itxt# ')
                  or line.startswith('#o#')):
                if self._rst_chunck:
                    self._append_rst_chunck()
                elif self._code_chunck:
                    self._append_code_chunck()
                if line.startswith('#fig# '):
                    self._chuncks.append(FigureChunk(line))
                elif line.startswith('#lfig# '):
                    self._chuncks.append(LocaleFigureChunk(line, self._topic.path, self._topic.rst_path))
                elif line.startswith('#cm# '):
                    self._chuncks.append(CircuitMacrosImageChunk(line, self._topic.path, self._topic.rst_path))
                elif line.startswith('#tz# '):
                    self._chuncks.append(TikzImageChunk(line, self._topic.path, self._topic.rst_path))
                elif line.startswith('#i# '):
                    self._chuncks.append(PythonIncludeChunk(self, line))
                elif line.startswith('#itxt# '):
                    self._chuncks.append(LitteralIncludeChunk(self, line))
                elif line.startswith('#o#'):
                    self._chuncks.append(OutputChunk(self, line, self.increment_stdout_chunk_counter()))
            elif line.startswith('#!#'): # RST content
                if self._code_chunck:
                    self._append_code_chunck()
                self._rst_chunck.append(line.strip()[4:] + '\n') # hack to get blank line
            else: # Python code
                # if line.startswith('pylab.show()'):
                #     continue
                remove_next_blanck_line = False
                if self._rst_chunck:
                    self._append_rst_chunck()
                if line.startswith('#h#') and isinstance(self._code_chunck, CodeChunk):
                    self._append_code_chunck(True)
                elif isinstance(self._code_chunck, HiddenCodeChunk):
                    self._append_code_chunck(False)
                self._code_chunck.append(line)
            if remove_next_blanck_line and i < number_of_lines and not self._source[i].strip():
                i += 1
        if self._rst_chunck:
            self._append_rst_chunck()
        elif self._code_chunck:
            self._append_code_chunck()

    ##############################################

    def _read_output_chunk(self):

        # Read the stdout and split in chunck
        with open(self.stdout_path) as f:
            self._stdout = f.read()
        self._stdout_chunks = []
        start = 0
        last_i = -1
        lines = self._stdout.split('\n')
        for i, line in enumerate(lines): # Fixme: portability
            if line.startswith('\f'):
                slice_ = slice(start, i)
                self._stdout_chunks.append((slice_, '\n'.join(lines[slice_])))
                start = i + 1
            last_i = i
        # Fixme: add last empty line ?
        if start <= last_i:
            slice_ = slice(start, last_i +1)
            self._stdout_chunks.append((slice_, '\n'.join(lines[slice_])))

    ##############################################

    def make_rst(self):

        """ Generate the example RST file. """

        self._logger.info("\nCreate RST file " + self._rst_path)

        self._read_output_chunk()

        has_title= False
        for chunck in self._chuncks:
            # self._logger.info('Chunck {0.__class__.__name__}'.format(chunck))
            if isinstance(chunck, RstChunk):
                content = str(chunck)
                if '='*7 in content:
                    has_title = True
                break

        if not has_title:
            title = self._basename.replace('-', ' ').title() # Fixme: Capitalize of
            title_line = '='*(len(title)+2)
            template = """
{title_line}
 {title}
{title_line}

"""
            header = template.format(title=title, title_line=title_line)
        else:
            header = ''

        # place the Python file in the rst path
        python_file_name = self._basename + '.py'
        link_path = self._topic.join_rst_path(python_file_name)
        if not os.path.exists(link_path):
            os.symlink(self._path, link_path)

        includes = """
.. include:: /project-links.txt
.. include:: /abbreviation.txt
"""

        with open(self._rst_path, 'w') as f:
            f.write(includes)
            if not has_title:
                f.write(header)
            template = """
.. getthecode:: {filename}
    :language: python

"""
            f.write(template.format(filename=python_file_name))
            for chunck in self._chuncks:
                f.write(str(chunck))

            # f.write(self._output)

####################################################################################################

class Topic:

    _logger = _module_logger.getChild('Topic')

    ##############################################

    def __init__(self, factory, relative_path):

        self._factory = factory
        self._relative_path = relative_path
        self._basename = os.path.basename(relative_path)

        self._path = self._factory.join_examples_path(relative_path)
        self._rst_path = self._factory.join_rst_example_path(relative_path)

        self._subtopics = [] # self._retrieve_subtopics()
        self._examples = []
        self._links = []
        python_files = [filename for filename in self._python_files_iterator()
                        if self._filter_python_files(filename)]
        if python_files:
            self._logger.info("\nProcess Topic: " + relative_path)
            self._make_hierarchy()
            for filename in python_files:
                example = Example(self, filename)
                if example.is_link:
                    self._logger.info("\n  found link: " + filename)
                    self._links.append(example)
                else:
                    self._logger.info("\n  found: " + filename)
                    self._examples.append(example)

    ##############################################

    def __bool__(self):
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

    def _files_iterator(self, extension):

        pattern = os.path.join(self._path, '*.' + extension)
        for file_path in glob.glob(pattern):
            yield os.path.basename(file_path)

    ##############################################

    def _python_files_iterator(self):

        return self._files_iterator('py')

    ##############################################

    def _m4_files_iterator(self):

        return self._files_iterator('m4')

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

    def _read_readme(self, make_circuit_figure):

        figures = []
        image_directive = '.. image:: '
        image_directive_length = len(image_directive)
        with open(self._readme_path()) as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith(image_directive):
                    figure = line[image_directive_length:]
                    figures.append(figure)

        # Fixme: m4 path, tikz ???
        if make_circuit_figure:
            m4_files = list(self._m4_files_iterator())
            for figure in figures:
                m4_file = figure.replace('.png', '.m4')
                if m4_file in m4_files:
                    CircuitMacrosImage(m4_file, self._path, self._rst_path).make_figure()

        return content

    ##############################################

    def _example_hierarchy(self):

        """ Return a list of directory corresponding to the file hierarchy after ``.../examples/`` """

        return self._relative_path.split(os.path.sep)

    ##############################################

    def _make_hierarchy(self):

        """ Create the file hierarchy. """

        example_hierarchy = self._example_hierarchy()
        for directory_list in sublist_accumulator_iterator(example_hierarchy):
            directory = self._factory.join_rst_example_path(*directory_list)
            if not os.path.exists(directory):
                os.mkdir(directory)

    ##############################################

    def process_examples(self, make_figure, make_circuit_figure, force):

        for example in self._examples:
            self.process_example(example, make_figure, make_circuit_figure, force)

    ##############################################

    def process_example(self, example, make_figure, make_circuit_figure, force):

        example.read()
        if force or example:
            if make_figure:
                example.make_figure()
            example.make_rst()
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

    def make_toc(self, make_circuit_figure):

        """ Create the TOC. """

        if not self:
            return

        toc_path = self.join_rst_path('index.rst')
        self._logger.info("\nCreate TOC " + toc_path)

        title = self._basename.replace('-', ' ').title() # Fixme: Capitalize of
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
            content = self._read_readme(make_circuit_figure)
            # protect for .format()
            content = content.replace('{', '{{').replace('}', '}}')
            template += content + '\n' # insert a new line for '.. End'

        # Sort the TOC
        file_dict = {x.basename:x.rst_filename for x in self._examples}
        file_dict.update({x.basename:x.rst_inner_path for x in self._links})
        keys = sorted(file_dict.keys())

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
        if counter_strings:
            template += 'This section has '
            if len(counter_strings) == 1:
                template += counter_strings[0]
            elif len(counter_strings) == 2:
                template += counter_strings[0] + ' and ' + counter_strings[1]
            elif len(counter_strings) == 3:
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

class ExampleRstFactory:

    """This class processes recursively the examples directory and generate figures and RST files."""

    _logger = _module_logger.getChild('ExampleRstFactory')

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

        self._logger.info("\nExamples Path: " + self._examples_path)
        self._logger.info("\nRST Path: " + self._rst_example_directory)

        self._example_failures = []

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
            topic.make_toc(make_circuit_figure)

        if self._example_failures:
            self._logger.warning("These examples failed:\n" +
                                 '\n'.join([example.path for example in self._example_failures]))

    ##############################################

    def register_failure(self, example):

        self._example_failures.append(example)
