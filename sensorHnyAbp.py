#!/usr/bin/env python

"""
Copyright(C) 2020, BrucesHobbies
All Rights Reserved

AUTHOR: Bruce
DATE: 12/1/2020
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2021/03/01  BrucesHobbies   Fixed exception logic in readAbp()'s


OVERVIEW:
  Read and calculate pressure optional with temperature from Honeywell ABP series pressure sensor 
  (High Accuracy, Compensated/Amplified, 60 mbar to 10 bar | 6kPa to 1 MPa | 1 psi to 150 psi,
  Liquid Media Capable)


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

Each sensor is either I2C or SPI, but not both.

RASPBERRY PI I2C PINS to ABP PRESSURE SENSOR (4-wires):
  RPI 40-pin           ABP (From Table 8 in Data Sheet)
  Pin  1 (+3.3 VDC)  = Pin 2 (+3.3 Vsupply)
  Pin  3 (SDA1)      = Pin 5 (SDA)
  Pin  5 (SCL1)      = Pin 6 (SCL)
  Pin  6 (GND)       = Pin 1 (GND)

RASPBERRY PI SPI PINS to ABP PRESSURE SENSOR (5-wires):
  RPI 40-pin           ABP (From Table 8 in Data Sheet)
  Pin 17 (+3.3 VDC)  = Pin 2 (+3.3 Vsupply)
  Pin 21 (SPI_MISO)  = Pin 5 (MISO)
  Pin 23 (SPI_CLK)   = Pin 6 (SCLK)
  Pin 24 (SPI_CE0_N) = Pin 3 (SS)
  Pin 25 (GND)       = Pin 1 (GND)

PACKAGES REQUIRED:
  sudo apt-get install python3-smbus    # I2C 

Use RASPI Config to enable I2C and SPI buses.

# https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md
Commands to display if SPI is enabled on Raspberry PI OS
  ls /dev/*spi*    # Response should be: /dev/spidev0.0  /dev/spidev0.1

Commands to display I2C addresses in use from connected hardware on Raspberry PI OS:
  sudo i2cdetect -y 0
  sudo i2cdetect -y 1


--- OVERVIEW ----------------------------------------------------------------------------
https://sensing.honeywell.com/  
  Sensors available from these distributors: Arrow, Digikey, and Mouser

Decodes sensor type from:
  Basic Board Mount Pressure Sensors, ABP Series, 32305128 Issue E
  Figure 4: Nomenclature and Order Guide

Remove Product series, package, pressure port, and option prefix before passing string to function.
Remove transfer function and supply voltage suffix before passing string to function.

Example 1: ABPMANN001PDSA3 which is a 0 - 1 psi differential 3.3VDC pressure sensor use "001PDS"
Example 2: ABPDANN060MG2A3 which is a 0 - 60 mbar gage 3.3VDC pressure sensor use "060PG2"

Additional examples:
ABPDRRT005PG2A5       ABP D RR T 005PG 2 A 5       "005PG2"
ABPMRRV001PD2A3       ABP M RR V 001PD 2 A 3       "001PD2"
ABPMRRV060MG2A3       ABP M RR V 060MG 2 A 3       "060MG2"
ABPDRRV001PDAA5       ABP D RR V 001PD A A 5       "001PDA"

ABPDRRV001PDSA3       ABP D RR V 001PD S A 3       "001PDS"
ABPDRRV060MGSA3       ABP D RR V 060MG S A 3       "060MGS"
                      |   | |  | |  || | | |        |  ||+------> Output type (S|1-7)
                      |   | |  | |  || | | |        |  |+-------> Differential | Gage
                      |   | |  | |  || | | |        |  +--------> Units: mbar, bar, kPa, MPa, psi
                      |   | |  | |  || | | |        +-----------> Range
                      |   | |  | |  || | | +-> Supply voltage
                      |   | |  | |  || | +---> Transfer function
                      |   | |  | |  || +-----> Output type (S|1-7)
                      |   | |  | |  |+-------> Differential | Gage
                      |   | |  | |  +--------> Units: mbar, bar, kPa, MPa, psi
                      |   | |  | +-----------> Range
                      |   | |  +-------------> Option: N, D, T, V
                      |   | +----------------> Pressure port
                      |   +------------------> Package: D=DIP, M=SMT, L=Leadless SMT
                      +----------------------> Product series: Amplified Basic Pressure
"""


