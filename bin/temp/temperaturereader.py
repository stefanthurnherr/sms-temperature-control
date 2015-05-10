#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import glob
import time


def __get_device_file():
    base_dir = '/sys/bus/w1/devices/'
    deviceFolders = glob.glob(base_dir + '28*')
    if len(deviceFolders) == 0:
        print("no 28* device folder found under {0}, bye.".format(base_dir))
        return None
 
    return deviceFolders[0] + '/w1_slave'


def read_temp_raw():
    device_file = __get_device_file()
    if device_file: 
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    else:
        return None


def read_celsius():
    lines = read_temp_raw()
    if not lines:
        return None
 
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


if __name__ == "__main__":
    print(read_celsius())
