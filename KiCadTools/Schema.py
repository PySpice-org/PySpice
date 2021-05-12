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

__all__ = ["KicadSchema"]

####################################################################################################

"""This module implements a KiCad 6 schema file format parser and a netlist generator.

Actually, it only retrieves useful data to generate a netlist.

Since version 6, KiCad uses a file format based on `S-expression
<https://en.wikipedia.org/wiki/S-expression`_, also called symbolic expressions and abbreviated as
sexprs, is a notation for nested list (tree-structured) data, invented for and popularized by the
programming language Lisp.

Notice this code implements many tricks to handle this (WTHF) file format:

* The sexpdata Python module provides data at a very low level in comparison to XML and even
  JSON/YAML.
* KiCad don't store fundamental information like the netlist, thus we have to guess it using
  wire and pin coordinates.

Why the hell, KiCad don't use an XML file format and don't store the netlist !

Disclaimer: This code is not nuclear power plant, aeronautical and spatial proof...

See also, https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Libraries_Files_Format

"""

####################################################################################################

import math

from pprint import pprint

import sexpdata
from sexpdata import car, cdr

####################################################################################################

EPSILON = 1e-4   # numerical tolerance to match coordinate...

####################################################################################################

class Position:

    ##############################################

    def __init__(self, x, y):
        self._x = x
        self._y = y

    ##############################################

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    ##############################################

    def __str__(self):
        return f"xy=({self._x:.2f}, {self._y:.2f})"

    ##############################################

    def __eq__(self, other):
        return (math.fabs(self._x - other.x) < EPSILON and
                math.fabs(self._y - other.y) < EPSILON)

    ##############################################

    def __add__(self, other):
        return Vector(self._x + other.x, self._y + other.y)

    ##############################################

    def __sub__(self, other):
        return Vector(self._x - other.x, self._y - other.y)

    ##############################################

    def __mul__(self, matrice):
        x = matrice[0][0] * self._x + matrice[0][1] * self._y
        y = matrice[1][0] * self._x + matrice[1][1] * self._y
        return Vector(x, y)

####################################################################################################

class Vector(Position):

    ##############################################

    def scalar_product(self, other):
        return self._x * other.x +  self._y * other.y

    ##############################################

    def vectorial_product(self, other):
        return self._x * other.y - self._y * other.x

    ##############################################

    def length(self):
        return math.sqrt(self.scalar_product(self))

    ##############################################

    def normalize(self):
        l = self.length()
        return self.__class__(self._x/l, self._y/l)

    ##############################################

    @classmethod
    def identity(cls):
        return [[1, 0],
                [0, 1]]

    ##############################################

    @classmethod
    def rotation(cls, angle):
        if angle == 0:
            return [[1, 0],
                    [0, 1]]
        elif angle == 90:
            return [[ 0, 1],
                    [-1, 0]]
        elif angle == 180:
            # mirror x and y
            return [[-1, 0],
                    [ 0, -1]]
        elif angle == 270:
            # 90 and mirror y
            return [[ 0, 1],
                    [-1, 0]]

    ##############################################

    @classmethod
    def x_mirror(cls, matrice):
        return [[-matrice[0][0], -matrice[0][1]],
                [ matrice[1][0],  matrice[1][1]]]

    @classmethod
    def y_mirror(cls, matrice):
        return [[ matrice[0][0],  matrice[0][1]],
                [-matrice[1][0], -matrice[1][1]]]

####################################################################################################

class PositionAngle(Position):

    ##############################################

    def __init__(self, x, y, angle):
        super().__init__(x, y)
        self._angle = angle

    ##############################################

    @property
    def angle(self):
        return self._angle

    ##############################################

    def __str__(self):
        return super().__str__() + f" @{self._angle}"

####################################################################################################

class Pin(PositionAngle):

    ##############################################

    def __init__(self, number, name, x, y, angle):
        super().__init__(x, y, angle)
        self._number = number
        self._name = name

    ##############################################

    @property
    def number(self):
        return self._number

    @property
    def name(self):
        return self._name

    ##############################################

    def __str__(self):
        return f"Pin f{self._number} " + super().__str__()

####################################################################################################

class PinPosition(Position):

    ##############################################

    def __init__(self, number, name, x, y):
        super().__init__(x, y)
        self._number = number   # Fixme: mixin
        self._name = name
        self.net_id = None

    ##############################################

    @property
    def number(self):
        return self._number

    @property
    def name(self):
        return self._name

    ##############################################

    def __str__(self):
        return f"Pin Position #{self._number} net #{self.net_id} " + super().__str__()

