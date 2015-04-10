#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import sys


class UssdFetcher(object):
    def __init__(self, gammu_config_file, gammu_config_section):
        self.gammu_config_file = gammu_config_file
        self.gammu_config_section = gammu_config_section
        self.reply_encoding = 'latin1'

    def fetch_ussd_reply_raw(self, ussd):
        config_file = self.gammu_config_file
        config_section = self.gammu_config_section
        response = subprocess.check_output(['gammu', '-c', config_file, '-s', config_section, 'getussd', ussd])
        if u'Service reply' in response:
            for line in response.splitlines():
                if line.startswith(u'Service reply'):
                    service_reply_raw = line[line.find('"')+1:-1]
                    return self.__remove_zero_padding_from_reply_raw(service_reply_raw)
        return None


    def __remove_zero_padding_from_reply_raw(self, reply_raw):
        padded_unicode = self.convert_reply_raw_to_unicode(reply_raw)
        unpadded_unicode = padded_unicode.replace('\0', '')
        return self.convert_reply_unicode_to_raw(unpadded_unicode)

 
    def convert_reply_raw_to_unicode(self, reply_raw):
        if reply_raw is None:
            return reply_raw
        reply_unicode = reply_raw.decode('hex').decode(self.reply_encoding)
        return reply_unicode


    def convert_reply_unicode_to_raw(self, reply_unicode):
        if reply_unicode is None:
            return return_unicode
        reply_raw = reply_unicode.encode(self.reply_encoding).encode('hex')
        return reply_raw


if __name__ == "__main__":

    #ussd = '*111#'
    ussd = '#121#'
    print("Trying to call USSD code {0} ...".format(ussd))

    config_file = '/home/pi/.gammurc'
    config_section = '2'

    ussd_fetcher = UssdFetcher(config_file, config_section)
    reply_raw = ussd_fetcher.fetch_ussd_reply_raw(ussd)
    print("completed gammu ussd call, got:")
    print(reply_raw)

    print("type (raw) is: {0}.".format(type(reply_raw)))

    if reply_raw is not None:
        reply_unicode = ussd_fetcher.convert_reply_raw_to_unicode(reply_raw)
        print("type (unicode) is: {0}.".format(type(reply_unicode)))
        print("ASCII-decoded reply (with non-ASCII characters replaced) is:")
        print(reply_unicode.encode('ascii', 'replace')) # remember: python default encoding is 'ascii'

        #reply_raw = "0053004D0053003A006100200030003500470042002000740069006C006C00200031003300330020007300E50020006B0061006E00200064007500200073007500720066006100200030002C003500470042002000690020003300300020006400610067006100720020006600F6007200200065006E00640061007300740020003300300020006B0072002E000A00530041004C0044004F003A002000340036002C003300380020006B0072000A00500072006900730070006C0061006E003A0020005300740061006E0064006100720064"

    print('Done, bye')
