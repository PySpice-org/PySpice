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
    'EuclidianMatrice',
    'Position',
    'PositionAngle',
    'Vector',
]

####################################################################################################

import math

####################################################################################################

EPSILON = 1e-4   # numerical tolerance to match coordinate

####################################################################################################

class EuclidianMatrice:

    ##############################################

    @classmethod
    def identity(cls):
        return [[1, 0],
                [0, 1]]

    ##############################################

    @classmethod
    def rotation(cls, angle):
        if angle == 0:
            return cls.identity()
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

    @property
    def is_vertical(self):
        return math.fabs(self._x) < EPSILON

    @property
    def is_horizontal(self):
        return math.fabs(self._y) < EPSILON

    ##############################################

    def scalar_product(self, other):
        return self._x * other.x + self._y * other.y

    ##############################################

    def vectorial_product(self, other):
        return self._x * other.y - self._y * other.x

    ##############################################

    def length(self):
        return math.sqrt(self.scalar_product(self))

    ##############################################

    @classmethod
    def point_in_segment(cls, start, end, point):
        # UxV = |U| |V| sin(theta) = 0 if colinear
        # U.V = |U| |V| cos(theta) = |U| |V|= U.U |V|/|U|
        # Fixme: could cache
        U = end - start
        V = point - start
        return (math.fabs(U.vectorial_product(V)) < EPSILON
                and
                0 <= U.scalar_product(V) <= U.scalar_product(U))

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
