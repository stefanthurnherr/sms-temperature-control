#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from temp import temperaturereader


while True:
    print(temperaturereader.read_celsius())
    time.sleep(5)