####################################################################################################

class SymbolLib:

    ##############################################

    def __init__(self, name):
        self._name = name
        self._pins = []

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def pins(self):
        return iter(self._pins)

    ##############################################

    def add_pin(self, number, name, x, y, angle):
        pin = Pin(number, name, x, y, angle)
        self._pins.append(pin)

####################################################################################################

class Symbol(PositionAngle):

    ##############################################

    def __init__(self, lib, x, y, angle, reference, value):
        super().__init__(x, y, angle)
        self._mirror = None
        self._lib = lib
        self._reference = reference
        self._value = value
        self._pins = []

    ##############################################

    @property
    def reference(self):
        return self._reference

    @property
    def value(self):
        return self._value

    @property
    def pins(self):
        return iter(self._pins)

    ##############################################

    def mirror(self, axis):
        self._mirror = axis

    ##############################################

    def _pin_position(self, pin):

        # Fixme: pin angle ???
        # print(pin)
        v = Vector(pin.x, -pin.y)

        angle = self._angle
        matrice = Vector.rotation(self._angle)
        if self._mirror == 'x':
            matrice = Vector.x_mirror(matrice)
        if self._mirror == 'y':
            matrice = Vector.y_mirror(matrice)

        p = v * matrice + self

        return PinPosition(pin.number, pin.name, p.x, p.y)

    ##############################################

    def guess_netlist(self, wires):

        print()
        print(f"{self._reference} " + super().__str__() + f" {self._mirror}")
        for pin in self._lib.pins:
            pin_position = self._pin_position(pin)
            for wire in wires:
                if wire.match_pin(pin_position):
                    pin_position.net_id = wire.net_id
            if pin_position.net_id is None:
                print('>>>> Pin not found !!!')
            print(pin_position)
            self._pins.append(pin_position)

####################################################################################################

class Junction(Position):

    ##############################################

    def __str__(self):
        return "Junction at " + super().__str__()

####################################################################################################

class Wire:

    ##############################################

    def __init__(self, id, start_point, end_point):
        self._id = id
        self._start = Position(*start_point)
        self._end = Position(*end_point)
        self._u = self._end - self._start
        self._connections = set()
        self._net_id = None

    ##############################################

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def connections(self):
        return self._connections

    ##############################################

    @property
    def net_id(self):
        return self._net_id

    @net_id.setter
    def net_id(self, value):
        if self._net_id is None:
            self._net_id = value
            for _ in self._connections:
                _.net_id = value
        elif self._net_id != value:
            raise NameError(f"net_id overwrite to {value} was {self._net_id}")

    ##############################################

    def __str__(self):
        direction = ''
        if math.fabs(self._u.x) < EPSILON:
            direction = 'vertical'
        elif math.fabs(self._u.y) < EPSILON:
            direction = 'horizontal'
        return f"Wire #{self._id} from {self._start} to {self._end} {direction} net #{self.net_id}"

    ##############################################

    def match_pin(self, pin_position):
        return self._start == pin_position or self._end == pin_position

    ##############################################

    def match_extremities(self, wire):
        if (self._start == wire.start or
            self._start == wire.end or
            self._end == wire.start or
            self._end == wire.end
            ):
            self.connect((self, wire))
            return True
        return False

    ##############################################

    def contains(self, junction):
        U = self._u.normalize()
        V = junction - self._start
        if math.fabs(U.vectorial_product(V)) > EPSILON:
            return False
        s = U.scalar_product(V)
        # print(self, self._u.length(), s)
        return 0 <= s <= self._u.length()

    ##############################################

    @classmethod
    def connect(cls, wires):
        for _ in wires:
            _.add_connections(wires)

    ##############################################

    def add_connection(self, wire):
        if wire is not self:
            self._connections.add(wire)

    ##############################################

    def add_connections(self, wires):
        for _ in wires:
            self.add_connection(_)

####################################################################################################

