#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from subprocess import Popen, PIPE


def get_rpi_serial_number():
    with open(os.devnull, "w") as fnull:
        cpuInfoProc = Popen(['cat', '/proc/cpuinfo'], stdout = PIPE, stderr = fnull)
        (stdout, _) = cpuInfoProc.communicate()
        if stdout:
            cpuInfoLines = filter(lambda s: "Serial  " in s, stdout.split("\n"))
            return cpuInfoLines[0].split(":")[1].lstrip(' 0')
        else:
            return None


def get_inet_address():
    with open(os.devnull, "w") as fnull:
        ifConfigProc = Popen('/sbin/ifconfig', stdout = PIPE, stderr = fnull)
        (stdout, _) = ifConfigProc.communicate()
        localIpAddress = stdout.strip().split("\n")[1]
        if 'inet' in localIpAddress:
            return localIpAddress.split()[1][5:]
        else:
            return None


def get_git_revision():
    with open(os.devnull, "w") as fnull:
        gitproc = Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout = PIPE, stderr = fnull)
        (stdout, _) = gitproc.communicate()
        if stdout:    
            return stdout.strip()
        else:
            return None


if __name__ == "__main__":
    print "System Info utility class with following capabilities:"
    print "  inet address      : {0}".format(get_inet_address())
    print "  git revision      : {0}".format(get_git_revision())
    print "  RPi serial number : {0}".format(get_rpi_serial_number())

    print "Bye."

