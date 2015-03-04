#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO


# GPIO.BCM: use GPIO numbering
# GPIO.BOARD: use board numbering
GPIO_MODE = GPIO.BCM
CHANNEL_BCM_ID = 22

class PowerSwitcher(object):
    def __init__(self, gpio_ids=[CHANNEL_BCM_ID], warnings=False):
        self.gpio_ids = gpio_ids
        
        GPIO.setmode(GPIO_MODE)
        GPIO.setwarnings(warnings)
        GPIO.setup(CHANNEL_BCM_ID, GPIO.OUT)
        
        self.set_status_off()

 
    def get_status_string(self):
        power_status = self.__get_status()
        if power_status == 1:
            return 'OFF'
        else:
            return 'ON'


    def set_status_on(self):
        if self.__get_status() == 1:
            self.__set_channel_value_to(GPIO.LOW)


    def set_status_off(self):
        if self.__get_status() == 0:
            self.__set_channel_value_to(GPIO.HIGH)


    def tear_down(self):
        GPIO.cleanup(CHANNEL_BCM_ID)


    def __get_status(self):
        return GPIO.input(CHANNEL_BCM_ID)


    def __set_channel_value_to(self, gpioValue):
        GPIO.output(CHANNEL_BCM_ID, gpioValue)
        return self.__get_status()


if __name__ == "__main__":

    ps = PowerSwitcher(warnings=True)

    print "initial value is {0}".format(ps.get_status_string())

    intervalSeconds = 5
    iteration = 1
    max_iteration = 3
    while iteration <= max_iteration:
        print "iteration {0}/{1}".format(iteration, max_iteration)
        ps.set_status_on()
        print "  set to on - value now is {0}".format(ps.get_status_string())
        time.sleep(intervalSeconds)
        ps.set_status_off()
        print "  set to off - value now is {0}".format(ps.get_status_string())
        time.sleep(intervalSeconds)
        iteration = iteration + 1

    ps.tear_down()
