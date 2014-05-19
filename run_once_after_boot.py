#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import ConfigParser

from relay import powerswitcher
from sms import smssender


powerswitcher.init_pins()
power_status = powerswitcher.get_status_string_safe()

now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')
admin_phone_number = config.get('Administrator', 'number')

print "{0} Successfully initialized pins after boot, power is now {1}. Sending confirmation sms to {2}.".format(now_text, power_status, admin_phone_number)

reboot_message = "Hi Admin! Restart completed at {0}, power is now {1}.".format(now_text, power_status)
smssender.send_sms(reboot_message, admin_phone_number)
