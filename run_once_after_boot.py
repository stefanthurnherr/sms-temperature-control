#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from relay import powerswitcher

powerswitcher.init_pins()
power_status = powerswitcher.get_status_string_safe()

now = datetime.datetime.now()
now_text = now.strftime("%Y-%m-%d %H:%M:%S")

print "{0} Successfully initialized pins after boot, power is now {1}.".format(now_text, power_status)
