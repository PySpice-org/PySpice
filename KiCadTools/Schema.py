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
    "KiCadSchema",
]

####################################################################################################

"""This module implements a KiCad 6 schema file format parser and a netlist generator.

Actually, it only retrieves useful data to generate a netlist.

Since version 6, KiCad uses a file format based on `S-expression
<https://en.wikipedia.org/wiki/S-expression`_, also called symbolic expressions and abbreviated as
sexprs, is a notation for nested list (tree-structured) data, invented for and popularized by the
programming language Lisp.

Notice this code implements many tricks to handle this file format:

* The sexpdata Python module provides data at a very low level in comparison to XML and even
  JSON/YAML.
* KiCad don't store fundamental information like the netlist, thus we have to guess it using
  wire and pin coordinates.
* KiCad uses localised property names, e.g. for sheet filename

Why the hell, KiCad don't use an XML file format and don't store the netlist !

See also, https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Libraries_Files_Format

"""

####################################################################################################

import logging

# from pprint import pprint

from .Geometry import EuclidianMatrice, Position, PositionAngle, Vector
from .Sexpression import Sexpression, car, cdr, car_value

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def exchange_pair(_):
    return (_[1], _[0])

####################################################################################################

class NameMixin:

    ##############################################

    def __init__(self, name):
        self._name = name

    ##############################################

    @property
    def name(self):
        return self._name

####################################################################################################

class NumberNameMixin(NameMixin):

    ##############################################

    def __init__(self, number, name):
        self._number = number
        NameMixin.__init__(self, name)

    ##############################################

    @property
    def number(self):
        return self._number

    @property
    def name(self):
        return self._name

####################################################################################################

class Pin(NumberNameMixin, Position):

    ##############################################

    def __init__(self, number, name, x, y):
        Position.__init__(self, x, y)
        NumberNameMixin.__init__(self, number, name)

    ##############################################

    def __str__(self):
        return f"Pin f{self._number} " + super().__str__()

####################################################################################################

class PinPosition(NumberNameMixin, Position):

    ##############################################

    def __init__(self, number, name, x, y):
        Position.__init__(self, x, y)
        NumberNameMixin.__init__(self, number, name)
        self.net_id = None

    ##############################################

    def __str__(self):
        return f"Pin Position #{self._number} net #{self.net_id} " + super().__str__()

####################################################################################################

class SymbolLib(NameMixin):

    ##############################################

    def __init__(self, name):
        NameMixin.__init__(self, name)
        self._pins = []

    ##############################################

    @property
    def pins(self):
        return iter(self._pins)

    ##############################################

    def add_pin(self, number, name, x, y):
        pin = Pin(number, name, x, y)
        self._pins.append(pin)

####################################################################################################

class Symbol(PositionAngle):

    ##############################################

    def __init__(self, lib,
                 x, y, angle,
                 unit,
                 in_bom=True,
                 on_board=True,
                 reference='', value='',
                 footprint='',
                 datasheet='',
                 mirror=None,   # optional
                 ):
        super().__init__(x, y, angle)
        self._lib = lib
        self._mirror = None
        self._unit = unit
        self._in_bom = in_bom
        self._on_board = on_board
        self._reference = reference
        self._value = value
        self._footprint = footprint
        self._datasheet = datasheet
        self._pins = []

    ##############################################

    @property
    def lib(self):
        return self._lib

    @property
    def lib_name(self):
        return self._lib.name

    @property
    def mirror(self):
        return self._mirror

    @property
    def unit(self):
        return self._unit

    @property
    def in_bom(self):
        return self._in_bom

    @property
    def in_board(self):
        return self._in_board

    @property
    def reference(self):
        return self._reference

    @property
    def value(self):
        return self._value

    @property
    def footprint(self):
        return self._footprint

    @property
    def datasheet(self):
        return self._datasheet

    @property
    def pins(self):
        return iter(self._pins)

    @property
    def first_pin(self):
        return self._pins[0]

    ##############################################

    @property
    def direction(self):
        if self._angle == 0:
            return 'up'
        elif self._angle == 90:
            return 'right'
        elif self._angle == 180:
            return 'left'
        elif self._angle == 270:
            return 'down'

    ##############################################

    def _pin_position(self, pin):
        """Compute the pin position in the sheet"""
        v = Vector(pin.x, -pin.y)

        angle = self._angle
        matrice = EuclidianMatrice.rotation(self._angle)
        if self._mirror == 'x':
            matrice = EuclidianMatrice.x_mirror(matrice)
        elif self._mirror == 'y':
            matrice = EuclidianMatrice.y_mirror(matrice)

        p = v * matrice + self

        return PinPosition(pin.number, pin.name, p.x, p.y)

    ##############################################

    def guess_netlist(self, wires):
        for pin in self._lib.pins:
            pin_position = self._pin_position(pin)
            for wire in wires:
                if wire.match_pin(pin_position):
                    pin_position.net_id = wire.net_id
            if pin_position.net_id is None:
                self._logger.warning("Net not found")
            self._pins.append(pin_position)

