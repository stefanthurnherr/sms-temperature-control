How to get started
==================

Required hardware
-----------------
* Raspberry Pi with an sd card (4GB) and running raspbian image
* Temperature sensor
* Some cables, breadboard, resistances, LEDs (for testing purposes), multimeter
* relay (controlled by 5V connection, able to handle 220V circuit)
* 3G usb modem with valid SIM card
* USB hub (powered)


Initial setup
-------------
    #install gammu (python library to send/read sms)
    sudo apt-get install gammu

    # install some kernel modules required for temp sensor and 3G usb stick
    sudo modprobe w1_gpio
    sudo modprobe w1_therm
    sudo modprobe usbserial
    # or add permanently to /etc/modules

    # add python script to root crontab (root is required to read/write GPIO channels)
    # sudo crontab -e
    # */15 * * * * /usr/bin/python /home/pi/sms-temperature-control/say_hello.py >> /tmp/crontab.stdout 2>&1
    # */01 * * * * /usr/bin/python /home/pi/sms-temperature-control/process_sms.py >> /tmp/crontab.stdout 2>&1
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