class KicadSchema:

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

    def __init__(self, path):

        self._symbol_libs = {}
        self._junctions = []
        self._wires = []
        self._symbols = []

        self._read(path)
        self._guess_netlist()

    ##############################################

    def _read(self, path):

        with open(path) as fh:
            s_data = sexpdata.load(fh)

        if car(s_data).value() != 'kicad_sch':
            raise ValueError()

        for sexpr in cdr(s_data):
            # print()
            # print(sexpr)
            car_value = car(sexpr).value()

            if car_value == 'version':
                # [Symbol('version'), 20210406]
                self._version = cdr(sexpr)

            elif car_value == 'generator':
                # [Symbol('generator'), Symbol('eeschema')]
                pass

            elif car_value == 'uuid':
                # [Symbol('uuid'), Symbol('ca1ca076-e632-4fcc-8412-0a7bfcb4ba0b')]
                pass

            elif car_value == 'paper':
                # [Symbol('paper'), 'A4']
                pass

            elif car_value == 'lib_symbols':
                for s_symbol in cdr(sexpr):
                    # Symbol('symbol'),
                    #     'spice-ngspice:C',
                    #     [Symbol('pin_names'), [Symbol('offset'), 0.254]],
                    #     [Symbol('in_bom'), Symbol('yes')],
                    #     [Symbol('on_board'), Symbol('yes')],
                    #     [Symbol('property'), 'Reference', 'C',
                    #         [Symbol('id'), 0], [Symbol('at'), 0, 1.016, 0],
                    #         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]],
                    #         [Symbol('justify'), Symbol('left'), Symbol('bottom')]]],
                    #     [Symbol('property'), 'Value', 'C',
                    #         [Symbol('id'), 1], [Symbol('at'), 0, -1.27, 0],
                    #         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]],
                    #         [Symbol('justify'), Symbol('left'), Symbol('top')]]],
                    #     [Symbol('property'), 'Footprint', '',
                    #         [Symbol('id'), 2], [Symbol('at'), 0, 0, 0],
                    #         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.524, 1.524]]]],
                    #     [Symbol('property'), 'Datasheet', '', [Symbol('id'), 3], [Symbol('at'), 0, 0, 0],
                    #         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.524, 1.524]]]],
                    #     [Symbol('symbol'), 'C_0_1',
                    #         [Symbol('polyline'), [Symbol('pts'), [Symbol('xy'), -2.54, -0.635], [Symbol('xy'), 2.54, -0.635]],
                    #             [Symbol('stroke'), [Symbol('width'), 0]], [Symbol('fill'), [Symbol('type'), Symbol('none')]]],
                    #         [Symbol('polyline'), [Symbol('pts'), [Symbol('xy'), -2.54, 0.635], [Symbol('xy'), 2.54, 0.635]],
                    #             [Symbol('stroke'), [Symbol('width'), 0]], [Symbol('fill'), [Symbol('type'), Symbol('none')]]]
                    #     ],
                    #     [Symbol('symbol'), 'C_1_1',
                    #          [Symbol('pin'),
                    #              Symbol('passive'),
                    #              Symbol('line'),
                    #              [Symbol('at'), 0, 2.54, 270],
                    #              [Symbol('length'), 1.905],
                    #              [Symbol('name'), '~', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 0.254, 0.254]] ]],
                    #              [Symbol('number'), '1', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 0.254, 0.254]]]]
                    #          ],
                    #          [Symbol('pin'),
                    #              Symbol('passive'),
                    #              Symbol('line'),
                    #              [Symbol('at'), 0, -2.54, 90],
                    #              [Symbol('length'), 1.905],
                    #              [Symbol('name'), '~', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 0.254, 0.254]]]],
                    #              [Symbol('number'), '2', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 0.254, 0.254]]]
                    #          ]
                    #     ]
                    # ]
                    # print('>'*100)
                    _, d = self.to_dict(s_symbol)
                    # print(pprint(d))
                    self.fix_key_as_dict(d, 'property', 'properties')
                    self.fix_key_as_dict(d, 'symbol', 'symbols')
                    for _ in d['symbols'].values():
                        self.fix_key_as_list(_, 'polyline', 'polylines')
                        self.fix_key_as_list(_, 'pin', 'pins')
                    # pprint(d)
                    name = self.sattr(d)
                    symbol_lib = SymbolLib(name)
                    self._symbol_libs[name] = symbol_lib
                    # kind of XPath to get pins...
                    for d1 in d['symbols'].values():
                        for key, d2 in d1.items():
                            if key == 'pins':
                                for spin in d2:
                                    number = self.sattr(spin['number'])
                                    name = self.sattr(spin['name'])
                                    symbol_lib.add_pin(number, name, *spin['at'])

            elif car_value == 'junction':
                # [Symbol('junction'), [Symbol('at'), 111.76, 73.66], [Symbol('diameter'), 1.016], [Symbol('color'), 0, 0, 0, 0]]
                _, d = self.to_dict(sexpr)
                junction = Junction(*d['at'])
                self._junctions.append(junction)

            elif car_value == 'wire':
                # Symbol('wire'),
                #     [Symbol('pts'), [Symbol('xy'), 140.97, 73.66], [Symbol('xy'), 144.78, 73.66]],
                #     [Symbol('stroke'), [Symbol('width'), 0], [Symbol('type'), Symbol('solid')], [Symbol('color'), 0, 0, 0, 0]],
                #     [Symbol('uuid'), Symbol('53b6c7f9-e319-4bc4-82b5-f7c696f8e2db')]
                _, d = self.to_dict(sexpr)
                self.fix_key_as_list(d['pts'], 'xy', 'xys')
                start_point, end_point = d['pts']['xys']
                wire = Wire(len(self._wires), start_point, end_point)
                self._wires.append(wire)

            elif car_value == 'symbol':
                # Symbol('symbol'),
                #     [Symbol('lib_id'), 'spice-ngspice:R'],
                #     [Symbol('at'), 116.84, 78.74, 270],
                #     [Symbol('mirror'), Symbol('x')],
                #     [Symbol('unit'), 1],
                #     [Symbol('in_bom'), Symbol('yes')],
                #     [Symbol('on_board'), Symbol('yes')],
                #     [Symbol('uuid'), Symbol('00000000-0000-0000-0000-00006099a2a1')],
                #     [Symbol('property'), 'Reference', 'Remi1', [Symbol('id'), 0], [Symbol('at'), 116.84, 82.55, 90]],
                #     [Symbol('property'), 'Value', '165k', [Symbol('id'), 1], [Symbol('at'), 116.84, 85.09, 90]],
                #     [Symbol('property'), 'Footprint', '', [Symbol('id'), 2], [Symbol('at'), 116.84, 78.74, 0],
                #                           [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.524, 1.524]]]],
                #     [Symbol('property'), 'Datasheet', '', [Symbol('id'), 3], [Symbol('at'), 116.84, 78.74, 0],
                #                          [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.524, 1.524]]]],
                #     [Symbol('pin'), '1', [Symbol('uuid'), Symbol('4eb52cb1-9134-412d-b80c-94785a2cfc61')]],
                #     [Symbol('pin'), '2', [Symbol('uuid'), Symbol('15aa4aaa-9c23-451a-b015-db0e7f3f79c5')]]
                # print('>'*100)
                _, d = self.to_dict(sexpr)
                # Fixme: mirror x and y ???
                self.fix_key_as_dict(d, 'property', 'properties')
                self.fix_key_as_dict(d, 'pin', 'pins')
                # pprint(d)
                lib_id = d['lib_id']
                lib = self._symbol_libs[lib_id]
                reference = self.sattr(d['properties']['Reference'])
                value = self.sattr(d['properties']['Value'])
                symbol = Symbol(lib, *d['at'], reference, value)
                if 'mirror' in d:
                    symbol.mirror(d['mirror'])
                self._symbols.append(symbol)

            elif car_value == 'sheet_instances':
                pass

            elif car_value == 'symbol_instances':
                pass

    ##############################################

    def _guess_netlist(self):

        for junction in self._junctions:
            print(junction)
            for wire in self._wires:
                s = set()
                if wire.contains(junction):
                    # print(f"  in {wire}")
                    s.add(wire)
                if len(s) > 1:
                    Wire.connect(s)

        for wire1 in self._wires:
            for wire2 in self._wires:
                if wire1 is not wire2:
                    if wire1.match_extremities(wire2):
                        pass
                    # print(f"{wire1} match {wire2}")

        net_id = 0
        for wire in self._wires:
            if wire.net_id is None:
                net_id += 1
                wire.net_id = net_id
            print(wire)
            for _ in wire.connections:
                print(f"  {_}")
        print(f"Number of nets: {net_id}")

        for symbol in self._symbols:
            symbol.guess_netlist(self._wires)

    ##############################################

    def netlist(self):
        for symbol in self._symbols:
            print(f"{symbol.reference} {symbol.value}")
            for pin in symbol.pins:
                print(f"  p#{pin.number} {pin.name} -> net #{pin.net_id}")
