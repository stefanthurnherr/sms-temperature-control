#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
from datetime import datetime,timedelta
import time
import os
import subprocess
import ConfigParser

from temp import temperaturereader
from relay import PowerSwitcher


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TemperatureKeeper(object):

    def __init__(self, config_parser):
        self.config = {}
        self.config_parser = config_parser

        log_dir_raw = config_parser.get('System', 'log_dir')
        log_dir = os.path.abspath(log_dir_raw)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.config['logDir'] = log_dir

        self.config['enabled'] = config_parser.getboolean('PowerAutocontrol', 'enabled')
        self.config['relayGpioChannels'] = config_parser.get('PowerSwitching', 'relay_gpio_channels')

    def get_switch_on_temperature(self):
        return self.config_parser.getfloat('PowerAutocontrol', 'switch_on_temperature')

    def get_switch_off_temperature(self):
        return self.config_parser.getfloat('PowerAutocontrol', 'switch_off_temperature')

    def set_on_off_temperatures(self, switchOnTemperature, switchOffTemperature) {
        float(switchOnTemperature)
        float(switchOffTemperature)
        self.config_parser.set('PowerAutocontrol', 'switch_on_temperature', str(switchOnTemperature))
        self.config_parser.set('PowerAutocontrol', 'switch_off_temperature', str(switchOffTemperature))
    }
 
    def run(self):
        if not self.config['enabled']:
            debug("Power autocontrol disabled, aborting.")
            return

        temp_raw = temperaturereader.read_celsius()
        if temp_raw: 
            temp = round(temp_raw, 1)
            debug("  responding with temperature: {} Celsius.".format(temp))
        else:
            debug("  temperature could not be read.")
            response_message = u'Hi! Temperature sensor is offline, check log files.'    


# ------------------------------------------------------------------------------- #

def debug(message):
    print("{:>9}  {}".format(os.getpid(), message))
    sys.stdout.flush()
  

# How to run this method from command-line:
#  python -c 'from keep_temperature import test; test()'
#
def test():
    debug("welcome to test()")
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read('/home/pi/sms-temperature-control/my.cfg')

    tk = TemperatureKeeper(config_parser)


if __name__ == '__main__':

    uptime_threshold = 5*60
    uptime = systeminfo.get_uptime_seconds()
    if uptime > uptime_threshold: # otherwise allow reboot script to run completely to clean up etc.

        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read('/home/pi/sms-temperature-control/my.cfg')

        pgrep_pattern = 'python .*' + os.path.basename(__file__) + '\\\''
        pgrep_pids = systeminfo.get_pgrep_pids(pgrep_pattern)

        if len(pgrep_pids) < 1:
            debug("pgrep pattern wrong, my own script process not found: {}".format(pgrep_pattern))
        elif len(pgrep_pids) == 1 and pgrep_pids[0] == os.getpid():
            debug("START no other pid found for this script (PID: {}), going ahead with ensuring minimum temperature...".format(pgrep_pids))
            temperature_keeper = TemperatureKeeper(config_parser)
            temperature_keeper.run()
            debug("DONE ensuring minimum temperature.")
        else:
            debug("Found other processes already running this script (PIDs: {}), skipping this script run.".format(pgrep_pids))

    else:
        debug("Uptime ({0} seconds) is less than {1} seconds, skipping ensuring minimum temperature.".format(uptime, uptime_threshold))

