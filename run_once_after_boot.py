#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import subprocess

import ConfigParser

from relay import powerswitcher
from sms import SmsSender


now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

print "{0} -------------------REBOOT-----------------------".format(now_text)

powerswitcher.init_pins()
power_status = powerswitcher.get_status_string_safe()

print "{0} Successfully initialized pins after (re-)boot, power is now {1} ...".format(now_text, power_status)

# FIXME: only run the usb_modeswitch stuff below if required according to lsusb
print "----------------------<lsusb>-----------------------"
sys.stdout.flush()
lsusb_return_code = subprocess.call("lsusb")
print "----------------------</lsusb>----------------------"

# run usb_modeswitch to ensure 3G modem is in modem state (and not in storage mode)
time.sleep(10) # wait until modem is connected
print "-----------------<usb_modeswitch>-------------------"
sys.stdout.flush()
return_code = subprocess.call("/usr/sbin/usb_modeswitch -c /etc/usb_modeswitch.conf", shell=True)
print "-----------------</usb_modeswitch>------------------"
print "{0}    Ran usb_modeswitch, got return code {1}".format(now_text, return_code)
if int(return_code) == 0:
    time.sleep(60) # sleep a while after disconnect to give modem time to (re-)connect

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')
admin_phone_number = config.get('Administrator', 'number')
admin_notify_sms = config.getboolean('Administrator', 'notify_startup_sms')

print "{0}    Sending confirmation sms to admin ({1})? {2}.".format(now_text, admin_phone_number, admin_notify_sms)
if admin_notify_sms:
    gammu_config_file = config.get('Phone', 'gammu_config_file')
    gammu_config_section = config.get('Phone', 'gammu_config_section')

    reboot_message = "Hi Admin! Restart completed at {0}, power is now {1}.".format(now_text, power_status)
    sms_sender = SmsSender(gammu_config_file, gammu_config_section)	
    sms_sender.send_sms(reboot_message, admin_phone_number)
