####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

import fractions

import numpy as np

from scipy.special import gamma
from scipy.linalg import solve

####################################################################################################

from PySpice.Math import odd

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
for derivative_order, derivative_order_dict in centred_coefficients.iteritems():
    for coefficients in derivative_order_dict.itervalues():
        if len(coefficients) > 1:
            for i in xrange(len(coefficients) -2, -1, -1):
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

def compute_exact_finite_difference_coefficients(derivative_order, grids, x0=0):

    N = len(grids)

    # d[m,n,v]
    d = [[[0
           for v in range(N)]
          for n in range(N)]
         for m in xrange(derivative_order +1)]

    d[0][0][0] = fractions.Fraction(1,1)
    c1 = 1
    for n in xrange(1, N):
        c2 = 1
        for v in xrange(n):
            c3 = grids[n] - grids[v]
            c2 *= c3
            if n <= derivative_order:
                d[n][n-1][v] = 0
            for m in xrange(min(n, derivative_order) +1):
                d[m][n][v] = ( (grids[n] - x0)*d[m][n-1][v] - m*d[m-1][n-1][v] ) / c3
        for m in xrange(min(n, derivative_order) +1):
            d[m][n][n] = fractions.Fraction(c1,c2)*( m*d[m-1][n-1][n-1] - (grids[n-1] - x0)*d[m][n-1][n-1] )
        c1 = c2

    return d[-1][-1]

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
    for k in xrange(grid_size):
        indexes = k + np.arange(grid_size)
        D[:,k] = solve(M[:,indexes], r)

    return D

####################################################################################################

def _check_finite_difference_coefficients():

    for derivative_order, derivative_order_dict in centred_coefficients.iteritems():
        for accuracy_order, coefficients in derivative_order_dict.iteritems():
            if accuracy_order > 1:
                coefficients = np.array(coefficients)
                grid_size = accuracy_order +1
                # D = compute_finite_difference_coefficients(derivative_order, grid_size)
                # computed_coefficients = D[:,grid_size/2]
                computed_coefficients = compute_exact_finite_difference_coefficients(derivative_order,
                                                                                     range(-accuracy_order/2,accuracy_order/2+1))
                computed_coefficients = [float(x) for x in computed_coefficients]
                # print "Derivative order {} Accuracy order {}".format(derivative_order, accuracy_order)
                # print coefficients
                # print computed_coefficients
                # print np.abs(coefficients - computed_coefficients)
                assert(np.all(np.isclose(coefficients, computed_coefficients)))

    for derivative_order, derivative_order_dict in forward_coefficients.iteritems():
        for accuracy_order, coefficients in derivative_order_dict.iteritems():
            if accuracy_order > 1:
                coefficients = np.array(coefficients)
                grid_size = derivative_order + accuracy_order
                # D = compute_finite_difference_coefficients(derivative_order, grid_size)
                # computed_coefficients = D[:,-1]
                computed_coefficients = compute_exact_finite_difference_coefficients(derivative_order, range(grid_size))
                computed_coefficients = [float(x) for x in computed_coefficients]
                # print "Derivative order {} Accuracy order {}".format(derivative_order, accuracy_order)
                # print D
                # print coefficients
                # print computed_coefficients
                # print np.abs(coefficients - computed_coefficients)
                assert(np.all(np.isclose(coefficients, computed_coefficients)))

_check_finite_difference_coefficients()

####################################################################################################
# 
# End
# 
####################################################################################################
