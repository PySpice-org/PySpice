####################################################################################################

export PySpice_source_path=${PWD}
export PySpice_examples_path=${PySpice_source_path}/examples

source ${HOME}/python-virtual-env/py3-pyqt5/bin/activate
append_to_python_path_if_not ${PySpice_source_path}
append_to_python_path_if_not ${PySpice_source_path}/tools

append_to_path_if_not /usr/local/stow/ngspice-26/bin
append_to_ld_library_path_if_not /usr/local/stow/ngspice-26/lib/

####################################################################################################
# 
# End
# 
####################################################################################################
