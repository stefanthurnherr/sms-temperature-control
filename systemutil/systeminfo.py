#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands
from subprocess import Popen, PIPE


def get_rpi_serial_number():
    cpuInfoLines = commands.getoutput("cat /proc/cpuinfo").split("\n")
    #cpuInfoLines = ["hello", "Serial      : 000000065gh7890 ", "world"]
    cpuInfoLines = filter(lambda s: "Serial  " in s, cpuInfoLines)
    return cpuInfoLines[0].split(":")[1].lstrip(' 0')


def get_inet_address():
    localIpAddress = commands.getoutput("/sbin/ifconfig").split("\n")[1] 
    if 'inet' in localIpAddress:
        return localIpAddress.split()[1][5:]
    else:
        return None

def get_git_revision():
    gitproc = Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout = PIPE)
    (stdout, _) = gitproc.communicate()
    return stdout.strip()


if __name__ == "__main__":
    print "System Info utility class with following capabilities:"
    print "  inet address      : {0}".format(get_inet_address())
    print "  git revision      : {0}".format(get_git_revision())
    print "  RPi serial number : {0}".format(get_rpi_serial_number())

    print "Bye."

