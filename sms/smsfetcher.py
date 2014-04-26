#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gammu
import sys
import datetime


GAMMU_CONFIG_PATH='/home/pi/.gammurc'


def delete_get_next_sms():
    return get_next_sms(True)


def get_next_sms(delete_message):

    # Create object for talking with phone
    sm = gammu.StateMachine()

    # Optionally load config file as defined by first parameter
    if len(sys.argv) >= 2:
        # Read the configuration from given file
        sm.ReadConfig(Filename = sys.argv[1])
        # Remove file name from args list
        del sys.argv[1]
    else:
        # Read the configuration ('~/.gammurc' if not specified)
        sm.ReadConfig(Filename = GAMMU_CONFIG_PATH)

    # Connect to the phone
    sm.Init()

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
                    sender_message = repr(sms[0]['Text'])
                    sms_log_file.write('\n' + now_text);
                    sms_log_file.write(separator + received_timestamp);
                    sms_log_file.write(separator + sender_number);
                    sms_log_file.write(separator + sender_message);
                sm.DeleteSMS(deleteSms['Folder'], deleteSms['Location'])
            else:
                print "DeleteSMS is commented out but would happen right here!"

            deletedSms.append(sms)

        # comment this to go through all sms instead of the first one only
        return deletedSms




if __name__ == "__main__":
    next_sms = get_next_sms(False)
    print "found next sms: {0}".format(next_sms)

