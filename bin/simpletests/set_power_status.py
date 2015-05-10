#!/usr/bin/python
# -*- coding: utf-8 -*-

from relay import powerswitcher


powerswitcher.setup()

old_power_status = powerswitcher.get_status()
old_power_status_string = powerswitcher.get_status_string()

if old_power_status == 0:
    powerswitcher.set_status_off()
else:
    powerswitcher.set_status_on()

new_power_status_string = powerswitcher.get_status_string()

#powerswitcher.tearDown()

print("toggled power status from {0} to {1}".format(old_power_status_string, new_power_status_string))
