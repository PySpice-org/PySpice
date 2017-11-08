export PySpice_source_path=${PWD}
export PySpice_examples_path=${PySpice_source_path}/examples

source /opt/python-virtual-env/py36/bin/activate
append_to_python_path_if_not ${PySpice_source_path}
append_to_python_path_if_not ${PySpice_source_path}/tools

append_to_path_if_not /usr/local/stow/ngspice-26/bin
append_to_ld_library_path_if_not /usr/local/stow/ngspice-26/lib/

# OSError: cannot load library libngspice.so: /usr/local/stow/ngspice-27/lib/libngspice.so: undefined symbol: MIFiSize.  Additionally, ctypes.util.find_library() did not manage to locate a library called 'libngspice.so'

# src/xspice/mif

# append_to_path_if_not /usr/local/stow/ngspice-27/bin
# append_to_ld_library_path_if_not /usr/local/stow/ngspice-27/lib/
