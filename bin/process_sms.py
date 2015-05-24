#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
from datetime import datetime,timedelta
import time
import os
import subprocess
import ConfigParser
import gammu # for exception handling only

from temp import temperaturereader
from sms import SmsFetcher
from sms import SmsSender
from sms import UssdFetcher
from relay import PowerSwitcher
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

        log_dir_raw = config_parser.get('System', 'log_dir')
        log_dir = os.path.abspath(log_dir_raw)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.config['logDir'] = log_dir
    
        self.config['myNumber'] = config_parser.get('Phone', 'number')
        self.config['gammuConfigFile'] = config_parser.get('Phone', 'gammu_config_file')
        self.config['gammuConfigSection'] = config_parser.get('Phone', 'gammu_config_section')
        self.config['ussdCheckBalance'] = config_parser.get('Phone', 'ussd_balance_inquiry')
        self.config['balanceFetchInterval'] = config_parser.getint('Phone', 'ussd_balance_auto_fetch_interval_days')
        self.config['balanceInfoRegex'] = config_parser.get('Phone', 'ussd_balance_reply_line_regex')
    
        self.config['blacklistSenders'] = config_parser.get('SmsProcessing', 'blacklist_senders')
        self.config['systemDatetimeMaxDiffNoUpdateSeconds'] = config_parser.getint('SmsProcessing', 'system_datetime_max_diff_no_update_seconds')

        self.config['relayGpioChannels'] = config_parser.get('PowerSwitching', 'relay_gpio_channels')
        
        rebootIntervalDaysString = config_parser.get('System', 'reboot_interval_days')
        if rebootIntervalDaysString:
            rebootIntervalDays = int(rebootIntervalDaysString)
        else:
            rebootIntervalDays = 0
        self.config['rebootIntervalDays'] = rebootIntervalDays


    def run(self):
        errors_file = self.config['workDir'] + '/GAMMU_ERRORS'
        errors_threshold_file = self.config['workDir'] + '/ERRORS_THRESHOLD_BEFORE_REBOOT'
        
        sms_processing_error = True
        try:
            sms_processed_status = self.__process_next_sms()
            sms_processing_error = False
            self.__update_balance_if_necessary()
 
        #except:
        #    debug("error occurred while trying to process sms: " + sys.exc_info()[0])
        
        finally:
            reboot_scheduled = False
 
            if sms_processing_error:
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
                debug("caught error number {} while trying to process next sms, scheduling reboot? {}.".format(new_error_count, schedule_reboot))
                
                if schedule_reboot:
                    with open(errors_threshold_file, 'w') as f:
                        self.__write_int_to_file(f, next_reboot_threshold) 
                    reboot_scheduled = True
                    return_code = subprocess.call(['/usr/bin/sudo', '/sbin/shutdown', '-r', 'now'], bufsize=-1, stderr=subprocess.STDOUT)
                    debug("reboot scheduled (return code:{}), next gammu error threshold is {} ...".format(return_code, next_reboot_threshold))

            else:
                os.remove(errors_file) if os.path.isfile(errors_file) else None
                os.remove(errors_threshold_file) if os.path.isfile(errors_threshold_file) else None

            reboot_interval_days = self.config['rebootIntervalDays']
            if not reboot_scheduled and reboot_interval_days > 0:
                max_uptime_seconds = reboot_interval_days * 24 * 60 * 60
                uptime_seconds = systeminfo.get_uptime_seconds()
                if uptime_seconds > max_uptime_seconds:
                    debug("current uptime {} exceeds max configured uptime {}, scheduling reboot.".format(uptime_seconds, max_uptime_seconds))
                    subprocess.call(['/usr/bin/sudo', '/sbin/shutdown', '-r', 'now'], bufsize=-1, stderr=subprocess.STDOUT)


    def __read_file_and_parse_first_int(self, f):
        first_line = f.readlines()[0]
        return int(first_line)
       
    def __write_int_to_file(self, f, int_value):
        f.write(str(int_value))
 

    def __process_next_sms(self):
        signal_strength_percentage = '--'
        time_before_fetch = time.time()
        try:
            sms_fetcher = SmsFetcher(self.config['gammuConfigFile'], self.config['gammuConfigSection'], self.config['logDir'] + '/sms-delete.log') 
            signal_strength_percentage = sms_fetcher.get_signal_strength_percentage()
            sms_messages = sms_fetcher.delete_get_next_sms()
        except (gammu.ERR_TIMEOUT, gammu.ERR_DEVICENOTEXIST, gammu.ERR_NOTCONNECTED):
            timeout_after_time = time.time() - time_before_fetch
            debug("Got exception after {} seconds while trying to fetch/delete next sms (signalStrength: {}%).".format(timeout_after_time, signal_strength_percentage))
            raise # re-raise exception so we get the stacktrace to stderr
        
        absolute_script_path = os.path.abspath(__file__)
        
        if not sms_messages:
            # would write a log message every minute even if no sms found 
            #debug("No sms found by {} - bye.".format(absolute_script_path))
            return TemperatureController.NO_SMS_FOUND
        
        debug("Start sms processing (found {} messages) by {}".format(len(sms_messages), absolute_script_path))
        
        sms = sms_messages[0]
        
        # set system datetime to sent/received DateTime from received sms if delta is big enough
        if self.config['systemDatetimeMaxDiffNoUpdateSeconds'] > 0:
            system_datetime = datetime.now()
            sms_datetime_naive = sms[0]['DateTime']
            delta_datetime = sms_datetime_naive - system_datetime
            delta_seconds = delta_datetime.total_seconds()
            if abs(delta_seconds) > self.config['systemDatetimeMaxDiffNoUpdateSeconds']:
                # example unix date: Thu Nov 28 23:29:53 CET 2014
                sms_datetime_unix = sms_datetime_naive.strftime("%a %b %d %H:%M:%S %Y")
                set_date_cmd = "date -s \"{0}\" > /dev/null".format(sms_datetime_unix)
                debug("Updating system datetime (delta: {} seconds) using cmd: {}".format(delta_seconds, set_date_cmd))
                os.system(set_date_cmd)
            #else:
        	#debug("system date diff ({} seconds) is not greater than configured delta ({} seconds), skipping updating.".format(delta_seconds, self.config['systemDatetimeMaxDiffNoUpdateSeconds']))
        
        now_string = datetime.now().strftime(DATETIME_FORMAT)
        
        sender_number = sms[0]['Number']
        sender_message_raw = sms[0]['Text']
        sender_message = repr(sender_message_raw)
        debug("  got sms message from {}: {}".format(sender_number, sender_message))
        
        if self.config['myNumber'] in sender_number:
            debug("  got sms from my own number - not responding in order to prevent infinite loop. Bye!")
            return TemperatureController.SMS_IGNORED
        elif self.config['blacklistSenders']: # empty strings are false in python
           for blacklist_sender in self.config['blacklistSenders'].split(","): 
                if len(blacklist_sender) > 0 and blacklist_sender in sender_number: 
                    debug("  this sender is in blacklist (matched '{}') - ignoring. Bye!".format(blacklist_sender))
                    return TemperatureController.SMS_IGNORED
        
        if len(sms_messages) > 1:
            debug("  found sms consisting of {} parts - only the first part will be considered.".format(len(sms_messages)))
        
        
        response_message = None
        
        if sender_message_raw and sender_message_raw.lower().startswith('temp'):
            temp_raw = temperaturereader.read_celsius()
            if temp_raw: 
                temp = round(temp_raw, 1)
                debug("  responding with temperature: {} Celsius.".format(temp))
                response_message = u'Hi! Current temperature here is {0} Celsius ({1}).'.format(temp, now_string)
            else:
                debug("  temperature could not be read.")
                response_message = u'Hi! Temperature sensor is offline, check log files.'
        
        elif sender_message_raw and sender_message_raw.lower().startswith('power'):
            requested_state = ''
            gpio_channels = [int(channel) for channel in self.config['relayGpioChannels'].split(',')]
            powerswitcher = PowerSwitcher(gpio_channels=gpio_channels)
            power_status_before = powerswitcher.get_status_string()
            if sender_message_raw.lower().startswith('power on'):
                requested_state = 'ON'
                powerswitcher.set_status_on()
                debug("  power has been set ON")
            elif sender_message_raw.lower().startswith('power off'):
                requested_state = 'OFF'
                powerswitcher.set_status_off()
                debug("  power has been set OFF")
        
            power_status = powerswitcher.get_status_string()
            
            debug("  responding with power status: {} (was: {}).".format(power_status, power_status_before))
            if requested_state:
                response_message = u'Hi! Power has been switched {0}, was {1} ({2}).'.format(power_status, power_status_before, now_string)
            else:
                response_message = u'Hi! Power is currently {0} ({1}).'.format(power_status, now_string)
        
        elif sender_message_raw and sender_message_raw.lower().startswith('systeminfo'):
            debug("  responding with system info:")
            up_since = systeminfo.get_last_reboot_date_time()
            kernelVersion = systeminfo.get_kernel_version()
            rpiSerialNumber = systeminfo.get_rpi_serial_number()
            localInetAddress = systeminfo.get_inet_address()
            gitRevision = systeminfo.get_git_revision()
            balance_info = self.__get_cached_balance_info(short=True)
            debug("    system datetime  : {}".format(now_string))
            debug("    up since         : {}".format(up_since))
            debug("    kernel version   : {}".format(kernelVersion))
            debug("    RPi serial       : {}".format(rpiSerialNumber))
            debug("    inet address     : {}".format(localInetAddress))
            debug("    git revision     : {}".format(gitRevision))
            debug("    Signal strength  : {}%".format(signal_strength_percentage))
            debug("    Balance          : {}".format(balance_info))
            response_message = u'Hi!\n sysTime: {0}\n uptime: {1}\n kernel: {2}\n serial: {3}\n inet: {4}\n gitRev: {5}\n signal: {6}%\n $$: {7}.'.format(now_string, up_since, kernelVersion, rpiSerialNumber, localInetAddress, gitRevision, signal_strength_percentage, balance_info)
        
        
        elif sender_message_raw and sender_message_raw.lower().startswith('checkbalance'):
            ussd = self.config['ussdCheckBalance']
            self.__update_balance_if_necessary(force=True)
            balance_info = self.__get_cached_balance_info()
            debug("  responding with USSD reply for {}:".format(ussd))
            debug("  " + balance_info.encode('ascii', 'replace'))
            response_message = u'Hi! Current balance info:\n{0}'.format(balance_info)

        else:
            debug("  not recognized, answering with help message.")
            response_message = u"Hi! 'temp' to get current temperature, 'power' (+' on'/' off') to get (change) power status. Other commands: 'systeminfo', 'checkbalance'."
        
        time_before_send = time.time()
        try:
            sms_sender = SmsSender(self.config['gammuConfigFile'], self.config['gammuConfigSection']) 
            sms_sender.send_sms(response_message, sender_number)
            return TemperatureController.SMS_PROCESSED
        except (gammu.ERR_UNKNOWN):
            timeout_after_time = time.time() - time_before_send
            debug("Got exception after {} seconds while trying to send sms.".format(timeout_after_time))
            raise # re-raise exception so we get the stacktrace to stderr


    def __update_balance_if_necessary(self, force=False):
        balance_file = self.config['workDir'] + '/LAST_BALANCE'
        ussd = self.config['ussdCheckBalance']
        balance_fetch_interval = self.config['balanceFetchInterval']
        can_do_check = True and ussd
        do_check = force or not os.path.exists(balance_file)
        if os.path.exists(balance_file):
            last_updated_time = datetime.fromtimestamp(os.path.getctime(balance_file))
            do_check = do_check or (balance_fetch_interval > 0 and (last_updated_time < datetime.now() - timedelta(days=balance_fetch_interval)))
            if (not can_do_check) or do_check:
                os.remove(balance_file)

        if can_do_check and do_check:
            debug("Updating cached balance (force={}) using USSD code '{}' ...".format(force, ussd))
            ussd_fetcher = UssdFetcher(self.config['gammuConfigFile'], self.config['gammuConfigSection'])
            reply_raw = ussd_fetcher.fetch_ussd_reply_raw(ussd)
            with open(balance_file, 'w') as f:
                if reply_raw is not None:
                    f.write(reply_raw)
            debug("done.")


    def __get_cached_balance_info(self, short=False):
        balance_file = self.config['workDir'] + '/LAST_BALANCE'
        if os.path.isfile(balance_file):
            ussd_fetcher = UssdFetcher(self.config['gammuConfigFile'], self.config['gammuConfigSection'])
            with open(balance_file, 'r') as f:
                file_content = f.read()
                reply_unicode = ussd_fetcher.convert_reply_raw_to_unicode(file_content)
                balance_regex_raw = self.config['balanceInfoRegex']
                if not balance_regex_raw:
                    return reply_unicode
                balance_regex = re.compile(balance_regex_raw, flags=re.UNICODE|re.MULTILINE)
                match = re.search(balance_regex, reply_unicode)

                if match:
                    if short and match.groups():
                        return match.group(1)
                    else:
                        return match.group(0)
 
        return None


# ------------------------------------------------------------------------------- #

def debug(message):
    print("{:>9}  {}".format(os.getpid(), message))
    sys.stdout.flush()
  

# How to run this method from command-line:
#  python -c 'from process_sms import test; test()'
#
def test():
    debug("welcome to test()")
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read('/home/pi/sms-temperature-control/my.cfg')

    tc = TemperatureController(config_parser)


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
            debug("START no other pid found for this script (PID: {}), going ahead with sms processing...".format(pgrep_pids))
            temperature_controller = TemperatureController(config_parser)
            temperature_controller.run()
            debug("DONE sms processing.")
        else:
            debug("Found other processes already running this script (PIDs: {}), skipping this script run.".format(pgrep_pids))

    else:
        debug("Uptime ({0} seconds) is less than {1} seconds, skipping sms processing.".format(uptime, uptime_threshold))
