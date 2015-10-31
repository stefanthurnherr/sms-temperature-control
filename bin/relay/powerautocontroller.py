#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import ConfigParser

from relay import PowerSwitcher


class PowerAutocontroller(object):

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

    def set_switch_onoff_temperatures(self, outputConfigFilepath, switchOnTemperature, switchOffTemperature):
        float(switchOnTemperature)
        float(switchOffTemperature)
        self.config_parser.set('PowerAutocontrol', 'switch_on_temperature', str(switchOnTemperature))
        self.config_parser.set('PowerAutocontrol', 'switch_off_temperature', str(switchOffTemperature))
        with open(outputConfigFilepath, 'w') as f:
            self.config_parser.write(f)
 
    def run(self, currentTemperature):
        if not self.config['enabled']:
            debug("  power autocontrol disabled by configuration, aborting.")
            return

        lower_bound = get_switch_on_temperature()
        upper_bound = get_switch_off_temperature()

        gpio_channels = [int(channel) for channel in self.config['relayGpioChannels'].split(',')]

        powerswitcher = PowerSwitcher(gpio_channels=gpio_channels)
        power_status_before = powerswitcher.get_status_string()

        if currentTemperature > upper_bound or currentTemperature < lower_bound:
            debug("  current temperature {0} is outside configured interval [{1},{2}], ensuring power is switched OFF ...".format(currentTemperature, lower_bound, upper_bound))
            powerswitcher.set_status_off()
        else:
            debug("  current temperature {0} is within configured interval [{1},{2}], ensuring power is switched ON ...".format(currentTemperature, lower_bound, upper_bound))
            powerswitcher.set_status_on()

        power_status_after = powerswitcher.get_status_string()
        debug("  power is now {1} (was: {0})".format(power_status_before, power_status_after))


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

    poc = PowerAutocontroller(config_parser)


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
            debug("START no other pid found for this script (PID: {}), going ahead with running power autocontroller...".format(pgrep_pids))
            power_autocontroller = PowerAutocontroller(config_parser)
            power_autocontroller.run()
            debug("DONE running power autocontroller.")
        else:
            debug("Found other processes already running this script (PIDs: {}), skipping this script run.".format(pgrep_pids))

    else:
        debug("Uptime ({0} seconds) is less than {1} seconds, skipping ensuring minimum temperature.".format(uptime, uptime_threshold))

