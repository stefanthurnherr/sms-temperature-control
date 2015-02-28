#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys

import _gammuhelper


class SmsSender(object):
    def __init__(self, gammu_config_file, gammu_config_section):
        self.gammu_state_machine = _gammuhelper.get_init_state_machine(gammu_config_file, gammu_config_section)

    def send_sms(self, text, number):
        SMS = {
            'Class': 1,                #SMS Class
            'Unicode': True,
            'Text': text,              #Message
            'SMSC': {'Location': 1},
            'Number': number,          #The phone number
        }
        self.gammu_state_machine.SendSMS(SMS)


    # doesnt work, might need a text of a certain length?
    def send_multi_sms(self, text, number):
        smsinfo = {
            'Class': 1,
            'Unicode': True,
            'Entries':  [
                {
                    'ID': 'ConcatenatedTextLong',
                    'Buffer': text
                }
            ]}

        # Encode messages
        encoded = _gammuhelper.encode_sms(smsinfo)

        for sms in encoded:
            sms['SMSC'] = {'Location': 1}
            sms['Number'] = number
            self.gammu_state_machine.SendSMS(sms)


    def get_network_datetime(self):
        return self.gammu_state_machine.GetDateTime()


if __name__ == "__main__":
    hello_text = "Raspberry Pi says: Hi! (a gammu-python test sms)"

    phone_number = ''
    if len(sys.argv) >= 2:
        phone_number = sys.argv[1]
        del sys.argv[1]

    if not phone_number:
        print "Valid receiver phone number must be specified as the first argument - bye!" 
        sys.exit() 

    print "Sending following message as SMS to {0}".format(phone_number)
    print " {0}".format(hello_text)

    sms_sender = SmsSender('/home/pi/.gammurc', 1)
    sms_sender.send_sms(hello_text, phone_number)
    print "Successfully sent sms - bye!"
