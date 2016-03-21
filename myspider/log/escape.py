#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-21 21:55:18
# ---------------------------------------


__all__ = ('escape_codes', 'parse_colors')


def escape(*x):
    if x[0].startswith('0'):
        codes = ';'.join(x)
    else:
        codes = '0;' + ';'.join(x)
    return '\033[' + codes + 'm'


escape_codes = {
    'reset':    escape('0'),
    'black':    escape('90'),
    'red':      escape('91'),
    'green':    escape('92'),
    'yellow':   escape('93'),
    'blue':     escape('94'),
    'purple':   escape('95'),
    'cyan':     escape('96'),
    'white':    escape('97'),
}


def parse_colors(name):
    return escape_codes[name]
