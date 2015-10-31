#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import ConfigParser

from systemutil import systeminfo
from relay import PowerAutocontroller
from temp import temperaturereader


CONFIG_FILEPATH = '/home/pi/sms-temperature-control/my.cfg'


# ------------------------------------------------------------------------------- #

def debug(message):
    print("{:>9}  {}".format(os.getpid(), message))
    sys.stdout.flush()
  

if __name__ == '__main__':

    uptime_threshold = 5*60
    uptime = systeminfo.get_uptime_seconds()
    if uptime > uptime_threshold: # otherwise allow reboot script to run completely to clean up etc.

        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read(CONFIG_FILEPATH)

        pgrep_pattern = 'python .*' + os.path.basename(__file__) + '\\\''
        pgrep_pids = systeminfo.get_pgrep_pids(pgrep_pattern)

        if len(pgrep_pids) < 1:
            debug("pgrep pattern wrong, my own script process not found: {}".format(pgrep_pattern))
        elif len(pgrep_pids) == 1 and pgrep_pids[0] == os.getpid():
            debug("START no other pid found for this script (PID: {}), going ahead with running power autocontroller...".format(pgrep_pids))
            power_autocontroller = PowerAutocontroller(config_parser)

            current_temp_raw = temperaturereader.read_celsius()

            power_autocontroller.run(current_temp_raw)
            debug("DONE running power autocontroller.")
        else:
            debug("Found other processes already running this script (PIDs: {}), skipping this script run.".format(pgrep_pids))

    else:
        debug("Uptime ({0} seconds) is less than {1} seconds, skipping ensuring minimum temperature.".format(uptime, uptime_threshold))

