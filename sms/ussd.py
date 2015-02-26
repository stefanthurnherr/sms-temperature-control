#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gammu
import subprocess


#
# from http://stackoverflow.com/questions/16554899/gammu-check-balance-using-getussd-is-encrypted
#
def __chunks(l, n):
  for i in range(0, len(l), n):
    yield l[i:i+n]
def decode_ussd_response(ussd_response):
    response = []
    for chunk in list(__chunks(ussd_response, 4)):
        response.append(chr(int(chunk[2:],16)))
        #print chr(int(chunk[2:],16)), # print and end with empty string instead of newline
    return ''.join(response)


if __name__ == "__main__":
    
    ussd = '*111#'
    print "Trying to call USSD code {0} ...".format(ussd)

    config_file = '/home/pi/.gammurc'
    config_section = 2

    gammu_sm = gammu.StateMachine()
    gammu_sm.ReadConfig(Section = config_section, Filename = config_file)
    gammu_sm.Init(Replies=1)
    
    #return_code = subprocess.call(['gammu', '-c', config_file, '-s', str(config_section), 'getussd', ussd], bufsize=-1, stderr=subprocess.STDOUT)
    response = subprocess.check_output(['gammu', '-c', config_file, '-s', str(config_section), 'getussd', ussd])
    print "completed gammu ussd call, got:"
    print response
    
    #response = "0053004D0053003A006100200030003500470042002000740069006C006C00200031003300330020007300E50020006B0061006E00200064007500200073007500720066006100200030002C003500470042002000690020003300300020006400610067006100720020006600F6007200200065006E00640061007300740020003300300020006B0072002E000A00530041004C0044004F003A002000340036002C003300380020006B0072000A00500072006900730070006C0061006E003A0020005300740061006E0064006100720064"

    print "service reply parsed is:"
    if "Service reply" in response:
        lines = response.splitlines()
        for line in lines:
            if line.startswith('Service reply'):
                hex_response = line[line.find('0'):-1]
                print hex_response.decode("hex")


    print "Done, bye." 
