How to get started
==================

Required hardware
-----------------
* Raspberry Pi with an sd card (I recommend at least 4GB) and running raspbian image
* Temperature sensor (I used DS18B20 with cable and waterproof)
* Some cables, breadboard, resistances, LEDs (for testing purposes), multimeter
* Relay (I used a [5V AC250V10A 1-channel relay module](http://www.ebay.com/itm/5V-One-1-Channel-Relay-Module-Board-Shield-For-PIC-AVR-DSP-ARM-MCU-Arduino-MKLP-/251804970941?pt=LH_DefaultDomain_0&hash=item3aa0beefbd))
* GSM/3G usb modem, unlocked (I used [gsmliberty.net](http://www.gsmliberty.net) to unlock mine)
* valid SIM card (prepaid, preferably refillable via internet)
* Powered USB hub ([I used this 4-port hub from i-tec](http://www.i-tec-europe.eu/?t=3&v=265&lng=en), product number U2HUB412: small size and delivers enough current to power the RPi)
* Maybe some angled USB cables to save some space when packaging the whole thing (I bought one [here](http://www.angledcables.com/cables.html))
* A rasp and a drilling machine to make the holes for the cables
* Power cable with male and female plug; cable will be cut in half to put the relay in between

Initial hardware setup
----------------------
* Connect the temperature sensor to Pi pins 3V3/GND/GPIO4 with a 'pullup' resistor of 4K7 Ohm. Adafruit.com has a nice tutorial [here](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware). My temperature sensor has cable colors red=3V3, black=GND and white=DATA.


Initial software setup
----------------------
    #install gammu (python library to send/read sms)
    sudo apt-get install gammu python-gammu

    # install some kernel modules required for temp sensor and 3G usb stick
    sudo modprobe w1_gpio
    sudo modprobe w1_therm
    sudo modprobe usbserial
    # or better yet: add permanently to /etc/modules

    # generate a gammu configuration and store it into .gammurc in home dir (usb modem must be connected)
    gammu-detect > ~/.gammurc

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
    gammu getsecuritystatus

    # enter PIN
    gammu entersecuritycode PIN -

    # phone info
    gammu identify

    # send sms
    echo "sms content" | gammu sendsms TEXT +1234567890 # mobile number in international format

How to install a python module
------------------------------
    # example description see this url:
    # http://openmicros.org/index.php/articles/94-ciseco-product-documentation/raspberry-pi/217-getting-started-with-raspberry-pi-gpio-and-python#3

    # install python-dev and python-pip (pip install gcc amongst others)
    # sudo apt-get install python-dev python-pip

    # download python sources for module, e.g.:
    # wget https://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.5.5.tar.gz

    # untar sources

    # enter the extracted module directory

    # run this to install python module:
    # sudo python setup.py install
    # (alternative: sudo pip install rpi.gpio)

Screenshots of my temperature control box
-----------------------------------------
Assembled box without top cover: ![ScreenShot](/screenshots/readme-openbox.jpg)
Final version of the box: ![ScreenShot](/screenshots/readme-closedbox.jpg)

Ideas to be implemented in the future
-------------------------------------
* Use gammu's USSD interface to warn Administrator if balance (for prepaid SIM cards) is low
