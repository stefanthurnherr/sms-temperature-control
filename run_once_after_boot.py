#!/usr/bin/python
# -*- coding: utf-8 -*-
import commands
import datetime
import time
import sys
import subprocess

import ConfigParser

import gammu # for exception handling only
from relay import powerswitcher
from sms import SmsSender


now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

print "{0} -------------------REBOOT-----------------------".format(now_text)

powerswitcher.init_pins()
power_status = powerswitcher.get_status_string_safe()

print "{0} Successfully initialized pins after (re-)boot, power is now {1} ...".format(now_text, power_status)

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')

modem_identifier = config.get('Phone', 'modem_identifier')


lsusb_output = subprocess.check_output("lsusb", stderr=subprocess.STDOUT)
if modem_identifier and (modem_identifier in lsusb_output):
    print "{0} Modem with identifier {1} loaded correctly according to lsusb.".format(now_text, modem_identifier)
else:
    # run usb_modeswitch to ensure 3G modem is in modem state (and not in storage mode)
    print "{0} Modem with identifier {1} not found in lsusb output, running usb_modeswitch...".format(now_text, modem_identifier) 
    time.sleep(30) # wait until modem is connected
    print "-----------------<usb_modeswitch>-------------------"
    sys.stdout.flush()
    return_code = subprocess.call(['/usr/sbin/usb_modeswitch', '-c', '/etc/usb_modeswitch.conf'], stderr=subprocess.STDOUT)
    print "-----------------</usb_modeswitch>------------------"
    print "{0} Ran usb_modeswitch, got return code {1}".format(now_text, return_code)
    if int(return_code) == 0:
        time.sleep(60) # sleep a while after disconnect to give modem time to (re-)connect

sys.stdout.flush()

localIpAddress = commands.getoutput("/sbin/ifconfig").split("\n")[1] 
if 'inet' in localIpAddress:
    localIpAddress = localIpAddress.split()[1][5:]
    print "{0} My IP address is {1}.".format(now_text, localIpAddress)
else:
    localIpAddress = "none" 
    print "{0} No inet interface found, not reachable on any IP address.".format(now_text)

admin_phone_number = config.get('Administrator', 'number')
admin_notify_sms = config.getboolean('Administrator', 'notify_startup_sms')

print "{0} Sending confirmation sms to admin ({1})? {2}.".format(now_text, admin_phone_number, admin_notify_sms)
if admin_notify_sms:
    gammu_config_file = config.get('Phone', 'gammu_config_file')
    gammu_config_section = config.get('Phone', 'gammu_config_section')

    send_success = False
    send_attempts = 0
    retry_interval_seconds = 60
    while not send_success:
        try:
	    send_attempts += 1
    	    
	    sms_sender = SmsSender(gammu_config_file, gammu_config_section)	
    	    network_datetime = sms_sender.get_network_datetime()
    	    system_datetime = now_text

    	    reboot_message = "Hi Admin! Restart (inet:{3}) complete @ system/network {0}/{1}. Power is {2}. ({4} sms send attempts needed)".format(system_datetime, network_datetime, power_status, localIpAddress, send_attempts)
            
	    sms_sender.send_sms(reboot_message, admin_phone_number)
            send_success = True
        except gammu.ERR_TIMEOUT, e:
	    if (e.Code == 14 and e.Where == 'Init'):
		print "{0} attempt #{1} to send boot-completed sms to admin failed, retrying after sleeping {}min ...".format(now_text, send_attempts, retry_interval_seconds/60)
	        time.sleep(retry_interval_seconds)
	    else:
		raise



