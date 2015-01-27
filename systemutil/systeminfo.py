#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands


def get_inet_address():
    localIpAddress = commands.getoutput("/sbin/ifconfig").split("\n")[1] 
    if 'inet' in localIpAddress:
        return localIpAddress.split()[1][5:]
    else:
        return None


if __name__ == "__main__":
    print "System Info utility class with following capabilities:"
    print "  Inet address: {0}".format(get_inet_address())
    print "Bye."