####################################################################################################

class Wire:

    _logger = _module_logger.getChild("Wire")

    ##############################################

    def __init__(self, id, start_point, end_point):
        self._id = id
        self._start = Position(*start_point)
        self._end = Position(*end_point)
        self._connections = set()
        self._connection_types = set()
        self._net_id = None

        u = self._end - self._start
        if u.is_vertical:
            self._direction = 'V'
        elif u.is_horizontal:
            self._direction = 'H'
        else:
            self._direction = None

    ##############################################

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def direction(self):
        return self._direction

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
        if self._direction == 'V':
            direction = 'vertical'
        elif self._direction == 'H':
            direction = 'horizontal'
        return f"{self.__class__.__name__} #{self._id} from {self._start} to {self._end} {direction} net #{self.net_id}"

    ##############################################

    def match_pin(self, pin_position):
        return self._start == pin_position or self._end == pin_position

    ##############################################

    def match_junction(self, junction):
        if self.contains(junction):
            junction.connect_wire(self)

    ##############################################

    def match_extremities(self, wire):
        connection = None
        if self._start == wire.start:
            connection = ('s', 's')
        elif self._start == wire.end:
            connection = ('s', 'e')
        elif self._end == wire.start:
            connection = ('e', 's')
        elif self._end == wire.end:
            connection = ('e', 'e')
        if connection is not None:
            self.add_connection(wire, connection)
            wire.add_connection(self, exchange_pair(connection))
            return True
        return False

    ##############################################

    def contains(self, obj):
        return Vector.point_in_segment(self._start, self._end, obj)

    ##############################################

    def add_connection(self, wire, type_):
        if wire is self:
            self._logger.warning("self connection")
        else:
            self._connections.add(wire)
            self._connection_types.add((wire, type_))

    ##############################################

    # @classmethod
    # def connect(cls, wires):
    #     if len(wires) > 1:
    #         for _ in wires:
    #             _.add_connections(wires)

    ##############################################

    # def add_connections(self, wires):
    #     for _ in wires:
    #         self.add_connection(_)

####################################################################################################

class Bus(Wire):
    pass

####################################################################################################

class Junction(Position):

    ##############################################

    def __init__(self, x, y):
        super().__init__(x, y)
        self._wires = set()

    ##############################################

    @property
    def wires(self):
        return iter(self._wires)

    ##############################################

    def __str__(self):
        return "Junction at " + super().__str__()

    ##############################################

    def connect_wire(self, wire):
        self._wires.add(wire)

####################################################################################################

class NoConnect(Position):

    ##############################################

    def __str__(self):
        return "No connect at " + super().__str__()

####################################################################################################

class BusEntry(Position):

    ##############################################

    def __str__(self):
        return "Bus entry at " + super().__str__()

####################################################################################################

class Label(NameMixin, PositionAngle):

    ##############################################

    def __init__(self, name, x, y, angle):
        NameMixin.__init__(self, name)
        PositionAngle.__init__(self, x, y, angle)

    ##############################################

    def __str__(self):
        return f"Label f{self._name} " + super().__str__()

####################################################################################################

class GlobalLabel(Label):

    ##############################################

    def __str__(self):
        return f"Global label f{self._name} " + super().__str__()

####################################################################################################

class HierarchicalLabel(Label):

    ##############################################

    def __str__(self):
        return f"Hierarchical label f{self._name} " + super().__str__()

####################################################################################################

class Sheet:
    pass

####################################################################################################

class NetId:

    UUID = 0
    NETS = []
    MAP = {}

    ##############################################

    @classmethod
    def assign_ids(cls):
        _id = 1
        for net_id in cls.NETS:
            if net_id._id is None:
                net_id._id = _id
                cls.MAP[_id] = net_id._uuid
                _id += 1

    ##############################################

    def __init__(self):
        NetId.UUID += 1   # Fixme: Atomic
        self._uuid = NetId.UUID
        self._id = None
        NetId.NETS.append(self)

    ##############################################

    @property
    def uuid(self):
        return self._uuid

    ##############################################

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value not in NetId.MAP:
            self._id = value
            NetId.MAP[value] = self._uuid
        else:
            raise NameError("Id is already assigned")

    ##############################################

    def __str__(self):
        if self._id is None:
            return f"UUID #{self._uuid}"
        else:
            return f"#{self._id}"

