#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gammu


def get_init_state_machine(gammu_config_file, gammu_config_section):
    gammu_sm = gammu.StateMachine()
    gammu_sm.ReadConfig(Section = int(gammu_config_section), Filename = gammu_config_file)
    gammu_sm.Init()
    return gammu_sm


if __name__ == "__main__":
    print "Helper class, not intended to be called directly."
    
