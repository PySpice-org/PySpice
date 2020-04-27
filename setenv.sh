export PySpice_source_path=${PWD}
export PySpice_examples_path=${PySpice_source_path}/examples

source /opt/python-virtual-env/py38/bin/activate
append_to_python_path_if_not ${PySpice_source_path}
append_to_python_path_if_not ${PySpice_source_path}/tools

NGSPICE_VERSION=30
append_to_path_if_not /usr/local/stow/ngspice-${NGSPICE_VERSION}/bin
append_to_ld_library_path_if_not /usr/local/stow/ngspice-${NGSPICE_VERSION}/lib/
