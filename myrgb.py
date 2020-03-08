#!/usr/bin/env python3

"""
myrgb.py
27-oct-19 hjltu@ya.ru
"""
from colorsys import rgb_to_hsv as r2h
from colorsys import hsv_to_rgb as h2r

def rgb2hsv(r, g, b):
    print('r2h-in:',r,g,b)
    h, s, v = r2h(float(r)/255, float(g)/255, float(b)/255)
    return h*360, s*255, v*255

def hsv2rgb(h, s, v):
    print('h2r:',h,s,v)
    r, g, b = h2r(float(h)/360, float(s)/255, float(v)/255)
    return r*255, g*255, b*255

