#!/usr/bin/python
# -*- coding: utf-8 -*-

import gammu
import sys


# Create state machine object
sm = gammu.StateMachine()

# Read ~/.gammurc
sm.ReadConfig()

# Connect to phone
sm.Init()

# Reads network information from phone
dateTimeInfo = sm.GetDateTime()

# Print information
print 'Current network date/time: %s' % dateTimeInfo

print 'Bye!'
