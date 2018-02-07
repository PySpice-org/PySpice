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

####################################################################################################

import unittest

import numpy as np

from scipy.special import gamma
from scipy.linalg import solve

####################################################################################################

from PySpice.Math import odd
from PySpice.Math.Calculus import compute_exact_finite_difference_coefficients, derivative

####################################################################################################

# From Generation of Finite Difference Formulas on Arbitrary Space Grids
#   Bengt Fornberg, Mathematics of computation, volume 51, number 184, october 1988

centred_coefficients = {
    # on a grid -4,...,4
    # [order of derivative][order of accuracy] = (left coefficients, ...)
    0: { None: [1,] },
    1: {
        2: [-1/2.,   0],
        4: [1/12.,   -2/3.,   0],
        6: [-1/60.,   3/20.,   -3/4.,   0],
        8: [1/280.,   -4/105.,   1/5.,   -4/5.,   0],
   },
    2: {
        2: [1,  -2],
        4: [-1/12.,  4/3.,  -5/2.],
        6: [1/90.,  -3/20.,  3/2.,  -49/18.],
        8: [-1/560.,  8/315.,  -1/5.,  8/5.,  -205/72.],
   },
}
# complete right coefficients
for derivative_order, derivative_order_dict in centred_coefficients.items():
    for coefficients in derivative_order_dict.values():
        if len(coefficients) > 1:
            for i in range(len(coefficients) -2, -1, -1):
                coefficient = coefficients[i]
                if odd(derivative_order):
                    coefficient *= -1
                coefficients.append(coefficient)

forward_coefficients = {
    # on a grid 0...8
    # [order of derivative][order of accuracy] = (coefficients)
    0: { None:(1,) },
    1: {
        1: (-1,  1),
        2: (-3/2.,  2,  -1/2.),
        3: (-11/6.,  3,  -3/2.,  1/3.),
        4: (-25/12.,  4,  -3,  4/3.,  -1/4.),
        5: (-137/60.,  5,  -5,  10/3.,  -5/4.,  1/5.),
        6: (-49/20.,  6,  -15/2.,  20/3.,  -15/4.,  6/5.,  -1/6.),
        7: (-363/140.,  7,  -21/2.,  35/3.,  -35/4.,  21/5.,  -7/6.,  1/7.),
        8: (-761/280.,  8,  -14,  56/3.,  -35/2.,  56/5.,  -14/3.,  8/7.,  -1/8.),
   },
    2: {
        1: (1,  -2,  1),
        2: (2,  -5,  4,  -1),
        3: (35/12.,  -26/3.,  19/2.,  -14/3.,  11/12.),
        4: (15/4.,  -77/6.,  107/6.,  -13,  61/12.,  -5/6.),
        5: (203/45.,  -87/5.,  117/4.,  -254/9.,  33/2.,  -27/5.,  137/180.),
        6: (469/90.,  -223/10.,  879/20.,  -949/18.,  41,  -201/10.,  1019/180.,  -7/10.),
        7: (29531/5040.,  -962/35.,  621/10.,  -4006/45.,   691/8.,  -282/5.,  2143/90.,  -206/35.,  363/560.),
   },
}

####################################################################################################

def compute_finite_difference_coefficients(derivative_order, grid_size):

    # from http://www.scientificpython.net/pyblog/uniform-finite-differences-all-orders

    n = 2*grid_size -1
    A = np.tile(np.arange(grid_size), (n,1)).T
    B = np.tile(np.arange(1-grid_size,grid_size), (grid_size,1))
    M = (B**A)/gamma(A+1)

    r = np.zeros(grid_size)
    r[derivative_order] = 1

    D = np.zeros((grid_size, grid_size))
    for k in range(grid_size):
        indexes = k + np.arange(grid_size)
        D[:,k] = solve(M[:,indexes], r)

    return D

####################################################################################################

class TestFiniteDifference(unittest.TestCase):

    ##############################################

    def test_coefficient(self):

        for derivative_order, derivative_order_dict in centred_coefficients.items():
            for accuracy_order, coefficients in derivative_order_dict.items():
                if accuracy_order is not None and accuracy_order > 1:
                    coefficients = np.array(coefficients)
                    grid_size = accuracy_order +1
                    # D = compute_finite_difference_coefficients(derivative_order, grid_size)
                    # computed_coefficients = D[:,grid_size/2]
                    grid = list(range(-accuracy_order//2,accuracy_order//2+1))
                    computed_coefficients = compute_exact_finite_difference_coefficients(derivative_order, grid)
                    computed_coefficients = [float(x) for x in computed_coefficients]
                    # print "Derivative order {} Accuracy order {}".format(derivative_order, accuracy_order)
                    # print coefficients
                    # print computed_coefficients
                    # print np.abs(coefficients - computed_coefficients)
                    self.assertTrue(np.all(np.isclose(coefficients, computed_coefficients)))

        for derivative_order, derivative_order_dict in forward_coefficients.items():
            for accuracy_order, coefficients in derivative_order_dict.items():
                if accuracy_order is not None and accuracy_order > 1:
                    coefficients = np.array(coefficients)
                    grid_size = derivative_order + accuracy_order
                    # D = compute_finite_difference_coefficients(derivative_order, grid_size)
                    # computed_coefficients = D[:,-1]
                    grid = list(range(grid_size))
                    computed_coefficients = compute_exact_finite_difference_coefficients(derivative_order, grid)
                    computed_coefficients = [float(x) for x in computed_coefficients]
                    # print "Derivative order {} Accuracy order {}".format(derivative_order, accuracy_order)
                    # print D
                    # print coefficients
                    # print computed_coefficients
                    # print np.abs(coefficients - computed_coefficients)
                    self.assertTrue(np.all(np.isclose(coefficients, computed_coefficients)))

    ##############################################

    def test_derivative(self):

        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x)
        true_dy1 = np.cos(x) # d sin = cos
        true_dy2 = -y # d cos = - sin

        dy1 = derivative(x, y, derivative_order=1, accuracy_order=4)
        dy2 = derivative(x, y, derivative_order=2, accuracy_order=4)

        # import matplotlib.pyplot as plt
        # plt.plot(x[:-1], np.diff(y)/np.diff(x) - true_dy1[:-1])
        # plt.plot(x, dy1 - true_dy1)
        # plt.plot(x, dy2 - true_dy2)
        # plt.show()
        np.testing.assert_array_almost_equal(dy1, true_dy1, decimal=1)
        np.testing.assert_array_almost_equal(dy2, true_dy2, decimal=1)

####################################################################################################

if __name__ == '__main__':

    unittest.main()
