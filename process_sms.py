#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
import time
import os
import ConfigParser
import gammu # for exception handling only

from temp import temperaturereader
from sms import SmsFetcher
from sms import SmsSender
from relay import powerswitcher

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')

MY_NUMBER = config.get('Phone', 'number')
GAMMU_CONFIG_FILE = config.get('Phone', 'gammu_config_file')
GAMMU_CONFIG_SECTION = config.get('Phone', 'gammu_config_section')

BLACKLIST_SENDERS = config.get('SmsProcessing', 'blacklist_senders')

now = datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

signal_strength_percentage = '--'
time_before_fetch = time.time()
try:
    sms_fetcher = SmsFetcher(GAMMU_CONFIG_FILE, GAMMU_CONFIG_SECTION) 
    signal_strength_percentage = sms_fetcher.get_signal_strength_percentage()
    sms_messages = sms_fetcher.delete_get_next_sms()
except (gammu.ERR_TIMEOUT, gammu.ERR_DEVICENOTEXIST, gammu.ERR_NOTCONNECTED):
    timeout_after_time = time.time() - time_before_fetch
    print "{0} Got exception after {1} seconds while trying to fetch/delete next sms (signalStrength: {2}%).".format(now_text, timeout_after_time, signal_strength_percentage)
    raise # re-raise exception so we get the stacktrace to stderr

absolute_script_path = os.path.abspath(__file__)

if not sms_messages:
    # would write a log message every minute even if no sms found 
    #print "{0} No sms found by {1} - bye.".format(now_text, absolute_script_path)
    sys.exit()

print "{0} Start sms processing by {1}".format(now_text, absolute_script_path)

sms = sms_messages[0]

# set system datetime to sent/received DateTime from received sms if delta is big enough
system_datetime = datetime.now()
sms_datetime = sms[0]['DateTime']
delta_datetime = sms_datetime - system_datetime
delta_seconds = delta_datetime.total_seconds()
delta_max = 90 * 60 # 90 minutes
if abs(delta_seconds) > delta_max:
    # example unix date: Thu Nov 28 23:29:53 CET 2014
    sms_datetime_unix = sms_datetime.strftime("%a %b %d %H:%M:%S CET 2014")
    set_date_cmd = "date -s \"{0}\"".format(sms_datetime_unix)
    print "{0} Updating system date using cmd: {1}".format(now_text, set_date_cmd)
    os.system(set_date_cmd)
else:
    print "{0} system date diff is less than configured delta (diff = {1} seconds), skipping updating.".format(now_text, delta_seconds)


sender_number = sms[0]['Number']
sender_message_raw = sms[0]['Text']
sender_message = repr(sender_message_raw)
print "  got sms message from {0}: {1}".format(sender_number, sender_message)

if MY_NUMBER in sender_number:
    print "  got sms from my own number - not responding in order to prevent infinite loop. Bye!"
    sys.exit()
elif BLACKLIST_SENDERS: # empty strings are false in python
   for blacklist_sender in BLACKLIST_SENDERS.split(","): 
        if len(blacklist_sender) > 0 and blacklist_sender in sender_number: 
            print "  this sender is in blacklist (matched '{0}') - ignoring. Bye!".format(blacklist_sender)
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

time_before_send = time.time()
try:
    sms_sender = SmsSender(GAMMU_CONFIG_FILE, GAMMU_CONFIG_SECTION) 
    sms_sender.send_sms(response_message, sender_number)
except (gammu.ERR_UNKNOWN):
    timeout_after_time = time.time() - time_before_send
    print "{0} Got exception after {1} seconds while trying to send sms.".format(now_text, timeout_after_time)
    raise # re-raise exception so we get the stacktrace to stderr

