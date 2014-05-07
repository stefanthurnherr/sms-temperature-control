#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
import os
import ConfigParser

from temp import temperaturereader
from sms import smsfetcher
from sms import smssender
from relay import powerswitcher

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')
MY_NUMBER = config.get('Phone', 'number')

sms_messages = smsfetcher.delete_get_next_sms()

now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")
absolute_script_path = os.path.abspath(__file__)


if not sms_messages:
    print "{0} No sms found by {1} - bye.".format(now_text, absolute_script_path)
    sys.exit()

print "{0} Start sms processing by {1}".format(now_text, absolute_script_path)

sms = sms_messages[0]

sender_number = sms[0]['Number']
sender_datetime = sms[0]['DateTime'].strftime("%Y-%m-%d %H:%M:%S")
sender_message_raw = sms[0]['Text']
sender_message = repr(sender_message_raw)
print "  got sms message from {0}: {1}".format(sender_number, sender_message)

if MY_NUMBER in sender_number:
    print "  got sms from my own number - not responding in order to prevent infinite loop. Bye!"
    sys.exit()

if len(sms_messages) > 1:
    print "  found sms consisting of {0} parts - only the first part will be considered.".format(len(sms_messages))


response_message = None

if sender_message_raw and sender_message_raw.lower().startswith('temp'):
    temp_raw = temperaturereader.read_celsius()
    temp = round(temp_raw, 1)
    print "  responding with temperature: {0} Celsius.".format(temp)
    response_message = "Hi! Current temperature here is {0} Celsius ({1}).".format(temp, now_text)

elif sender_message_raw and sender_message_raw.lower().startswith('power'):
    
    requested_state = ''
    power_status_before = powerswitcher.get_status_string_safe()
    if sender_message_raw.lower().startswith('power on'):
        requested_state = 'ON'
        powerswitcher.set_status_on_safe()
        print"  power has been set ON"
    elif sender_message_raw.lower().startswith('power off'):
        requested_state = 'OFF'
        powerswitcher.set_status_off_safe()
        print"  power has been set OFF"

    power_status = powerswitcher.get_status_string_safe()
    
    print "  responding with power status: {0} (was: {1}).".format(power_status, power_status_before)
    if requested_state:
        response_message = "Hi! Power has been switched {0}, was {1} ({2}).".format(power_status, power_status_before, now_text)
    else:
        response_message = "Hi! Power is currently {0} ({1}).".format(power_status, now_text)

else:
    print "  not recognized, answering with help message."
    response_message = "Hi! To get current temperature, start sms with 'temp'. To check/control power, start sms with 'power' (followed by on/off to control)."

#response_message = response_message + " Your message from {0} was: \"{1}\"".format(sender_datetime, sender_message)

smssender.send_sms(response_message, sender_number)

