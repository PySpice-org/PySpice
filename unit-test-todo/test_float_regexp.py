####################################################################################################

import re

####################################################################################################

numeric_const_pattern = r"""
(?i:(?P<NUMBER_PART>
# [-+]? # optional sign
(?:
    (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
    |
    (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
)
# followed by optional exponent part if desired
(?: e [+-]? \d+ ) ?
))
"""
number_re = re.compile(numeric_const_pattern, re.VERBOSE)

for txt in (
        '1',
        '123',
        '1.',
        '123.',
        '.1',
        '.123',
        '1e2',
        '1E2',
        '123e2',
        '123e45',
        '1e-2',
        '123e-45',
        '123e+45',
        '1.2e3',
        '1.23e4',
        '1.23e45',
        '.123e4',
        '.123e45',
):
    match = number_re.match(txt)
    print(txt, '->', match.groupdict())
    if txt != match.groupdict()['NUMBER_PART']:
        print('   ^ ERROR')

####################################################################################################

numeric_const_pattern = r"""
(?i:
    (?P<NUMBER_PART>
        # [-+]? # optional sign
        (?:
            (?: \d* \. \d+ )   # .1 .12 .123 etc 9.1 etc 98.1 etc
            |
            (?: \d+ \.? )      # 1. 12. 123. etc 1 12 123 etc
        )
        # followed by optional exponent part if desired
        (?: e [+-]? \d+ ) ?
    )
    (?P<UNIT_PART>
        (meg) | (mil) | [tgkmunpf]
    ) ?
    (?P<EXTRA_UNIT>
        [a-z]*
    )
)
"""
number_re = re.compile(numeric_const_pattern, re.VERBOSE)

for txt in (
        '123e-45u',
        '.123e45u',
        '123e-45uVolt',
        '.123e45Volt',
):
    match = number_re.match(txt)
    print(match.groupdict())
