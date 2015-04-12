#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import glob
import time
import sys
import os
import subprocess

import ConfigParser

import gammu # for exception handling only
from relay import PowerSwitcher
from sms import SmsSender
from systemutil import systeminfo


log_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("{0} -------------------REBOOT-----------------------".format(log_ts))

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')

work_dir = config.get('System', 'work_dir')
for lock_file_path in glob.iglob(work_dir + '/.lock*'):
    print("{0} removing old lockfile '{1}'.".format(log_ts, lock_file_path))
    os.remove(lock_file_path)

channel_list = config.get('PowerSwitching', 'relay_gpio_channels')
gpio_channels = [int(channel) for channel in channel_list.split(',')]
powerswitcher = PowerSwitcher(gpio_channels=gpio_channels)
power_status = powerswitcher.get_status_string()

print("{0} Successfully initialized pins after (re-)boot, power is now {1} ...".format(log_ts, power_status))

modem_identifier = config.get('Phone', 'modem_identifier')

lsusb_output = subprocess.check_output("lsusb", bufsize=-1, stderr=subprocess.STDOUT)
if modem_identifier and (modem_identifier in lsusb_output):
    print("{0} Modem with identifier {1} loaded correctly according to lsusb.".format(log_ts, modem_identifier))
elif modem_identifier:
    # run usb_modeswitch to ensure 3G modem is in modem state (and not in storage mode)
    print("{0} Modem with identifier {1} not found in lsusb output, running usb_modeswitch after 30secs sleep ...".format(log_ts, modem_identifier))
    time.sleep(30) # wait until modem is connected
    print("-----------------<usb_modeswitch>-------------------")
    sys.stdout.flush()
    # -I arg needed for Huawei E1820, otherwise modeswitch doesn't work upon cold boot without additional warm reboot
    return_code = subprocess.call(['/usr/sbin/usb_modeswitch', '-I', '-c', '/etc/usb_modeswitch.conf'], bufsize=-1, stderr=subprocess.STDOUT)
    print("-----------------</usb_modeswitch>------------------")
    print("{0} Ran usb_modeswitch, got return code {1}".format(log_ts, return_code))
    if int(return_code) == 0:
        print("{0} sleeping for 60secs before continuing ...".format(log_ts))
        time.sleep(60) # sleep a while after disconnect to give modem time to (re-)connect
else:
    print("{0} No modem_identifier specified, skipping usb_modeswitch enforcement.".format(log_ts))

sys.stdout.flush()

localIpAddress = systeminfo.get_inet_address()
if localIpAddress:
    print("{0} My IP address is {1}.".format(log_ts, localIpAddress))
else:
    localIpAddress = 'None'
    print("{0} No inet interface found, not reachable on any IP address.".format(log_ts))

admin_phone_number = config.get('Administrator', 'number')
admin_notify_sms = config.getboolean('Administrator', 'notify_startup_sms')

print("{0} Sending confirmation sms to admin ({1})? {2}.".format(log_ts, admin_phone_number, admin_notify_sms))
if admin_notify_sms:
    gammu_config_file = config.get('Phone', 'gammu_config_file')
    gammu_config_section = config.get('Phone', 'gammu_config_section')
   
    gammu_errors_count = '0' 
    errors_file = work_dir + '/GAMMU_ERRORS'
    if os.path.isfile(errors_file):
        with open(errors_file, 'r') as f:
            gammu_errors_count = f.readlines()[0]
    current_reboot_threshold = '-'
    errors_threshold_file = work_dir + '/ERRORS_THRESHOLD_BEFORE_REBOOT'
    if os.path.isfile(errors_threshold_file):
        with open(errors_threshold_file, 'r') as f:
            current_reboot_threshold = f.readlines()[0]

    send_success = False
    send_attempts = 0
    retry_interval_seconds = 60
    while not send_success:
        try:
            send_attempts += 1
    	    
            sms_sender = SmsSender(gammu_config_file, gammu_config_section)	

            reboot_message = u'Hi Admin! Reboot done @ {0}. Power is {1}. Inet: {2}. {3} sms send attempts needed. 3G dongle error status: {4}/{5}.'.format(log_ts, power_status, localIpAddress, send_attempts, gammu_errors_count, current_reboot_threshold)
            
            sms_sender.send_sms(reboot_message, admin_phone_number)
            send_success = True
        except (gammu.ERR_TIMEOUT) as e:
	    if (('Code' in e and e['Code'] == 14) and ('Where' in e and e['Where'] == 'Init')):
		print("{0} attempt #{1} to send boot-completed sms to admin failed, retrying after sleeping {2}mins ...".format(log_ts, send_attempts, retry_interval_seconds/60))
	        time.sleep(retry_interval_seconds)
	    else:
		raise

