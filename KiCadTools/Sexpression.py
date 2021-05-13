####################################################################################################
#
# KiCadTools - Python Tools for KiCad
# Copyright (C) 2021 Fabrice Salvaire
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

__all__ = [
    'Sexpression',
    'car',
    'car_value',
    'cdr',
]

####################################################################################################

# Ideas to make an OO API
#
# provide a list of keys to be mapped in a dict/list, e.g. property -> properties
#
# [Symbol() ...] -> to Sexpr object
# A Sexpr object has childs

####################################################################################################

import sexpdata
from sexpdata import car, cdr

####################################################################################################

def car_value(_):
    return car(_).value()

####################################################################################################

class Sexpression:

    ##############################################

    @classmethod
    def to_dict(cls, sexpr):
        """Convert a S-expression to JSON"""
        if isinstance(car(sexpr), sexpdata.Symbol):
            d = {'_': []}
            for item in cdr(sexpr):
                if isinstance(item, sexpdata.Symbol):
                    d['_'].append(item.value())
                elif isinstance(item, list):
                    key, value = cls.to_dict(item)
                    # some keys can appear more than one time...
                    while key in d:
                        key += '*'
                    d[key] = value
                if isinstance(item, (int, float, str)):
                    d['_'].append(item)
            if d['_']:
                if len(d.keys()) == 1:
                    d = d['_']
                    if len(d) == 1:
                        d = d[0]
            else:
                # Fixme: could use d.get('_', []) ???
                del d['_']
            return car(sexpr).value(), d
        else:
            return sexpr

    ##############################################

    @classmethod
    def fix_key_as_dict(cls, adict, key, new_key):
        """Fix key*... as a dict"""
        new_dict = {}
        while key in adict:
            d = adict[key]
            del adict[key]
            key2 = d['_'][0]
            d['_'] = d['_'][1:]
            new_dict[key2] = d
            key += '*'
        if new_dict:
            adict[new_key] = new_dict

    ##############################################

    @classmethod
    def fix_key_as_list(cls, adict, key, new_key):
        """Fix key*... as a list"""
        new_list = []
        while key in adict:
            d = adict[key]
            del adict[key]
            new_list.append(d)
            key += '*'
        if new_list:
            adict[new_key] = new_list

    ##############################################

    @classmethod
    def sattr(cls, d):
        return d['_'][0]

    # Fixme:
    #  XPath method
    #  extended dict [key1/key2/...]

    ##############################################

    @classmethod
    def load(cls, path):
        with open(path) as fh:
            _ = sexpdata.load(fh)
        return _