import sys
import time
import smbus    # I2C support
import spidev	# SPI support


class SensorHnyAbp :
    def __init__(self, sensor) :
        # ABP sensor Analog Digital Converter
        self.OUTPUT_MAX = 14745    # 2^14 counts at 90% - maximum 
        self.OUTPUT_MIN = 1638     # 2^14 counts at 10% - minimum

        # ABP sensor pressure range as floats
        self.PRESSURE_MAX = 60.0   # at output maximum
        self.PRESSURE_MIN = 0.0    # at output minimum

        # ABP pressure units and type
        self.PRESS_UNITS = "psi"
        self.PRESS_SENSOR = "diff"

        self.i2c_address = 0x28    # ABP sensor address on the I2C bus

        print("ABP sensor: " + sensor)

        if len(sensor)!=6 :
            print("Error in sensor selection!")
            return

        # RANGE
        range = float(sensor[:3])
        if range<1 or range>600 :
            print("Error in pressure range!")
            return

        self.PRESSURE_MAX = float(range)
        self.PRESSURE_MIN = 0.0

        # UNITS
        if sensor[3]=="M" :
            self.PRES_UNITS = "mbar"
            self.__conv2inchwc = 0.401865
        elif sensor[3]=="B" :
            self.PRES_UNITS = "bar"
            self.__conv2inchwc = 401.865
        elif sensor[3]=="K" :
            self.PRES_UNITS = "kPa"
            self.__conv2inchwc = 4.01865
        elif sensor[3]=="G" :
            self.PRES_UNITS = "mPa"
            self.__conv2inchwc = 4018.65
        elif sensor[3]=="P" :
            self.PRES_UNITS = "psi"
            self.__conv2inchwc = 27.679904842545
        else :
            print("Error in pressure range units!")
            self.__conv2inchwc = 0.0

        # diff|gage
        if sensor[4]=="D" :
            self.PRESS_SENSOR = "diff"
            self.PRESSURE_MIN = -self.PRESSURE_MAX
        elif sensor[4]=="G" :
            self.PRESS_SENSOR = "gage"
        else :
            print("Error in diff|gage type!")

        # SPI or I2C address
        if sensor[5]=="S" :
            self.i2c_address = 0                  # i2c_address==0 indicates SPI for us
        else :
            i2c_addr = int(sensor[5])
            if (i2c_addr > 0) and (i2c_addr < 8) :
                self.i2c_address = (i2c_addr << 4) + 0x08
            else :
                print("Error in i2c address!")    # self.i2c_address remains unchanged

        if self.i2c_address :
            addr = " i2c address: " + hex(self.i2c_address)
        else :
            addr = " SPI"
        print("Range: " + str(round(self.PRESSURE_MIN,1)) + " to " + str(round(self.PRESSURE_MAX,1)) + " " + self.PRES_UNITS + " " + self.PRESS_SENSOR + addr)

        # initialize appropriate bus
        if self.i2c_address :
            i2c_ch = 1                     # i2c channel
            self.bus=smbus.SMBus(i2c_ch)   # Initialize I2C (SMBus)
        else :
            self.spi = spidev.SpiDev()     # Initialize SPI bus
            bus = 0
            device = 0                     # Chip select pin: Set to 0 or 1

            self.spi.open(bus, device)     # Open SPI bus
            self.spi.max_speed_hz = 500000
            self.spi.mode = 0


    def __del__(self) :            # del Abp pressure sensor
        if self.i2c_address :
            self.bus.close()
        else :
            self.spi.close()


    def __cnts2pres(self, dataBlk) :
        # converts 2 bytes to return scaled floating point
        # print("dataBlk[0]: " + hex(dataBlk[0]) + " dataBlk[1]: " + hex(dataBlk[1]))
        ans = ((dataBlk[0] & 0x003F) << 8) + (dataBlk[1] & 0x00ff)

        # calculation of PSI value per Honeywell Technical Note
        return ((ans-self.OUTPUT_MIN) * (self.PRESSURE_MAX-self.PRESSURE_MIN) / (self.OUTPUT_MAX-self.OUTPUT_MIN)) + self.PRESSURE_MIN 


    def __cnts2tempC(self, dataBlk) :
        # converts 2 bytes to return scaled floating point
        tempC = (dataBlk[2] << 3) + ((dataBlk[3] & 0xE0) >> 5)

        # calculation of temperature per Honeywell Technical Note
        # Temperature output may be uncompensated depending on part number
        return (tempC * 200.0 / 2047.0) - 50.0


    def __statusDecode(statusCode) : 
        """ Status bits
            0 = normal operation, valid data
            1 = device in command mode
            2 = stale data
            3 = diagnostic condition
        """
        return


    # Reads the I2C pressure sensor returning pressure only
    def readAbp(self):                           
        try :
            if self.i2c_address :
                result = self.bus.read_i2c_block_data(self.i2c_address, 0, 2)  # send address with read bit and returns 2 bytes
            else :
                result = self.spi.readbytes(2)

            pressure = self.__cnts2pres(result)

        except :
            pressure = None


        return pressure


    # Reads the I2C pressure sensor and also returns status
    def readAbpStatus(self):
        try :
            if self.i2c_address :
                result = self.bus.read_i2c_block_data(self.i2c_address, 0, 2)  # send address with read bit and returns 2 bytes
            else :
                result = self.spi.readbytes(2)

            status = (result[0] & 0xC0) >> 6
            pressure = self.__cnts2pres(result)

        except :
            status = None
            pressure = None

        return status, pressure


    # Reads the I2C pressure sensor and also returns status and temp
    def readAbpStatusTemp(self):
        try :
            if self.i2c_address :
                result = self.bus.read_i2c_block_data(self.i2c_address, 0, 4)  # send address with read bit and returns 4 bytes
            else :
                result = self.spi.readbytes(4)

            status = (result[0] & 0xC0) >> 6
            pressure = self.__cnts2pres(result)
            tempC = self.__cnts2tempC(result)

        except :
            status = None
            pressure = None
            tempC = None

        return status, pressure, tempC


    """ Conversions (need to verify temperature assumptions for inches of water column)
        1 PSI = 27.679904842545 inches water column at 4 deg C or 39.2 deg F (international standard)
        1" WC = 0.03612729182735355 PSI

        1 PSI = 27.70759 inches water column at 60 deg F (industry practice)
        1" WC = 0.030609 PSI

        1 mbar = 0.401865 inches water column
        1" WC = 2.490889083333 mbar

        1 mbar = 100 Pascals
        1 kPa = 1000 Pascals

        1 kPa = 10 mbar
        1" WC = kPa 0.0401865	# need to verify

        1 mPa = 1000 kPa
    """

    def psi2inchwc(self, psi) :
        return psi * 27.70759

    def mbar2inchwc(self, mbar) :
        return mbar * 0.401865

    def kPa2inchwc(self, kPa) :
        return kPa * 0.0401865	# need to verify

    def c2f(self, tempC) :
        return (tempC * 9.0 / 5.0 + 32.0)

    def pres2inwc(self, pressure) :
        return pressure * self.__conv2inchwc

