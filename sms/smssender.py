#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gammu


GAMMU_CONFIG_PATH = '/home/pi/.gammurc'


def send_sms(text, number):

    SMS = {
        'Class': 1,                #SMS Class
        'Text': text,              #Message
        'SMSC': {'Location': 1},
        'Number': number,          #The phone number
    }

    gammu_sm = gammu.StateMachine()
    gammu_sm.ReadConfig(Filename = GAMMU_CONFIG_PATH)
    gammu_sm.Init()                    #Connect to the phone
    gammu_sm.SendSMS(SMS)              #Send the SMS



if __name__ == "__main__":
    hello_text = "Raspberry Pi says: Hi! (a gammu-python test sms)"
    number = <insert-sender-mobile-number-here> 
    send_sms(hello_text, number)

