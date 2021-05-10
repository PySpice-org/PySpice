####################################################################################################
#
# Fix custom dunders
#
# grep -R __ PySpice | grep '__ =' | sed -e 's/.*: *//' | sed -e 's/ =.*//' | sort | uniq
#
####################################################################################################

# pytest unit-test OK

# class VoltageDivider(SubCircuitFactory):
#     __name__ = 'VoltageDivider'
#     _nodes = ('input', 'output_plus', 'output_minus')

#   File "PySpice/Spice/Netlist.py", line 1156, in __init__
#     super().__init__(self.__name__, *self._nodes, **kwargs)
# TypeError: __init__() argument after * must be an iterable, not NoneType


####################################################################################################

from pathlib import Path
import os

####################################################################################################

special = (
)

internals = (
    '__binary_operator_map__',
    '__classes__',
    '__declaration_order__',
    '__hash_map__',
    '__name_to_unit__',
    '__nodes__',
    '__operators__',
    '__optional_parameters__',
    '__parameters_from_args__',
    '__positional_parameters__',
    '__prefixed_unit_map__',
    '__prefixes__',
    '__spice_to_parameters__',
    '__unary_operator_map__',
    '__unit_map__',
    '__units__',
    '__value_ctor__',
    '__values_ctor__',
    '__variable_cls__',
)

constants = (
    '__MAX_COMMAND_LENGTH__',
    '__VALID_KWARGS__',
    '__alias__',
    '__analysis_name__',
    '__as_unit__',
    '__base_units__',
    '__default_unit__',
    '__git_tag__',
    '__is_si__',
    '__long_alias__',
    '__number_of_operands__',
    '__operator__',
    '__pins__',
    '__power__',
    '__precedence__',
    '__prefix__',
    '__quantity__',
    '__scale__', # unused ?
    '__si_unit__',
    '__spice_prefix__',
    '__spice_suffix__', # unused ?
    '__unit_name__',
    '__unit_suffix__',
)

####################################################################################################

def fix_file(path):
    print(path)

    with open(path, 'r') as fh:
        content = fh.read()

    for dunder in internals:
        fixed_name = dunder.replace('__', '_')
        fixed_name = fixed_name[:-1]
        content = content.replace(dunder, fixed_name)
    for dunder in constants:
        fixed_name = dunder.upper().replace('__', '')
        content = content.replace(dunder, fixed_name)

    os.rename(path, str(path) + '~~~')
    with open(path, 'w') as fh:
        fh.write(content)

####################################################################################################

for root_directory in (
        'PySpice',
        'unit-test',
):
    for root, directories, filenames in os.walk(root_directory):
        for filename in filenames:
            path = Path(root, filename)
            if path.suffix == '.py':
                fix_file(path)
