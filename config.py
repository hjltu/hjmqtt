#!/usr/bin/env python3
"""
config.py
"""

import os


def get_serial():
    # Extract rpi serial from cpuinfo fi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'Serial' in line:
                    sn = str(line[10:26])
                    print('sn',sn)
                    os.environ['SERIAL'] = sn
                    return sn
            return "SN"
    except Exception as e:
        return "ERR:" + str(e)


SERIAL = get_serial()
