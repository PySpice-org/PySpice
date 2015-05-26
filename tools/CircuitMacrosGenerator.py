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

####################################################################################################

import logging
import os
import subprocess
import shutil
import tempfile

####################################################################################################

# home_path = os.getenv('HOME') # Unix only
home_path = os.path.expanduser('~')
_circuit_macros_path = os.path.join(home_path, 'texmf', 'Circuit_macros')

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def generate(m4_path,
             dst_path,
             density=300,
             transparent='white',
             circuit_macros_path=_circuit_macros_path):

    # Create a temporary directory, it is automatically deleted
    tmp_dir = tempfile.TemporaryDirectory()
    _module_logger.info('Temporary directory ' + tmp_dir.name)
    
    picture_tex_path = os.path.join(tmp_dir.name, 'picture.tex')
    
    picture_tex_header = r'''
\documentclass[11pt]{article}
\usepackage{tikz}
\usetikzlibrary{external}
\tikzexternalize
\pagestyle{empty}
\begin{document}
'''
    
    with open(picture_tex_path, 'w') as f:
        f.write(picture_tex_header)

        m4_process = subprocess.Popen(('m4',
                                      '-I' + circuit_macros_path,
                                      'pgf.m4',
                                      'libcct.m4',
                                      m4_path),
                                      #shell=True,
                                     stdout=subprocess.PIPE,
        )
        dpic_process = subprocess.Popen(('dpic', '-g'),
                                        #shell=True,
                                        stdin=m4_process.stdout,
                                        stdout=subprocess.PIPE)
        m4_process.stdout.close()
        dpic_rc = dpic_process.wait()
        if dpic_rc:
            raise subprocess.CalledProcessError(dpic_rc, 'dpic')
        dpic_output = dpic_process.stdout.read().decode('utf-8')
        f.write(dpic_output)
        f.write(r'\end{document}')

    dev_null = open(os.devnull, 'w')
    
    current_dir = os.curdir
    os.chdir(tmp_dir.name)
    subprocess.check_call(('pdflatex',
                           '-shell-escape',
                           # '-output-directory=' + tmp_dir.name,
                           'picture.tex'),
                          stdout=dev_null, stderr=subprocess.STDOUT)
    os.chdir(current_dir)
    basename = os.path.splitext(os.path.basename(m4_path))[0]
    pdf_path = os.path.join(dst_path, basename + '.pdf')
    png_path = os.path.join(dst_path, basename + '.png')
    _module_logger.info('Generate ' + png_path)
    print('Generate ' + png_path)
    shutil.copy(os.path.join(tmp_dir.name, 'picture-figure0.pdf'), pdf_path)
    subprocess.check_call(('convert',
                           '-density', str(density),
                           '-transparent', str(transparent),
                           pdf_path, png_path),
                          stdout=dev_null, stderr=subprocess.STDOUT)

####################################################################################################
#
# End
#
####################################################################################################
