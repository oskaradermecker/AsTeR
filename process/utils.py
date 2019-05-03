# Author:  DINDIN Meryll
# Date:    03 May 2019
# Project: AsTeR

try: from process.imports import *
except: from imports import *

def interpolate(t_inp, t_out, val):

    if len(val) < len(t_out):
        f = interp1d(t_inp, val, kind='linear', fill_value='extrapolate')
        return f(t_out)

    if len(val) == len(t_out):
        return val

    if len(val) > len(t_out):
        f = interp1d(t_inp, val, kind='quadratic')
        return f(t_out)