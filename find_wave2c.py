# MIT License
#
# Copyright (c) 2018 Airthings AS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://airthings.com

# REVISIONS
# DATE          NAME             COMMENTS
# 2020-12-02    BrucesHobbies    Updated from python2 to python3
#                                Changed script to callable functions

import time
import struct

bluePyFound = 1

try :
    from bluepy.btle import Scanner, DefaultDelegate

    class DecodeErrorException(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    class ScanDelegate(DefaultDelegate):
        def __init__(self):
            DefaultDelegate.__init__(self)

except :
    print("Failed to import bluepy!")
    print("Try 'sudo pip3 install bluepy==1.2.0'")
    print("then 'sudo bluetoothctl','power on','show' and 'quit'")
    bluePyFound = 0


def findWave() :
    serial_no = ""
    attempts = 3

    if not bluePyFound :
        return 0

    scanner = Scanner().withDelegate(ScanDelegate())

    try:
        while not serial_no and attempts :
            attempts = attempts - 1
            devices = scanner.scan(2.0)

            for dev in devices:
                ManuData = ""
                ManuDataHex = []
                for (adtype, desc, value) in dev.getScanData():
                    if (desc == "Manufacturer"):
                        ManuData = value

                    if (ManuData == ""):
                        continue

                    for i, j in zip (ManuData[::2], ManuData[1::2]):
                        ManuDataHex.append(int(i+j, 16))

                    #Start decoding the raw Manufacturer data
                    if ((ManuDataHex[0] == 0x34) and (ManuDataHex[1] == 0x03)):
                        serial_no = str(256*256*256*ManuDataHex[5] + 256*256*ManuDataHex[4] + 256*ManuDataHex[3] + ManuDataHex[2])
                        print("Airthings addr %s (%s), RSSI=%d dB, SN=%s\n" % (dev.addr, dev.addrType, dev.rssi, serial_no))
                    else:
                        continue

    except DecodeErrorException:
        pass

    return int(serial_no)


if __name__ == '__main__':
    print("Serial_no: ", findWave())
