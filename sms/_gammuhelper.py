#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gammu
import ConfigParser


GAMMU_CONFIG_PATH = '/home/pi/.gammurc'


def get_init_state_machine():
    gammu_sm = gammu.StateMachine()
    gammu_sm.ReadConfig(Filename = GAMMU_CONFIG_PATH)
    gammu_sm.Init()                    #Connect to the phone
    return gammu_sm


if __name__ == "__main__":
    print "Helper class, not intended to be called directly."
    
