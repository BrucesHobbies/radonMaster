#!/usr/bin/env python

"""
Copyright(C) 2020, BrucesHobbies
All Rights Reserved

AUTHOR: Bruce
DATE: 12/1/2020
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------


LICENSE:
    This program code and documentation are for personal private use only. 
    No commercial use of this code is allowed without prior written consent.

    This program is free for you to inspect, study, and modify for your 
    personal private use. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

GENERAL INFORMATION:
  <https://cryptography.io/en/latest/fernet/>

"""

from cryptography.fernet import Fernet

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print("Error: import json module failed")
        sys.exit()

encoding = 'utf-8'

cfgDataFileName = 'cfgData.json'


cfgData = {
    u"token": "",
    u"key": "",
    u"GMAIL_USER": "",
    u"TO": ""
}


def cfgData_set(var, value):
    cfgData[var] = value
    with open(cfgDataFileName, 'w') as cfgDataFile:
        json.dump(cfgData, cfgDataFile)


def cfgData_get(var):
    return cfgData[var]


def password_key():
     key = Fernet.generate_key()
     return key.decode(encoding)


def password_encrypt(phrase):
    key = Fernet(bytes(cfgData['key'],encoding))
    token = key.encrypt(bytes(phrase,encoding))
    return token.decode(encoding)


def password_decrypt(token):
    f = Fernet(bytes(cfgData['key'],encoding))
    phrase = f.decrypt(bytes(token,encoding))
    return phrase.decode(encoding)


def password_return():
    return(password_decrypt(cfgData['token']))


def loadJsonFile():
    # load cfgData[] json file
    try:
        with open(cfgDataFileName, 'r') as cfgDataFile:
            cfgData_temp = json.load(cfgDataFile)
            for key in cfgData:  # If file loaded, replace default values in cfgData with values from file
                if key in cfgData_temp:
                   cfgData[key] = cfgData_temp[key]

    # If file does not exist, it will be created using defaults.
    except IOError:  
        print("Enter sender's device email userid (sending_userid@gmail.com):")    # Sender's email userid
        cfgData["GMAIL_USER"] = input()

        cfgData['key'] = password_key()

        print("Enter password: ")
        cfgData['token'] = password_encrypt(input())

        print("Enter recipient's email userid (recipient_userid@something.com):")  # Recepient's email userid
        cfgData["TO"] = input()

        with open(cfgDataFileName, 'w') as cfgDataFile:
            json.dump(cfgData, cfgDataFile)

    return


# --- MAIN -----------------------------------------------------------------
if __name__ == "__main__" :
    print("KEY   : " + cfgData['key'])
    print("TOKEN : " + cfgData['token'])
    print("USERID: " + cfgData['GMAIL_USER'])
    print("TO    : " + cfgData['TO'])
