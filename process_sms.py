#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
import time
import os
import subprocess
import ConfigParser
import gammu # for exception handling only

from temp import temperaturereader
from sms import SmsFetcher
from sms import SmsSender
from sms import UssdFetcher
from relay import powerswitcher
from systemutil import systeminfo


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TemperatureController(object):

    (NO_SMS_FOUND, SMS_PROCESSED, SMS_IGNORED) = (0, 1, 2) 

    def __init__(self, config_parser):
        self.config = {}

        work_dir_raw = config_parser.get('System', 'work_dir')
        work_dir = os.path.abspath(work_dir_raw)
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        self.config['workDir'] = work_dir
    
        self.config['myNumber'] = config_parser.get('Phone', 'number')
        self.config['gammuConfigFile'] = config_parser.get('Phone', 'gammu_config_file')
        self.config['gammuConfigSection'] = config_parser.get('Phone', 'gammu_config_section')
        self.config['ussdCheckBalance'] = config_parser.get('Phone', 'ussd_balance_inquiry')
    
        self.config['blacklistSenders'] = config_parser.get('SmsProcessing', 'blacklist_senders')
        self.config['systemDatetimeMaxDiffNoUpdateSeconds'] = config_parser.getint('SmsProcessing', 'system_datetime_max_diff_no_update_seconds')

        self.log_ts = datetime.now().strftime(DATETIME_FORMAT)


    def run(self):
        errors_file = self.config['workDir'] + '/GAMMU_ERRORS'
        errors_threshold_file = self.config['workDir'] + '/ERRORS_THRESHOLD_BEFORE_REBOOT'
        
        error_occurred = True
        try:
            sms_processed_status = self.__process_next_sms()
            error_occurred = False
       
        #except:
        #    print "error occurred while trying to process sms: ", sys.exc_info()[0] 
        
        finally:
            if error_occurred:
                current_reboot_threshold = 4 #first forced reboot after this number of successive gammu errors
                schedule_reboot = False
                if os.path.isfile(errors_threshold_file):
                    with open(errors_threshold_file, 'r') as f:
                        current_reboot_threshold = self.__read_file_and_parse_first_int(f)
               
                new_error_count = 1 
                if os.path.isfile(errors_file):
                    with open(errors_file, 'r+') as f:
                        old_error_count = self.__read_file_and_parse_first_int(f)
                        new_error_count = old_error_count + 1 
                        f.seek(0) 
                        self.__write_int_to_file(f, new_error_count)
                else:
                    with open(errors_file, 'w') as f:
                        self.__write_int_to_file(f, new_error_count) 
                
                schedule_reboot = new_error_count >= current_reboot_threshold 
                next_reboot_threshold = 2 * current_reboot_threshold
                print "{0} caught error number {1} while trying to process next sms, scheduling reboot? {2}.".format(self.log_ts, new_error_count, schedule_reboot) 
                
                if schedule_reboot:
                    with open(errors_threshold_file, 'w') as f:
                        self.__write_int_to_file(f, next_reboot_threshold) 
                    return_code = subprocess.call(['/usr/bin/sudo', '/sbin/shutdown', '-r', 'now'], bufsize=-1, stderr=subprocess.STDOUT)
                    print "{0} reboot scheduled (return code:{1}), next gammu error threshold is {2} ...".format(self.log_ts, return_code, next_reboot_threshold)

            else:
                os.remove(errors_file) if os.path.isfile(errors_file) else None
                os.remove(errors_threshold_file) if os.path.isfile(errors_threshold_file) else None


    def __read_file_and_parse_first_int(self, f):
        first_line = f.readlines()[0]
        return int(first_line)
       
    def __write_int_to_file(self, f, int_value):
        f.write(str(int_value))
 

    def __process_next_sms(self):
        signal_strength_percentage = '--'
        time_before_fetch = time.time()
        try:
            sms_fetcher = SmsFetcher(self.config['gammuConfigFile'], self.config['gammuConfigSection']) 
            signal_strength_percentage = sms_fetcher.get_signal_strength_percentage()
            sms_messages = sms_fetcher.delete_get_next_sms()
        except (gammu.ERR_TIMEOUT, gammu.ERR_DEVICENOTEXIST, gammu.ERR_NOTCONNECTED):
            timeout_after_time = time.time() - time_before_fetch
            print "{0} Got exception after {1} seconds while trying to fetch/delete next sms (signalStrength: {2}%).".format(self.log_ts, timeout_after_time, signal_strength_percentage)
            raise # re-raise exception so we get the stacktrace to stderr
        
        absolute_script_path = os.path.abspath(__file__)
        
        if not sms_messages:
            # would write a log message every minute even if no sms found 
            #print "{0} No sms found by {1} - bye.".format(self.log_ts, absolute_script_path)
            return TemperatureController.NO_SMS_FOUND
        
        print "{0} Start sms processing by {1}".format(self.log_ts, absolute_script_path)
        
        sms = sms_messages[0]
        
        # set system datetime to sent/received DateTime from received sms if delta is big enough
        if self.config['systemDatetimeMaxDiffNoUpdateSeconds'] > 0:
            system_datetime = datetime.now()
            sms_datetime = sms[0]['DateTime']
            delta_datetime = sms_datetime - system_datetime
            delta_seconds = delta_datetime.total_seconds()
            if abs(delta_seconds) > self.config['systemDatetimeMaxDiffNoUpdateSeconds']:
                # example unix date: Thu Nov 28 23:29:53 CET 2014
                sms_datetime_unix = sms_datetime.strftime("%a %b %d %H:%M:%S CET %Y")
                set_date_cmd = "date -s \"{0}\" > /dev/null".format(sms_datetime_unix)
                print "{0} Updating system datetime (delta: {1} seconds) using cmd: {2}".format(self.log_ts, delta_seconds, set_date_cmd)
                os.system(set_date_cmd)
            #else:
        	#print "{0} system date diff ({1} seconds) is not greater than configured delta ({2} seconds), skipping updating.".format(self.log_ts, delta_seconds, self.config['systemDatetimeMaxDiffNoUpdateSeconds'])
        
        now_string = datetime.now().strftime(DATETIME_FORMAT)
        
        sender_number = sms[0]['Number']
        sender_message_raw = sms[0]['Text']
        sender_message = repr(sender_message_raw)
        print "  got sms message from {0}: {1}".format(sender_number, sender_message)
        
        if self.config['myNumber'] in sender_number:
            print "  got sms from my own number - not responding in order to prevent infinite loop. Bye!"
            return TemperatureController.SMS_IGNORED
        elif self.config['blacklistSenders']: # empty strings are false in python
           for blacklist_sender in self.config['blacklistSenders'].split(","): 
                if len(blacklist_sender) > 0 and blacklist_sender in sender_number: 
                    print "  this sender is in blacklist (matched '{0}') - ignoring. Bye!".format(blacklist_sender)
                    return TemperatureController.SMS_IGNORED
        
        if len(sms_messages) > 1:
            print "  found sms consisting of {0} parts - only the first part will be considered.".format(len(sms_messages))
        
        
        response_message = None
        
        if sender_message_raw and sender_message_raw.lower().startswith('temp'):
            temp_raw = temperaturereader.read_celsius()
            if temp_raw: 
                temp = round(temp_raw, 1)
                print "  responding with temperature: {0} Celsius.".format(temp)
                response_message = "Hi! Current temperature here is {0} Celsius ({1}).".format(temp, now_string)
            else:
                print "  temperature could not be read."
                response_message = "Hi! Temperature sensor is offline, check log files."
        
        elif sender_message_raw and sender_message_raw.lower().startswith('power'):
            requested_state = ''
            power_status_before = powerswitcher.get_status_string_safe()
            if sender_message_raw.lower().startswith('power on'):
                requested_state = 'ON'
                powerswitcher.set_status_on_safe()
                print "  power has been set ON"
            elif sender_message_raw.lower().startswith('power off'):
                requested_state = 'OFF'
                powerswitcher.set_status_off_safe()
                print "  power has been set OFF"
        
            power_status = powerswitcher.get_status_string_safe()
            
            print "  responding with power status: {0} (was: {1}).".format(power_status, power_status_before)
            if requested_state:
                response_message = "Hi! Power has been switched {0}, was {1} ({2}).".format(power_status, power_status_before, now_string)
            else:
                response_message = "Hi! Power is currently {0} ({1}).".format(power_status, now_string)
        
        elif sender_message_raw and sender_message_raw.lower().startswith('systeminfo'):
            print "  responding with system info:"
            up_since = systeminfo.get_last_reboot_date_time()
            kernelVersion = systeminfo.get_kernel_version()
            rpiSerialNumber = systeminfo.get_rpi_serial_number()
            localInetAddress = systeminfo.get_inet_address()
            gitRevision = systeminfo.get_git_revision()
            print "    system datetime  : {0}".format(now_string)
            print "    up since         : {0}".format(up_since)
            print "    kernel version   : {0}".format(kernelVersion)
            print "    RPi serial       : {0}".format(rpiSerialNumber)
            print "    inet address     : {0}".format(localInetAddress)
            print "    git revision     : {0}".format(gitRevision)
            print "    Signal strength  : {0}%".format(signal_strength_percentage)
            response_message = "Hi!\n systemTime: {0}\n upSince: {1}\n kernel: {2}\n rpiSerial: {3}\n inet: {4}\n gitRev: {5}\n signal: {6}%\n.".format(now_string, up_since, kernelVersion, rpiSerialNumber, localInetAddress, gitRevision, signal_strength_percentage)
        
        
        elif sender_message_raw and sender_message_raw.lower().startswith('checkbalance'):
            ussd = self.config['ussdCheckBalance']
            print "  responding with USSD reply for {0} ...".format(ussd)
            ussd_fetcher = UssdFetcher(self.config['gammuConfigFile'], self.config['gammuConfigSection'])
            ussd_response = ussd_fetcher.fetch_ussd_response(ussd)
            print ussd_response
            response_message = ussd_response

        else:
            print "  not recognized, answering with help message."
            response_message = "Hi! To get temperature, start sms with 'temp'. To check power, start sms with 'power' (followed by 'on'/'off' to control). Other commands: systeminfo and checkbalance ({0}).".format(now_string)
        
        time_before_send = time.time()
        try:
            sms_sender = SmsSender(self.config['gammuConfigFile'], self.config['gammuConfigSection']) 
            sms_sender.send_sms(response_message, sender_number)
            return TemperatureController.SMS_PROCESSED
        except (gammu.ERR_UNKNOWN):
            timeout_after_time = time.time() - time_before_send
            print "{0} Got exception after {1} seconds while trying to send sms.".format(self.log_ts, timeout_after_time)
            raise # re-raise exception so we get the stacktrace to stderr


if __name__ == '__main__':
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read('/home/pi/sms-temperature-control/my.cfg')

    temperature_controller = TemperatureController(config_parser)
    temperature_controller.run()