# end class Abp



if __name__ == '__main__':
    print("Press CTRL+C to exit...")

    try:
        abp = SensorHnyAbp("060MG2")    # 0 to 60 mbar gage I2C
        # abp = SensorHnyAbp("001PDS")    # -1 to +1 psi diff SPI

        while True:
            """
            result = abp.readAbp()
            print('Press: {0:7.3f} {1:s} {2:7.2f} in.wc'.
                     format(round(result,3), abp.PRES_UNITS, round(abp.pres2inwc(result),2)) )

            status, result = abp.readAbpStatus()
            print('Status: {0:d}  Press: {1:7.3f} {2:s} {3:7.2f} in.wc'.
                   format(status, round(result,3), abp.PRES_UNITS, round(abp.pres2inwc(result),2)) )
            """

            status, result, tempC = abp.readAbpStatusTemp()
            if 0 :    # mbar
                print('Status: {0:d}  Press: {1:7.3f} {2:s} {3:7.2f} in.wc {4:5.1f} degF'.
                   format(status, round(result,3), abp.PRES_UNITS, round(abp.pres2inwc(result),2), round(abp.c2f(tempC),1)) )
            else :    # psi
                print('Status: {0:d}  Press: {1:7.3f} {2:s} {3:7.2f} in.wc {4:5.1f} degF'.
                   format(status, round(result,3), abp.PRES_UNITS, round(abp.pres2inwc(result),2), round(abp.c2f(tempC),1)) )

            time.sleep(1)            # Print out every second

    except KeyboardInterrupt:
        sys.exit(" Exit")
