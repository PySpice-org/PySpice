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

"""This module provides algorithms to compute the derivative of a function sampled on an uniform
grid.
"""

####################################################################################################

import fractions

import numpy as np

####################################################################################################

from PySpice.Math import odd

####################################################################################################

def compute_exact_finite_difference_coefficients(derivative_order, grid, x0=0):

    """This function compute the finite difference coefficients for the given derivative order and
    grid.  The parameter *x* specifies where is computed the derivative on the grid.  The grid is
    given as a list of integer offsets.

    The algorithm is derived from the article: Generation of Finite Difference Formulas on Arbitrary Space
    Grids, Bengt Fornberg, Mathematics of computation, volume 51, number 184, october 1988
    """

    N = len(grid)

    # d[m,n,v]
    d = [[[0
           for v in range(N)]
          for n in range(N)]
         for m in range(derivative_order +1)]

    d[0][0][0] = fractions.Fraction(1,1)
    c1 = 1
    for n in range(1, N):
        c2 = 1
        for v in range(n):
            c3 = grid[n] - grid[v]
            c2 *= c3
            if n <= derivative_order:
                d[n][n-1][v] = 0
            for m in range(min(n, derivative_order) +1):
                d[m][n][v] = ( (grid[n] - x0)*d[m][n-1][v] - m*d[m-1][n-1][v] ) / c3
        for m in range(min(n, derivative_order) +1):
            d[m][n][n] = fractions.Fraction(c1,c2)*( m*d[m-1][n-1][n-1] - (grid[n-1] - x0)*d[m][n-1][n-1] )
        c1 = c2

    return d[-1][-1]

####################################################################################################

def compute_finite_difference_coefficients(derivative_order, grid):
    return [float(x) for x in compute_exact_finite_difference_coefficients(derivative_order, grid)]

####################################################################################################

_coefficient_cache = dict(centred={}, forward={}, backward={})

def get_finite_difference_coefficients(derivative_order, accuracy_order, grid_type):

    if derivative_order < 1:
        raise ValueError("Wrong derivative order")

    if odd(accuracy_order) or accuracy_order < 2:
        raise ValueError("Wrong accuracy order")

    if grid_type == 'centred':
        window_size = accuracy_order // 2
        grid = list(range(-window_size, window_size +1))
    elif grid_type == 'forward':
        grid = list(range(derivative_order + accuracy_order))
    elif grid_type == 'backward':
        grid = list(range(-(derivative_order + accuracy_order) +1, 1))
        grid = list(reversed(grid)) # Fixme: why ?
    else:
        raise ValueError("Wrong grid type")

    key = '{}-{}'.format(derivative_order, accuracy_order)
    coefficients = _coefficient_cache[grid_type].get(key, None)
    if coefficients is None:
        coefficients = compute_finite_difference_coefficients(derivative_order, grid)
        _coefficient_cache[grid_type][key] = coefficients

    return grid, coefficients

####################################################################################################

def simple_derivative(x, values):
    """ Compute the derivative as a simple slope. """
    return x[:-1], np.diff(values)/np.diff(x)

####################################################################################################

def derivative(x, values, derivative_order=1, accuracy_order=4):

    """Compute the derivative at the given derivative order and accuracy order. The precision of the
    Taylor expansion is :math:`\mathcal{O}(dx^{accuracy})`.
    """

    dx = np.diff(x)
    # if not np.all(dx == dx[0]):
    #     raise ValueError("Sampling is not uniform")
    dx = dx[0]

    values_size, = values.shape

    derivative = np.zeros(values_size, dtype=values.dtype)

    grid, coefficients = get_finite_difference_coefficients(derivative_order, accuracy_order, 'centred')
    window_size = grid[-1]
    # print grid, coefficients
    vector_size = values_size - 2*window_size
    if not vector_size:
        raise ValueError("The size of the value's array is not sufficient for the given accuracy order")
    lower_index = window_size
    upper_index = values_size - window_size
    derivative_view = derivative[window_size:-window_size]
    for offset, coefficient in zip(grid, coefficients):
        if coefficient:
            # print offset, lower_index + offset, upper_index + offset
            derivative_view += values[lower_index + offset:upper_index + offset] * coefficient

    grid, coefficients = get_finite_difference_coefficients(derivative_order, accuracy_order, 'forward')
    # print grid, coefficients
    grid_size = len(grid)
    upper_index = window_size
    derivative_view = derivative[:window_size]
    for offset, coefficient in zip(grid, coefficients):
        # print offset, offset, window_size+offset
        derivative_view += values[offset:upper_index + offset] * coefficient

    grid, coefficients = get_finite_difference_coefficients(derivative_order, accuracy_order, 'backward')
    # print grid, coefficients
    grid_size = len(grid)
    lower_index = values_size - window_size
    upper_index = values_size
    derivative_view = derivative[-window_size:]
    for offset, coefficient in zip(grid, coefficients):
        # print offset, lower_index + offset, upper_index + offset
        derivative_view += values[lower_index + offset:upper_index + offset] * coefficient

    return derivative / dx**derivative_order
