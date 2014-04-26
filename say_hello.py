#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import getpass


now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

absoluteFilePath = os.path.abspath(__file__)

print "{0} Hello Cron World! (says {1} at {2})".format(now_text, getpass.getuser(), absoluteFilePath)

