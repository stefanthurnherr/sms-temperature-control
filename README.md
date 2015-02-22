ow to get started
==================

Required hardware
-----------------
* Raspberry Pi with an SD card (I recommend 8GB) and running raspbian image
* Temperature sensor (I used DS18B20 with cable and waterproof)
* Some cables, breadboard, resistances, LEDs (for testing purposes), multimeter
* Relay (I used a [5V AC250V10A 1-channel relay module](http://www.ebay.com/itm/5V-One-1-Channel-Relay-Module-Board-Shield-For-PIC-AVR-DSP-ARM-MCU-Arduino-MKLP-/251804970941?pt=LH_DefaultDomain_0&hash=item3aa0beefbd))
* GSM/3G USB modem, unlocked (I used [gsmliberty.net](http://www.gsmliberty.net) to unlock mine)
* valid SIM card (prepaid, preferably refillable via internet)
* Powered USB hub ([I used this 4-port hub from i-tec](http://www.i-tec-europe.eu/?t=3&v=265&lng=en), product number U2HUB412: small size and delivers enough current to power the RPi)
* Maybe some angled USB cables to save some space when packaging the whole thing (I bought one [here](http://www.angledcables.com/cables.html))
* A rasp and a drilling machine to make the holes for the cables
* Power cable with male and female plug; cable will be cut in half to put the relay in between

Initial hardware setup
----------------------
* Connect the temperature sensor to correct power/ground/data pins on the Pi using a 'pullup' resistor of 4K7 Ohm. See sensor specification and my corresponding python script. Adafruit.com also has a nice tutorial [here](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware). My temperature sensor has cable colors red=3V3, black=GND and white=DATA.
* Connect the relay to the correct Pi pins - check with specification and my corresponding python script


Initial software setup
----------------------
    # uninstall some useless/non-required packages
    > sudo apt-get remove --purge wolfram-engine
    
    # update RPi to latest and greatest
    > sudo apt-get update
    > sudo apt-get upgrade
    # and if you want to run latest RPi (nightly) builds:
    > sudo rpi-update

    #install gammu (python library to send/read sms)
    > sudo apt-get install gammu python-gammu

    # if you want to use an USB Ethernet adapter to connect to the RPi
    #  (for updating, configuring, debugging etc), then
    #  ensure that you have the following lines in /etc/network/interfaces :
    # allow-hotplug ethX
    # iface ethX inet dhcp 

    # Enable 1-wire support (for DS18B20 temperature sensor):
    #  For newer kernels >= 3.18.5):
    #   ensure following lines appear in your /boot/config.txt :
    device_tree=bcm2708-rpi-b-plus.dtb #for RPi A+/B+
    device_tree_overlay=overlays/w1-gpio-overlay.dtb
    #  For older kernels:
    #   ensure the following lines appear in your /etc/modules :
    w1_gpio
    w1_therm

    # ensure that the following module is listed in /etc/modules :
    usbserial

    # at this point restart if you haven't done so yet:
    > sudo shutdown -r now

    # generate a gammu configuration and store it into .gammurc in home dir (usb modem must be connected)
    > gammu-detect > ~/.gammurc

    # if not yet done: generate an ssh key pair
    > ssh-keygen -t rsa -C "your_email@example.com"
    # now clone this git repository into the pi home folder
    > cd
    > git clone git@github.com:stefanthurnherr/sms-temperature-control.git

    # go through config file at sms-temperature-control/my.cfg and adjust as needed

    # add python script to root crontab (root is required to read/write GPIO channels)
    # sudo crontab -e
    # */15 * * * * /usr/bin/python /home/pi/sms-temperature-control/say_hello.py >> /home/pi/sms-temperature-control/log/crontab.stdout 2>&1
    # */01 * * * * /usr/bin/python /home/pi/sms-temperature-control/process_sms.py >> /home/pi/sms-temperature-control/log/crontab.stdout 2>&1
    # @reboot      /usr/bin/python /home/pi/sms-temperature-control/run_once_after_boot.py >> /home/pi/sms-temperature-control/log/bootsetup.stdout 2>&1
    #
    # .---------------- minute (0 - 59) 
    # |  .------------- hour (0 - 23)
    # |  |  .---------- day of month (1 - 31)
    # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ... 
    # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7)  OR sun,mon,tue,wed,thu,fri,sat 
    # |  |  |  |  |
    # *  *  *  *  *  command to be executed
    #


Some helpful commands when trying out gammu
-------------------------------------------
    # waiting for PIN?
    > gammu getsecuritystatus

    # enter PIN
    > gammu entersecuritycode PIN -

    # phone info
    > gammu identify

    # send sms
    > echo "sms content" | gammu sendsms TEXT +1234567890 # mobile number in international format

    # send USSD code (to check sim card balance etc.) - I never got this to work with my USB dongle::
    > gammu -c ${HOME}/.gammurc.cfg getussd '*100#'


Screenshots of one of my boxes
------------------------------
Assembled box without top cover: ![ScreenShot](/screenshots/readme-openbox.jpg)
Final version of the box: ![ScreenShot](/screenshots/readme-closedbox.jpg)


Ideas to be implemented in the future
-------------------------------------
* Use gammu's USSD interface to warn Administrator if balance (for prepaid SIM cards) is low


How to install a python module
------------------------------
The current Raspian distribution has all required python modules installed by default, so this shouldn't be necessary. But I've kept it here for future reference.

    # example description see this url:
    # http://openmicros.org/index.php/articles/94-ciseco-product-documentation/raspberry-pi/217-getting-started-with-raspberry-pi-gpio-and-python#3

    # install python-dev and python-pip (pip install gcc amongst others)
    > sudo apt-get install python-dev python-pip

    # download python sources for module, e.g.:
    > wget https://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.5.5.tar.gz

    # untar sources

    # enter the extracted module directory

    # run this to install python module:
    > sudo python setup.py install
    # (alternative: sudo pip install rpi.gpio)
