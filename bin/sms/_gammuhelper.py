#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gammu


GAMMU_DEBUG_LEVEL='textall'

def get_init_state_machine(gammu_config_file, gammu_config_section):
    #gammu.SetDebugFile('/home/pi/sms-temperature-control/log/gammu-debug.out') 
    #gammu.SetDebugLevel(GAMMU_DEBUG_LEVEL) 
    gammu_sm = gammu.StateMachine()
    gammu_sm.ReadConfig(Section = int(gammu_config_section), Filename = gammu_config_file)
    gammu_sm.Init(Replies=1)
    return gammu_sm

def encode_sms(smsinfo):
    return gammu.EncodeSMS(smsinfo)

def get_signal_strength_percentage(gammu_state_machine):
    signal_quality = gammu_state_machine.GetSignalQuality()
    return signal_quality['SignalPercent']


if __name__ == "__main__":
    print("Helper class, not intended to be called directly.")
    
