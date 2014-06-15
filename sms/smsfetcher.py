#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime

import _gammuhelper


class SmsFetcher(object):
    def __init__(self, gammu_config_file, gammu_config_section):
	self.gammu_state_machine = _gammuhelper.get_init_state_machine(gammu_config_file, gammu_config_section)

    def get_signal_strength_percentage(self):
        return _gammuhelper.get_signal_strength_percentage(self.gammu_state_machine)

    def delete_get_next_sms(self):
        return self.get_next_sms(True)

    def get_next_sms(self, delete_message):
        sm = self.gammu_state_machine

        # Get sms status
        smsStatus = sm.GetSMSStatus()
        unreadSms = smsStatus['SIMUsed'] + smsStatus['PhoneUsed']
        #print "found", unreadSms, "unread sms in smsStatus:", smsStatus

        deletedSms = []

        start = True
        unreadSmsLeft = unreadSms
        while unreadSmsLeft > 0:
            if start:
                sms = sm.GetNextSMS(Start = True, Folder = 0)
                start = False
            else:
                sms = sm.GetNextSMS(Location = sms[0]['Location'], Folder = 0)
            unreadSmsLeft = unreadSmsLeft - len(sms)
            #print 'read sms #', (unreadSms - unreadSmsLeft), ': ',  sms

            for i,deleteSms in enumerate(sms):
                if delete_message:
                    with open('/home/pi/sms-temperature-control/log/sms-delete.log', 'a') as sms_log_file:
                        separator = '   '
                        now_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        received_timestamp = sms[0]['DateTime'].strftime("%Y-%m-%d %H:%M:%S")
                        sender_number = sms[0]['Number']
                        sender_number = sender_number.rjust(15) 
		        sender_message = repr(sms[0]['Text'])
                        sms_log_file.write('\n' + now_text);
                        sms_log_file.write(separator + received_timestamp);
                        sms_log_file.write(separator + sender_number);
                        sms_log_file.write(separator + sender_message);
                    sm.DeleteSMS(deleteSms['Folder'], deleteSms['Location'])
                else:
                    print "DeleteSMS is disabled but would happen right here!"

                deletedSms.append(sms)

            # comment this to go through all sms instead of the first one only
            return deletedSms




if __name__ == "__main__":
    gammu_config_file = '/home/pi/.gammurc'
    gammu_config_section = 4
    print "Fetching sms based on section {1} of gammu config at {0} ...".format(gammu_config_file, gammu_config_section) 
    sms_fetcher = SmsFetcher(gammu_config_file, gammu_config_section)
    next_sms = sms_fetcher.get_next_sms(False)
    print "found next sms: {0}".format(next_sms)