####################################################################################################

class KiCadSchema(Sexpression):

    ##############################################

    def __init__(self, path):

        self._symbol_libs = {}
        self._junctions = []
        self._no_connections = []
        self._bus_entries = []
        self._wires = []
        self._buses = []
        self._labels = []
        self._global_labels = []
        self._hierarchical_labels = []
        self._symbols = []
        self._sheets = []

        self._read(path)
        self._guess_netlist()

    ##############################################

    @property
    def symbol_libs(self):
        return iter(self._symbol_libs)

    @property
    def symbols(self):
        return iter(self._symbol_libs)

    @property
    def wires(self):
        return iter(self._wires)

    @property
    def junctions(self):
        return iter(self._junctions)

    @property
    def labels(self):
        return iter(self._labels)

    ##############################################

    def _read(self, path):

        s_data = self.load(path)

        if car_value(s_data) != 'kicad_sch':
            raise ValueError()

        for sexpr in cdr(s_data):
            _car_value = car_value(sexpr)

            if _car_value == 'version':
                # ('version', 20210406)
                self._version = cdr(sexpr)

            elif _car_value == 'generator':
                # ('generator', 'eeschema')
                self._generator = cdr(sexpr)

            elif _car_value == 'uuid':
                # ('uuid', 'ca1ca076-e632-4fcc-8412-0a7bfcb4ba0b')
                self._uuid = cdr(sexpr)

            elif _car_value == 'paper':
                # ('paper', 'A4')
                self._paper = cdr(sexpr)

            elif _car_value == 'lib_symbols':
                for s_symbol in cdr(sexpr):
                    self._on_lib_symbol(s_symbol)

            elif _car_value == 'junction':
                # ('junction', ('at', 111.76, 73.66), ('diameter', 1.016), ('color', 0, 0, 0, 0))
                _, d = self.to_dict(sexpr)
                junction = Junction(*d['at'])
                self._junctions.append(junction)

            elif _car_value == 'no_connect':
                # (no_connect (at 177.8 50.8) (uuid b47f754e-304e-4f98-968e-20e5e5d18e29))
                _, d = self.to_dict(sexpr)
                no_connection = NoConnection(*d['at'])
                self._no_connections.append(no_connection)

            elif _car_value == 'bus_entry':
                # (bus_entry (at 190.5 80.01) (size 2.54 2.54)
                #   (stroke (width 0.1524) (type solid) (color 0 0 0 0))
                #   (uuid 55cddc77-72fd-4412-84fa-867166598c36)
                # )
                _, d = self.to_dict(sexpr)
                bus_entry = BusEntry(*d['at'])
                self._bus_entries.append(bus_entry)

            elif _car_value == 'wire':
                # 'wire',
                #     ('pts', ('xy', 140.97, 73.66), ('xy', 144.78, 73.66)),
                #     ('stroke', ('width', 0), ('type', 'solid'), ('color', 0, 0, 0, 0)),
                #     ('uuid', '53b6c7f9-e319-4bc4-82b5-f7c696f8e2db')
                _, d = self.to_dict(sexpr)
                self.fix_key_as_list(d['pts'], 'xy', 'xys')
                start_point, end_point = d['pts']['xys']
                wire = Wire(len(self._wires), start_point, end_point)
                self._wires.append(wire)

            elif _car_value == 'bus':
                # (bus (pts (xy 101.6 81.28) (xy 127 81.28))
                #    (stroke (width 0) (type solid) (color 0 0 0 0))
                #    (uuid 1029c8b7-917c-4b83-8b82-040bab29659a)
                #  )
                _, d = self.to_dict(sexpr)
                self.fix_key_as_list(d['pts'], 'xy', 'xys')
                start_point, end_point = d['pts']['xys']
                bus = Bus(len(self._buss), start_point, end_point)
                self._buses.append(bus)

            elif _car_value == 'label':
                # (label "out" (at 134.62 86.36 180)
                #   (effects (font (size 1.27 1.27)) (justify right bottom))
                #   (uuid d18a8a30-fded-4d73-acd2-a0615b9eda55)
                # )
                _, d = self.to_dict(sexpr)
                label = Label(_, *d['at'])
                self._labels.append(label)

            elif _car_value == 'global_label':
                # (global_label "Ground" (shape input) (at 114.3 114.3 180) (fields_autoplaced)
                #   (effects (font (size 1.27 1.27)) (justify right))
                #   (uuid 2d598105-6602-42a5-9940-1d3919aba7e9)
                #   (property "Intersheet References" "${INTERSHEET_REFS}" (id 0) (at 105.2345 114.2206 0)
                #     (effects (font (size 1.27 1.27)) (justify right) hide)
                #   )
                # )
                _, d = self.to_dict(sexpr)
                global_label = GlobalLabel(_, *d['at'])
                self._global_labels.append(global_label)

            elif _car_value == 'hierarchical_label':
                # (hierarchical_label "W3" (shape input) (at 228.6 50.8 0)
                #   (effects (font (size 1.27 1.27)) (justify left))
                #   (uuid 2f06b05a-b838-4b5e-be45-45567e9ea945)
                # )
                _, d = self.to_dict(sexpr)
                hierarchical_label = HierarchicalLabel(_, *d['at'])
                self._hierarchical_labels.append(hierarchical_label)

            elif _car_value == 'symbol':
                self._on_symbol(sexpr)

            elif _car_value == 'sheet':
                # (sheet (at 76.2 76.2) (size 25.4 25.4) (fields_autoplaced)
                #   (stroke (width 0.0006) (type solid) (color 0 0 0 0))
                #   (fill (color 0 0 0 0.0000))
                #   (uuid c25a1926-29f6-4d91-8c26-f75c9c7dff11)
                #   (property "Nom feuille" "Sheet1" (id 0) (at 76.2 75.5643 0)
                #     (effects (font (size 1.27 1.27)) (justify left bottom))
                #   )
                #   (property "Fichier de feuille" "sheet1.kicad_sch" (id 1) (at 76.2 102.1087 0)
                #     (effects (font (size 1.27 1.27)) (justify left top))
                #   )
                #   (pin "W1" input (at 101.6 81.28 0)
                #     (effects (font (size 1.27 1.27)) (justify right))
                #     (uuid b0424fd4-3d1f-4f3b-be2f-1ff8781c6ef2)
                #   )
                # )
                pass

            elif _car_value == 'sheet_instances':
                # (sheet_instances
                #   (path "/" (page "1"))
                #   (path "/c25a1926-29f6-4d91-8c26-f75c9c7dff11" (page "2"))
                #   (path "/ee43db97-511c-42d6-92c0-c5fecfe9c5f6" (page "3"))
                # )
                pass

            elif _car_value == 'symbol_instances':
                # (symbol_instances
                #   (path "/52705c8a-fed0-4f7d-8870-412cce75c251"
                #     (reference "#PWR0101") (unit 1) (value "GND") (footprint "")
                #   )
                #   (path "/c25a1926-29f6-4d91-8c26-f75c9c7dff11/0e0e3bc6-dd31-4ee9-83c4-2b06632480b0"
                #     (reference "R1") (unit 1) (value "R") (footprint "")
                #   )
                #   (path "/ee43db97-511c-42d6-92c0-c5fecfe9c5f6/219580f3-4290-4b55-9258-083dd190dd5a"
                #     (reference "R2") (unit 1) (value "R") (footprint "")
                #   )
                # )
                pass

    ##############################################

    def _on_lib_symbol(self, sexpr):
        # 'symbol',
        #     'spice-ngspice:C',
        #     ('pin_names', ('offset', 0.254)),
        #     ('in_bom', 'yes'),
        #     ('on_board', 'yes'),
        #     ('property', 'Reference', 'C',
        #         ('id', 0), ('at', 0, 1.016, 0),
        #         ('effects', ('font', ('size', 1.27, 1.27)),
        #         ('justify', 'left', 'bottom'))),
        #     ('property', 'Value', 'C',
        #         ('id', 1), ('at', 0, -1.27, 0),
        #         ('effects', ('font', ('size', 1.27, 1.27)),
        #         ('justify', 'left', 'top'))),
        #     ('property', 'Footprint', '',
        #         ('id', 2), ('at', 0, 0, 0),
        #         ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('property', 'Datasheet', '', ('id', 3), ('at', 0, 0, 0),
        #         ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('symbol', 'C_0_1',
        #         ('polyline', ('pts', ('xy', -2.54, -0.635), ('xy', 2.54, -0.635)),
        #             ('stroke', ('width', 0)), ('fill', ('type', 'none'))),
        #         ('polyline', ('pts', ('xy', -2.54, 0.635), ('xy', 2.54, 0.635)),
        #             ('stroke', ('width', 0)), ('fill', ('type', 'none')))
        #     ),
        #     ('symbol', 'C_1_1',
        #          ('pin',
        #              'passive',
        #              'line',
        #              ('at', 0, 2.54, 270),
        #              ('length', 1.905),
        #              ('name', '~', ('effects', ('font', ('size', 0.254, 0.254)) )),
        #              ('number', '1', ('effects', ('font', ('size', 0.254, 0.254))))
        #          ),
        #          ('pin',
        #              'passive',
        #              'line',
        #              ('at', 0, -2.54, 90),
        #              ('length', 1.905),
        #              ('name', '~', ('effects', ('font', ('size', 0.254, 0.254)))),
        #              ('number', '2', ('effects', ('font', ('size', 0.254, 0.254)))
        #          )
        #     )
        # )

        _, d = self.to_dict(sexpr)
        self.fix_key_as_dict(d, 'property', 'properties')
        self.fix_key_as_dict(d, 'symbol', 'symbols')
        for _ in d['symbols'].values():
            self.fix_key_as_list(_, 'polyline', 'polylines')
            self.fix_key_as_list(_, 'pin', 'pins')

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
                        at = spin['at'][:2]
                        symbol_lib.add_pin(number, name, *at)

    ##############################################

    def _on_symbol(self, sexpr):
        # 'symbol',
        #     ('lib_id', 'spice-ngspice:R'),
        #     ('at', 116.84, 78.74, 270),
        #     ('mirror', 'x'),
        #     ('unit', 1),
        #     ('in_bom', 'yes'),
        #     ('on_board', 'yes'),
        #     ('uuid', '00000000-0000-0000-0000-00006099a2a1'),
        #     ('property', 'Reference', 'Remi1', ('id', 0), ('at', 116.84, 82.55, 90)),
        #     ('property', 'Value', '165k', ('id', 1), ('at', 116.84, 85.09, 90)),
        #     ('property', 'Footprint', '', ('id', 2), ('at', 116.84, 78.74, 0),
        #                           ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('property', 'Datasheet', '', ('id', 3), ('at', 116.84, 78.74, 0),
        #                          ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('pin', '1', ('uuid', '4eb52cb1-9134-412d-b80c-94785a2cfc61')),
        #     ('pin', '2', ('uuid', '15aa4aaa-9c23-451a-b015-db0e7f3f79c5'))

        _, d = self.to_dict(sexpr)
        self.fix_key_as_dict(d, 'property', 'properties')
        self.fix_key_as_dict(d, 'pin', 'pins')

        lib_id = d['lib_id']
        lib = self._symbol_libs[lib_id]
        properties = d['properties']
        symbol = Symbol(
            lib,
            *d['at'],
            mirror=d.get('mirror', None),
            unit=d['unit'],
            in_bom=d['in_bom'],
            on_board=d['on_board'],
            reference=self.sattr(properties['Reference']),
            value=self.sattr(properties['Value']),
            footprint=self.sattr(properties['Footprint']),
            datasheet=self.sattr(properties['Datasheet']),
        )
        self._symbols.append(symbol)

    ##############################################

    def _guess_netlist(self):

        for junction in self._junctions:
            for wire in self._wires:
                wire.match_junction(junction)
        # Useless: wires are broken ???
        # for junction in self._junctions:
        #     Wire.connect(junction.wires)

        # Match wires
        for wire1 in self._wires:
            for wire2 in self._wires:
                if wire1 is not wire2:
                    wire1.match_extremities(wire2)

        # Assign a net to wire set
        for wire in self._wires:
            if wire.net_id is None:
                wire.net_id = NetId()

        # Assign a net to pin
        for symbol in self._symbols:
            symbol.guess_netlist(self._wires)
        # Find the ground and assign final id
        for symbol in self._symbols:
            if symbol.lib_name in ('spice-ngspice:0', ):
                symbol.first_pin.net_id.id = 0
        NetId.assign_ids()

  ##############################################

    def netlist(self):
        print(f"Number of nets: {NetId.UUID}")
        for symbol in self._symbols:
            print(f"{symbol.reference} {symbol.value}")
            for pin in symbol.pins:
                print(f"  p#{pin.number} {pin.name} -> net {pin.net_id}")
