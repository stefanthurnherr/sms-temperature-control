#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import glob
import os
import getpass
import ConfigParser


now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

absoluteFilePath = os.path.abspath(__file__)

config = ConfigParser.SafeConfigParser()
config.read('/home/pi/sms-temperature-control/my.cfg')
phoneNumber = config.get('Phone', 'number')

print("{0} Hello Cron World! (says {1} at {2} with mobile number {3})".format(now_text, getpass.getuser(), absoluteFilePath, phoneNumber))

work_dir = config.get('System', 'work_dir')
print("work dir has following lock files:")
print(glob.glob(work_dir + '/.lock*'))
