#!/usr/bin/env python

"""
Copyright(C) 2021, BrucesHobbies
All Rights Reserved

AUTHOR: Bruce
DATE: 02/28/2021
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------



OVERVIEW:
    Write to the Microchip MCP4275 or MCP4276 DAC

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
    Debug print can be commented in or out.


RASPBERRY PI I2C PINS to DAC (2-wires plus power and ground):
  RPI 40-pin           MCP4275 DAC in 6-pin SOT-23-6
                     = Pin 1 Vout
                     = Pin 2 Vss (ground reference)
                     = Pin 3 Vdd (2.7V - 5.5V)
  Pin  3 (SDA1)      = Pin 4 (SDA)
  Pin  5 (SCL1)      = Pin 5 (SCL)
                     = Pin 6 A0 (I2C address bit)

PACKAGES REQUIRED:
  sudo apt-get install python3-smbus    # I2C 

Use RASPI Config to enable I2C bus.

Commands to display I2C addresses in use from connected hardware on Raspberry PI OS:
  sudo i2cdetect -y 0
  sudo i2cdetect -y 1

DAC command:
    Supports fast write, not to EEPROM (See data sheet Figure 6-1: Command type C2, C1 = 0, 0)
    Power down bits are zero for normal mode (See data sheet Table 5-2: PD1, PD0 = 0, 0)

"""

import sys
import time
import smbus    # I2C support


class mcp4275 :
    def __init__(self) :
        self.OUTPUT_MAX = 4095    # 2^12-1 counts

        # I2C address is 0x62 or 0x63
        self.i2c_address = 0x62
        print("mcp4275 i2c address: " + hex(self.i2c_address))

        # initialize bus
        i2c_ch = 1                     # i2c channel
        self.bus=smbus.SMBus(i2c_ch)   # Initialize I2C (SMBus)


    def __del__(self) :
        self.bus.close()


    def writeDAC(self, value):
        # value is between 0 and 1.0
        if value > 1 :
            value = 1
        elif value < 0 :
            value = 0

        value = int(round(value * self.OUTPUT_MAX))

        try :
            register = 0x00
            if 1 :
                # Documentation appears that register contains upper nibble (4-bits) of DAC value
                # Otherwise, try without putting upper nibble in register
                register = (value & 0x00FF) >> 8
                value = value & 0x00FF

            self.bus.write_i2c_block_data(self.i2c_address, register, value)
        except :
            pass

        return

# end class



if __name__ == '__main__':
    print("Press CTRL+C to exit...")

    try:
        dac = mcp4275()

        while True:
            print("Enter value (0.0 - 1.0): ")
            value = float(input())
            dac.writeDAC(value)

    except KeyboardInterrupt:
        print(" Keyboard interrupt caught, exiting.")
