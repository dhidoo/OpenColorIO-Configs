#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implements support for *Canon* colorspaces conversions and transfer functions.
"""

import array

import aces_ocio.generate_lut as genlut
from aces_ocio.utilities import ColorSpace

__author__ = 'ACES Developers'
__copyright__ = 'Copyright (C) 2014 - 2015 - ACES Developers'
__license__ = ''
__maintainer__ = 'ACES Developers'
__email__ = 'aces@oscars.org'
__status__ = 'Production'

__all__ = ['create_c_log',
           'create_colorspaces']


def create_c_log(gamut,
                 transfer_function,
                 name,
                 lut_directory,
                 lut_resolution_1d):
    """
    Object description.

    Canon-Log to ACES.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    name = "%s - %s" % (transfer_function, gamut)
    if transfer_function == "":
        name = "Linear - %s" % gamut
    if gamut == "":
        name = "%s" % transfer_function

    cs = ColorSpace(name)
    cs.description = name
    cs.equality_group = ''
    cs.family = 'Canon'
    cs.is_data = False

    def legal_to_full(codeValue):
        return (codeValue - 64.0) / (940.0 - 64.0)

    def c_log_to_linear(codeValue):
        # log = fullToLegal(c1 * log10(c2*linear + 1) + c3)
        # linear = (pow(10, (legalToFul(log) - c3)/c1) - 1)/c2
        c1 = 0.529136
        c2 = 10.1596
        c3 = 0.0730597

        linear = (pow(10.0, (legal_to_full(codeValue) - c3) / c1) - 1.0) / c2
        linear *= 0.9
        # print(codeValue, linear)
        return linear

    cs.to_reference_transforms = []

    if transfer_function == "Canon-Log":
        data = array.array('f', "\0" * lut_resolution_1d * 4)
        for c in range(lut_resolution_1d):
            data[c] = c_log_to_linear(1023.0 * c / (lut_resolution_1d - 1))

        lut = "%s_to_linear.spi1d" % transfer_function
        genlut.write_SPI_1d(lut_directory + "/" + lut,
                            0.0,
                            1.0,
                            data,
                            lut_resolution_1d,
                            1)

        cs.to_reference_transforms.append({
            'type': 'lutFile',
            'path': lut,
            'interpolation': 'linear',
            'direction': 'forward'})

    if gamut == 'Rec. 709 Daylight':
        cs.to_reference_transforms.append({
            'type': 'matrix',
            'matrix': [0.561538969, 0.402060105, 0.036400926, 0.0,
                       0.092739623, 0.924121198, -0.016860821, 0.0,
                       0.084812961, 0.006373835, 0.908813204, 0.0,
                       0, 0, 0, 1.0],
            'direction': 'forward'})
    elif gamut == 'Rec. 709 Tungsten':
        cs.to_reference_transforms.append({
            'type': 'matrix',
            'matrix': [0.566996399, 0.365079418, 0.067924183, 0.0,
                       0.070901044, 0.880331008, 0.048767948, 0.0,
                       0.073013542, -0.066540862, 0.99352732, 0.0,
                       0, 0, 0, 1.0],
            'direction': 'forward'})
    elif gamut == 'DCI-P3 Daylight':
        cs.to_reference_transforms.append({
            'type': 'matrix',
            'matrix': [0.607160575, 0.299507286, 0.093332140, 0.0,
                       0.004968120, 1.050982224, -0.055950343, 0.0,
                       -0.007839939, 0.000809127, 1.007030813, 0.0,
                       0, 0, 0, 1.0],
            'direction': 'forward'})
    elif gamut == 'DCI-P3 Tungsten':
        cs.to_reference_transforms.append({
            'type': 'matrix',
            'matrix': [0.650279125, 0.253880169, 0.095840706, 0.0,
                       -0.026137986, 1.017900530, 0.008237456, 0.0,
                       0.007757558, -0.063081669, 1.055324110, 0.0,
                       0, 0, 0, 1.0],
            'direction': 'forward'})
    elif gamut == 'Cinema Gamut Daylight':
        cs.to_reference_transforms.append({
            'type': 'matrix',
            'matrix': [0.763064455, 0.149021161, 0.087914384, 0.0,
                       0.003657457, 1.10696038, -0.110617837, 0.0,
                       -0.009407794, -0.218383305, 1.227791099, 0.0,
                       0, 0, 0, 1.0],
            'direction': 'forward'})
    elif gamut == 'Cinema Gamut Tungsten':
        cs.to_reference_transforms.append({
            'type': 'matrix',
            'matrix': [0.817416293, 0.090755698, 0.091828009, 0.0,
                       -0.035361374, 1.065690585, -0.030329211, 0.0,
                       0.010390366, -0.299271107, 1.288880741, 0.0,
                       0, 0, 0, 1.0],
            'direction': 'forward'})

    cs.from_reference_transforms = []
    return cs


def create_colorspaces(lut_directory, lut_resolution_1d):
    """
    Generates the colorspace conversions.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    colorspaces = []

    # Full conversion
    c_log_1 = create_c_log(
        "Rec. 709 Daylight",
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_1)

    c_log_2 = create_c_log(
        "Rec. 709 Tungsten",
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_2)

    c_log_3 = create_c_log(
        "DCI-P3 Daylight",
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_3)

    c_log_4 = create_c_log(
        "DCI-P3 Tungsten",
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_4)

    c_log_5 = create_c_log(
        "Cinema Gamut Daylight",
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_5)

    c_log_6 = create_c_log(
        "Cinema Gamut Tungsten",
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_6)

    # Linearization only
    c_log_7 = create_c_log(
        '',
        "Canon-Log",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_7)

    # Primaries only
    c_log_8 = create_c_log(
        "Rec. 709 Daylight",
        "",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_8)

    c_log_9 = create_c_log(
        "Rec. 709 Tungsten",
        "",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_9)

    c_log_10 = create_c_log(
        "DCI-P3 Daylight",
        "",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_10)

    c_log_11 = create_c_log(
        "DCI-P3 Tungsten",
        "",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_11)

    c_log_12 = create_c_log(
        "Cinema Gamut Daylight",
        "",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_12)

    c_log_13 = create_c_log(
        "Cinema Gamut Tungsten",
        "",
        "Canon-Log",
        lut_directory,
        lut_resolution_1d)
    colorspaces.append(c_log_13)

    return colorspaces