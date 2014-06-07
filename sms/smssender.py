#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gammu
import ConfigParser
import _gammuhelper


def send_sms(text, number):

    SMS = {
        'Class': 1,                #SMS Class
        'Text': text,              #Message
        'SMSC': {'Location': 1},
        'Number': number,          #The phone number
    }

    gammu_sm = _gammuhelper.get_init_state_machine()
    
    gammu_sm.SendSMS(SMS)



if __name__ == "__main__":
    hello_text = "Raspberry Pi says: Hi! (a gammu-python test sms)"
    
    config = ConfigParser.SafeConfigParser()
    config.read('my.cfg')
    phone_number = config.get('Phone', 'number')
    
    send_sms(hello_text, phone_number)

