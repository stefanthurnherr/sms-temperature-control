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
netinfo = sm.GetNetworkInfo()

# Print information

print 'Network arrak: %s' % netinfo
print 'Network name: %s' % netinfo['NetworkName']
print 'Network code: %s' % netinfo['NetworkCode']
print 'LAC: %s' % netinfo['LAC']
print 'CID: %s' % netinfo['CID']

print 'Bye!'
