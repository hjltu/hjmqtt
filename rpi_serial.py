#!/usr/bin/env python3
"""
rpi_serial.py
"""

import os


def get_serial():
    # Extract rpi serial from cpuinfo fi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'Serial' in line:
                    sn = str(line[10:26])
                    print('serial number found:',sn)
                    os.environ['SERIAL'] = sn
                    return sn
            print('serial number not found in /proc/cpuinfo file')
            return "SN"
    except Exception as e:
        return "ger serial ERR:" + str(e)

serial = get_serial()
