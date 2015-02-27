#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from subprocess import Popen, PIPE

def get_last_reboot_date_time():
    who_out = __get_cmd_stdout(['who', '-b'])
    date_time_index = who_out.find('boot') + 4
    return who_out[date_time_index:].strip()


def get_kernel_version():
    return __get_cmd_stdout(['uname', '-r']).strip()


def get_rpi_serial_number():
    stdout = __get_cmd_stdout(['cat', '/proc/cpuinfo']) 
    if stdout:
        cpuInfoLines = filter(lambda s: s.startswith('Serial'), stdout.split("\n"))
        cpuInfoLines = cpuInfoLines[0]
        cpuInfoLines = cpuInfoLines.split(":")[1]
        return cpuInfoLines.lstrip(' 0')
    else:
        return None


def get_inet_address(addIface=False):
    interfaceNames = ['eth0', 'eth1', 'wlan0']
    for interfaceName in interfaceNames:
        ifaceSuffix = ''
        if addIface:
            ifaceSuffix = ' (' + interfaceName + ')'
        
        ipAddress = __extract_inet_string(interfaceName)
        if ipAddress: 
            return ipAddress + ifaceSuffix
    return None


def __extract_inet_string(interfaceName):
    networkInterfaceString = __get_cmd_stdout(['/sbin/ifconfig', interfaceName])
    if not networkInterfaceString:
        return None 
    ipAddress = networkInterfaceString.strip().split("\n")[1]
    if 'inet' in ipAddress:
        return ipAddress.split()[1][5:] 
    else:
        return None
    

def get_git_revision():
    with open(os.devnull, "w") as fnull:
	scriptDirectory = os.path.dirname(os.path.abspath(__file__))
        gitproc = Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout = PIPE, stderr = fnull, cwd=scriptDirectory)
        (stdout, _) = gitproc.communicate()
        if stdout:    
            return stdout.strip()
        else:
            return None


def __get_cmd_stdout(cmd):
    with open(os.devnull, "w") as fnull:
        proc = Popen(cmd, stdout = PIPE, stderr = fnull)
        (stdout, _) = proc.communicate()
        return stdout


if __name__ == "__main__":
    print "System Info utility class with following capabilities:"
    print "  kernel version    : {0}".format(get_kernel_version())
    print "  inet address      : {0}".format(get_inet_address())
    print "  git revision      : {0}".format(get_git_revision())
    print "  RPi serial number : {0}".format(get_rpi_serial_number())

    print "Bye."

