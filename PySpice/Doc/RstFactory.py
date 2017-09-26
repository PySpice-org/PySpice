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

""" This module provides tools to build a Sphinx API documentation. """

####################################################################################################

import os

####################################################################################################

class RstFactory:

    """ This class build recursively a Sphinx API documentation from a Python root module. """

    init_file_name = '__init__.py'

    end_marker = """
.. End
"""

    ##############################################

    def __init__(self, module_path, rst_directory, excluded_directory):

        self._rst_directory = os.path.realpath(rst_directory)
        self._root_module_path = os.path.realpath(module_path)

        self._excluded_directory = [os.path.join(self._root_module_path, x) for x in excluded_directory]
        self._root_module_name = os.path.basename(self._root_module_path)

        print("RST API Path:    ", self._rst_directory)
        print("Root Module Path:", self._root_module_path)
        print("Root Module Name:", self._root_module_name)
        print('Exclude:', '\n  '.join(self._excluded_directory))

        if not os.path.exists(self._rst_directory):
            os.mkdir(self._rst_directory)

        self._process_recursively()

    ##############################################

    def _process_recursively(self):

        """ Process recursively the inner Python files and directories. """

        for module_path, sub_directories, files in os.walk(self._root_module_path, followlinks=True):
            for sub_directory in list(sub_directories):
                if os.path.join(module_path, sub_directory) in self._excluded_directory:
                    del sub_directories[sub_directories.index(sub_directory)]
            if self.is_python_directory_module(module_path):
                python_files = [file_name
                                for file_name in files
                                if self.is_python_file(file_name)]
                sub_modules = [sub_directory
                               for sub_directory in sub_directories
                               if self.is_python_directory_module(os.path.join(module_path, sub_directory))]
                if python_files or sub_modules:
                    self._process_directory_module(module_path, sorted(python_files), sorted(sub_modules))

    ##############################################

    def _process_directory_module(self, module_path, python_files, sub_modules):

        directory_module_name = os.path.basename(module_path)
        directory_module_python_path = self.module_path_to_python_path(module_path)
        dst_directory = self.join_rst_path(self.python_path_to_path(directory_module_python_path))
        print()
        print("Directory Module Name:", directory_module_name)
        print("Directory Module Python Path:", directory_module_python_path)
        print("Dest Path:", dst_directory)

        if not os.path.exists(dst_directory):
            os.mkdir(dst_directory)

        # Generate a RST file per module
        module_names = []
        for file_name in python_files:
            module_name = self.filename_to_module(file_name)
            module_names.append(module_name)
            print("  Module:", module_name)
            rst = self._generate_rst_module(directory_module_python_path, module_name)
            rst_file_name = os.path.join(dst_directory, module_name + '.rst')
            with open(rst_file_name, 'w') as f:
                f.write(rst)

        # Generate the TOC RST file
        rst = self._generate_toc(directory_module_name, sorted(module_names + sub_modules))
        rst += '\n'
        rst += self._generate_automodule(directory_module_python_path)
        rst += self.end_marker
        rst_file_name = os.path.join(os.path.dirname(dst_directory), directory_module_name + '.rst')
        with open(rst_file_name, 'w') as f:
            f.write(rst)

    ##############################################

    @staticmethod
    def is_python_directory_module(path):

        return os.path.exists(os.path.join(path, RstFactory.init_file_name))

    ##############################################

    @staticmethod
    def is_python_file(file_name):

        return (file_name.endswith('.py') and
                file_name != RstFactory.init_file_name and
                'flymake'not in file_name)

    ##############################################

    @staticmethod
    def path_to_python_path(path):

        return path.replace(os.path.sep, '.')

    ##############################################

    @staticmethod
    def python_path_to_path(python_path):

        return python_path.replace('.', os.path.sep)

    ##############################################

    @staticmethod
    def join_python_path(*args):

        return '.'.join(args)

    ##############################################

    @staticmethod
    def filename_to_module(file_name):

        return file_name[:-3] # suppress '.py'

    ##############################################

    def module_path_to_python_path(self, path):

        return self.path_to_python_path(self._root_module_name + path[len(self._root_module_path):])

    ##############################################

    def join_rst_path(self, path):

        return os.path.join(self._rst_directory, path)

    ##############################################

    def _generate_title(self, module_name):

        mod_rst = ' :mod:`'

        template = """
%(header_line)s
%(mod)s%(module_name)s`
%(header_line)s"""

        rst = template.lstrip() % dict(
            module_name=module_name,
            mod=mod_rst,
            header_line='*'*(len(module_name) + len(mod_rst) +2),
            )

        return rst

    ##############################################

    def _generate_toc(self, directory_module_name, module_names):

        template = """%(title)s

.. toctree::
"""

        rst = template.lstrip() % dict(
            title=self._generate_title(directory_module_name),
            )

        for module_name in module_names:
            rst += ' '*2 + os.path.join(directory_module_name, module_name) + '\n'

        return rst

    ##############################################

    def _generate_automodule(self, module_path):

        template = """
.. automodule:: %(module_path)s
   :members:
   :show-inheritance:
"""

        rst = template.lstrip() % dict(
            module_path=module_path,
            )

        return rst

    ##############################################

    def _generate_rst_module(self, module_path, module_name):

        template = """%(title)s

%(automodule)s
"""

        rst = template.lstrip() % dict(
            title=self._generate_title(module_name),
            automodule=self._generate_automodule(RstFactory.join_python_path(module_path, module_name))
            )
        rst += self.end_marker

        return rst
