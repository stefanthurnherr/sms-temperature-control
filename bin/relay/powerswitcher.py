#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO


# GPIO.BCM: use GPIO numbering
# GPIO.BOARD: use board numbering
GPIO_MODE = GPIO.BCM
DEFAULT_CHANNEL_BCM_ID = 22

class PowerSwitcher(object):
    def __init__(self, gpio_channels=[DEFAULT_CHANNEL_BCM_ID], warnings=False):
        self.gpio_channels = gpio_channels
        
        GPIO.setmode(GPIO_MODE)
        GPIO.setwarnings(warnings)
       
        for channel_id in gpio_channels: 
            GPIO.setup(channel_id, GPIO.OUT)
        
        #self.set_status_off()


    def is_status_off(self):
        return not self.is_status_on()


    def is_status_on(self):
        return self.__get_status() == 0

 
    def get_status_string(self):
        return 'ON' if self.is_status_on() else 'OFF'


    def set_status_on(self):
        if self.__get_status() == 1:
            self.__set_channel_value_to(GPIO.LOW)


    def set_status_off(self):
        if self.__get_status() == 0:
            self.__set_channel_value_to(GPIO.HIGH)


    def tear_down(self):
        for channel_id in self.gpio_channels:
            GPIO.cleanup(channel_id)


    def __get_status(self):
        return GPIO.input(self.gpio_channels[0])


    def __set_channel_value_to(self, gpioValue):
        for channel_id in self.gpio_channels:
            GPIO.output(channel_id, gpioValue)
        return self.__get_status()


if __name__ == "__main__":

    ps = PowerSwitcher(warnings=True, gpio_channels=[22,23])

    print("initial value is {0}".format(ps.get_status_string()))

    intervalSeconds = 5
    iteration = 1
    max_iteration = 3
    while iteration <= max_iteration:
        print("iteration {0}/{1}".format(iteration, max_iteration))
        ps.set_status_on()
        print("  set to on - value now is {0}".format(ps.get_status_string()))
        time.sleep(intervalSeconds)
        ps.set_status_off()
        print("  set to off - value now is {0}".format(ps.get_status_string()))
        if iteration < max_iteration:
            time.sleep(intervalSeconds)
        iteration = iteration + 1

    ps.tear_down()
