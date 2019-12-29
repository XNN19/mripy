#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import numpy as np
from numpy.polynomial import polynomial
from sklearn import linear_model
from . import six, utils


def nearest(x, parity='odd', round=np.round):
    if parity == 'even':
        return np.int_(round(x/2.0)) * 2
    elif parity == 'odd':
        return np.int_(round((x+1)/2.0)) * 2 - 1


def invert_affine(mat):
    M, v = mat[:,:3], mat[:,3]
    inv = np.linalg.inv(M)
    return np.c_[inv, -inv@v]


def concat_affine(mat2, mat1):
    '''
    mat @ v = mat2 @ mat1 @ v
    '''
    return np.c_[mat2[:,:3]@mat1[:,:3], mat2[:,:3]@mat1[:,3]+mat2[:,3]]


def apply_affine(mat, xyz):
    '''
    xyz : 3xN array
    '''
    return mat[:,:3] @ xyz + mat[:,3:4]


def LPI2RAI_affine(mat):
    LPI2RAI = np.c_[np.diag([-1,-1,1]), np.zeros(3)] # Interestingly, the inverse of LPI2RAI is itself (i.e., LPI2RAI==RAI2LPI)
    return concat_affine(LPI2RAI, concat_affine(mat, LPI2RAI))

RAI2LPI_affine = LPI2RAI_affine
# fsl2afni_affine = LPI2RAI_affine
# afni2fsl_affine = RAI2LPI_affine


def polyfit3d(x, y, z, f, deg, method=None):
    # https://stackoverflow.com/questions/7997152/python-3d-polynomial-surface-fit-order-dependent
    # https://docs.scipy.org/doc/numpy-1.13.0/reference/routines.polynomials.polynomial.html
    if method is None:
        method = 'ols'
    deg = np.array(deg) if utils.iterable(deg) else np.repeat(deg, 3)
    vander = polynomial.polyvander3d(x, y, z, deg)
    vander = vander.reshape(-1,vander.shape[-1])
    if method == 'ols':
        c = np.linalg.lstsq(vander, f.ravel(), rcond=None)[0]
    elif method == 'ridge':
        model = linear_model.Ridge(fit_intercept=False)
        model.fit(vander, f.ravel())
        c = model.coef_
    elif method == 'lasso':
        model = linear_model.Lasso(fit_intercept=False)
        model.fit(vander, f.ravel())
        c = model.coef_
    c = c.reshape(deg+1)
    return c 


def circular_mean(x, domain=None, weight=None, axis=None):
    '''
    Circular mean for values from arbitary circular domain (not necessarily angles).
    '''
    if domain is None:
        domain = [0, 2*np.pi]
    if weight is None:
        weight = np.ones(x.shape)
    # Mapping domain into [0, 2*pi]
    y = (x - domain[0]) / (domain[-1] - domain[0]) * 2*np.pi
    # Circular mean
    mean_y = np.sum(np.exp(1j*y) * weight, axis=axis) / np.sum(weight, axis=axis)
    mean_y = np.mod(np.angle(mean_y), 2*np.pi)
    # Mapping domain back
    mean_x = mean_y / (2*np.pi) * (domain[-1] - domain[0]) + domain[0]
    return mean_x


def circular_std(x, domain=None, weight=None, axis=None):
    '''
    Following scipy.stats.circstd()'s definition of circular standard deviation 
    that in the limit of small angles returns the 'linear' standard deviation.
    scipy.stats.circstd() doesn't support weight.
    pycircstat.std() doesn't support domain.
    astropy.stats.circvar() follows another definition.
    '''
    if domain is None:
        domain = [0, 2*np.pi]
    if weight is None:
        weight = np.ones(x.shape)
    # Mapping domain into [0, 2*pi]
    y = (x - domain[0]) / (domain[-1] - domain[0]) * 2*np.pi
    # Circular std
    mean_y = np.sum(np.exp(1j*y) * weight, axis=axis) / np.sum(weight, axis=axis)
    std_y = np.sqrt(-2*np.log(np.abs(mean_y)))
    # Mapping domain back
    std_x = std_y / (2*np.pi) * (domain[-1] - domain[0])
    return std_x


if __name__ == '__main__':
    pass