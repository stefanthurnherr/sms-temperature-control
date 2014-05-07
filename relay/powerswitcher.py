#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO


# GPIO.BCM: use GPIO numbering
# GPIO.BOARD: use board numbering
GPIO_MODE = GPIO.BCM
CHANNEL_BCM_ID = 22


def init_pins(warnings=False):
    setup(warnings)
    set_status_off()

def get_status_string_safe(warnings=False):
    setup(warnings) 
    return get_status_string()

def set_status_on_safe(warnings=False):
    setup(warnings) 
    if get_status() == 1:
        set_status_on()

def set_status_off_safe(warnings=False):
    setup(warnings) 
    if get_status() == 0:
        set_status_off()

#private
def setup(warnings=True):
    GPIO.setmode(GPIO_MODE)
    GPIO.setwarnings(warnings)
    GPIO.setup(CHANNEL_BCM_ID, GPIO.OUT)

#private
def tear_down():
    GPIO.cleanup(CHANNEL_BCM_ID)

#private
def get_status():
    return GPIO.input(CHANNEL_BCM_ID)

#private
def get_status_string():
    power_status = get_status()
    if power_status == 1:
        return 'OFF'
    else:
        return'ON'

#private
def set_status_on():
    return set_channel_value_to(GPIO.LOW)

#private
def set_status_off():
    return set_channel_value_to(GPIO.HIGH)

#private
def set_channel_value_to(gpioValue):
    GPIO.output(CHANNEL_BCM_ID, gpioValue)
    return get_status()


if __name__ == "__main__":

    setup()

    print "initial value is {0}".format(get_status())

    intervalSeconds = 5
    iteration = 0
    max_iteration = 3
    while iteration < max_iteration:
        print "iteration {0}/{1}".format(iteration, max_iteration)
        set_status_on()
        print "  set to on - value now is {0}".format(get_status())
        time.sleep(intervalSeconds)
        set_status_off()
        print "  set to off - value now is {0}".format(get_status())
        time.sleep(intervalSeconds)
        iteration = iteration + 1

    tear_down()
