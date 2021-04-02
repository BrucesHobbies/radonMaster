#!/usr/bin/env python

# Must be run as super user for bluepy lib to have proper permissions:
#     sudo python3 radonMaster.py
#     -or- as standalone...
#     sudo python3 wave.py

"""
Copyright(C) 2020, BrucesHobbies
All Rights Reserved

AUTHOR: BrucesHobbies
DATE: 12/1/2020
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2021/03/01  BrucesHobbies   Modified for pubScribe.py
  2021/03/24  BrucesHobbies   Added MP4725 DAC output option
  2021/04/01  BrucesHobbies   Changed wavePlus alert message format


OVERVIEW:
    Tested with Airthings WavePlus which reports:
        - Radon short-term average
        - Radon long-term average
        - Volatile Organic Compounds (VOC)
        - Carbon Dioxide (CO2)
        - Temperature
        - Relative Humidity (%rH)
        - Air pressure

    Airthings Wave is slightly different from WavePlus and will require code updates.

    See read_wave for SI units flags instead of USA units (pCi/L, deg F, inches Hg).

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
"""


import sys
import time
import os

import pubScribe

MCP4725_ENABLED = 0

if MCP4725_ENABLED :
    import mcp4725
    dac = mcp4725.mcp4725()
    # initialize bus
    # i2c_ch = 1                    # i2c channel
    # dac.bus=smbus.SMBus(i2c_ch)   # Initialize I2C (SMBus)


SerialNumber = 0

SamplePeriod = 60          # 60 Seconds, only used when run as main()

MODE='terminal'

LOGGING_ENABLED = 1

#
# find_wave and read_waveplus both require bluepy, SerialNumber==0 indicates bluepy lib or wave not found
# 
import find_wave2c
if not SerialNumber :
    SerialNumber = find_wave2c.findWave()

# If SerialNumber == 0 then don't attempt to read_waveplus
if SerialNumber :
    import read_waveplus2c


#
# Alert enables (0 = alert disabled)
#
radonAlertEnabled = 1
vocAlertEnabled = 1
co2AlertEnabled = 1
tempAlertEnabled = 1
humidityAlertEnabled = 1


"""
#
# Airthings brackets with my summary descriptions
#
radonBrackets = ((4.0,"Extreme"),(2.7,"Very high"),(1.4,"High"),(0.0,"Good"))
vocBrackets   = ((2000.0,"Extreme"),(250.0,"High"),(0.0,"Good"))
co2Brackets   = ((2000.0,"Extreme"),(1500.0,"Very high"),(1000.0,"High"),(400.0,"Average"),(0.0,"Better than average"))
#humidityBrackets are a separate function
tempBrackets  = ((77.0,"Red"),(64.0,"Green"),(-99.9,"Blue"))
"""


#
# Airthings updated notification brackets or create your own...
# https://help.airthings.com/en/articles/4500713-wave-plus-sensor-thresholds
# Last bracket is always nominal
#
radonBrackets = ((4.0,"Red"),(2.7,"Yellow"),(0.0,"Green"))          # Imperial/US
# radonBrackets = ((150.0,"Red"),(100.0,"Yellow"),(0.0,"Green"))    # Metric
vocBrackets   = ((2000.0,"Red"),(250.0,"Yellow"),(0.0,"Green"))
co2Brackets   = ((1000.0,"Red"),(800.0,"Yellow"),(0.0,"Normal"))
#humidityBrackets are a separate function

tempBrackets  = ((77.0,"Red"),(64.0,"Green"),(-99.9,"Blue"))      # Imperial/US, 2nd bracket is nominal
# tempBrackets  = ((25.0,"Red"),(18.0,"Green"),(-99.9,"Blue"))    # Metric, 2nd bracket is nominal


#
# Alert message throttling variables
#
radonAlertTime    = [0] * len(radonBrackets)
vocAlertTime      = [0] * len(vocBrackets)
co2AlertTime      = [0] * len(co2Brackets)
tempAlertTime     = [0] * len(tempBrackets)
humidityAlertTime = [0] * 3

#
THROTTLE_TIME = 24*60*60    # once a day in seconds


def compareValue(value, brackets) :
    result = ""

    for i in range(len(brackets)) :
        if value >= brackets[i][0] :
            result = brackets[i][1]
            break

    return i, result


def compareRH(percentage) :
    # percentage is number between 0 and 100
    if (percentage>70) or (percentage<25) :
        result = "Red"
        i=0
    elif (percentage>60) or (percentage<30) :
        result = "Yellow"
        i=1
    else :
        result = "Good"
        i=2

    return i, result


def sensor2StringUnits(sensors) :
    global radonAlertTime, vocAlertTime, co2AlertTime, tempAlertTime, humidityAlertTime

    alert = 0
    tsec = time.time()

    rhValue = sensors.getValue(read_waveplus2c.SENSOR_IDX_HUMIDITY)
    humidity = 'Humidity    : {0:7.1f} {1:s}   '.format(rhValue, sensors.getUnit(read_waveplus2c.SENSOR_IDX_HUMIDITY))
    if humidityAlertEnabled :
        i, result = compareRH(rhValue)
        humidity += result

        if i==len(humidityAlertTime)-1 :
            if humidityAlertTime[i]==0 :    # send alert once on transition into good bracket
                humidityAlertTime[i] = tsec
                alert = 1
        elif (tsec > (humidityAlertTime[i]+THROTTLE_TIME)) :
            humidityAlertTime[i] = tsec
            alert = 1
            humidityAlertTime[len(humidityAlertTime)-1] = 0    # reset 

    radonStValue = sensors.getValue(read_waveplus2c.SENSOR_IDX_RADON_SHORT_TERM_AVG)
    radon_st_avg = 'Radon ST avg: {0:7.1f} {1:s} '.format(radonStValue, sensors.getUnit(read_waveplus2c.SENSOR_IDX_RADON_SHORT_TERM_AVG))
    if radonAlertEnabled :
        i, result = compareValue(radonStValue, radonBrackets)
        radon_st_avg += result

        if i==len(radonAlertTime)-1 :
            if radonAlertTime[i]==0 :    # send alert once on transition into good bracket
                radonAlertTime[i] = tsec
                alert = 1
        elif (tsec > (radonAlertTime[i]+THROTTLE_TIME)) :
            radonAlertTime[i] = tsec
            alert = 1
            radonAlertTime[len(radonAlertTime)-1] = 0    # reset 

    radonLtValue = sensors.getValue(read_waveplus2c.SENSOR_IDX_RADON_LONG_TERM_AVG)
    radon_lt_avg = 'Radon LT avg: {0:7.1f} {1:s} '.format(radonLtValue, sensors.getUnit(read_waveplus2c.SENSOR_IDX_RADON_LONG_TERM_AVG))

    tempValue = sensors.getValue(read_waveplus2c.SENSOR_IDX_TEMPERATURE)
    temperature = 'Temperature : {0:7.1f} {1:s}  '.format(tempValue, sensors.getUnit(read_waveplus2c.SENSOR_IDX_TEMPERATURE))
    if tempAlertEnabled :
        i, result = compareValue(tempValue, tempBrackets)
        temperature += result

        if i==1 :
            if tempAlertTime[i]==0 :    # send alert once on transition into good bracket
                tempAlertTime[i] = tsec
                alert = 1
        elif (tsec > (tempAlertTime[i]+THROTTLE_TIME)) :
            tempAlertTime[i] = tsec
            alert = 1
            tempAlertTime[1] = 0    # reset 

    pressValue = sensors.getValue(read_waveplus2c.SENSOR_IDX_REL_ATM_PRESSURE)
    pressure = 'Pressure    : {0:7.2f} {1:s} '.format(pressValue, sensors.getUnit(read_waveplus2c.SENSOR_IDX_REL_ATM_PRESSURE))

    co2Value = sensors.getValue(read_waveplus2c.SENSOR_IDX_CO2_LVL)
    CO2_lvl = 'CO2 level   : {0:7.1f} {1:s}   '.format(co2Value, sensors.getUnit(read_waveplus2c.SENSOR_IDX_CO2_LVL))
    if co2AlertEnabled :
        i, result = compareValue(co2Value, co2Brackets)
        CO2_lvl += result

        if i==len(co2AlertTime)-1 :
            if co2AlertTime[i]==0 :    # send alert once on transition into good bracket
                co2AlertTime[i] = tsec
                alert = 1
        elif (tsec > (co2AlertTime[i]+THROTTLE_TIME)) :
            co2AlertTime[i] = tsec
            alert = 1
            co2AlertTime[len(co2AlertTime)-1] = 0    # reset 

    vocValue = sensors.getValue(read_waveplus2c.SENSOR_IDX_VOC_LVL)
    VOC_lvl = 'VOC level   : {0:7.1f} {1:s}   '.format(vocValue, sensors.getUnit(read_waveplus2c.SENSOR_IDX_VOC_LVL))
    if vocAlertEnabled :
        i, result = compareValue(vocValue, vocBrackets)
        VOC_lvl += result

        if i==len(vocAlertTime)-1 :
            if vocAlertTime[i]==0 :    # send alert once on transition into good bracket
                vocAlertTime[i] = tsec
                alert = 1
        elif (tsec > (vocAlertTime[i]+THROTTLE_TIME)) :
            vocAlertTime[i] = tsec
            alert = 1
            vocAlertTime[len(vocAlertTime)-1] = 0    # reset 
        
    data = [radonStValue, radonLtValue, vocValue, co2Value, tempValue, rhValue, pressValue]
    wavePlusString = [radon_st_avg, radon_lt_avg, VOC_lvl, CO2_lvl, temperature, humidity, pressure]

    return data, wavePlusString, alert


hdrRow = ""


#
# Header row for log file or display
#
def writeHeaders() :
    global hdrRow

    sensors = read_waveplus2c.Sensors()

    hdrRow = "Radon ST avg (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_RADON_SHORT_TERM_AVG)) \
                + "),Radon LT avg (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_RADON_LONG_TERM_AVG)) \
                + "),VOC level (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_VOC_LVL)) \
                + "),CO2 level (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_CO2_LVL)) \
                + "),Temperature (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_TEMPERATURE)) \
                + "),Humidity (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_HUMIDITY)) \
                + "),Pressure (" + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_REL_ATM_PRESSURE)) + ")"

    if MCP4725_ENABLED :
        hdrRow += ",Fan"

    if MODE=='terminal' :
        # print(hdrRow[5:])
        print(hdrRow)



#
# Read AirThings Waveplus, log data to csv file
#
msgOnce = 1

def readAirthings() :
    global msgOnce

    results = ""
    alert = 0

    if not SerialNumber :
        if msgOnce :
            msgonce = 0
            print("Wave not found! Trying manually entering serial number into code instead of scanning.")
        return

    try:
        waveplus = read_waveplus2c.WavePlus(SerialNumber)
        waveplus.connect()
        sensors = waveplus.read()
        waveplus.disconnect()

        data, wavePlusString, alert = sensor2StringUnits(sensors)

        if MCP4725_ENABLED :
            fanValue = round(dac.alg(data),3)
            # print("FanValue: ", fanValue)
            data.append(fanValue)
            wavePlusString.append('Fan value   : {0:7.2f}    '.format(fanValue))

        if LOGGING_ENABLED :
            topic = "RadonMaster/WavePlus"
            pubScribe.pubRecord(pubScribe.CSV_FILE, topic, data, hdrRow)
        
        results = ""
        for item in wavePlusString :
            results += item + "\n"

    except :
        print("readAirthings() Exception!")
        waveplus.disconnect()

    return results, alert


if __name__ == '__main__':

    if (MODE=='terminal'):
        print("\nPress ctrl+C to exit program\n")
        print("Device serial number: %s" %(SerialNumber))
        print("Sample Period: %u seconds" %(SamplePeriod))
        print("")

    pubScribe.connectPubScribe()

    writeHeaders()

    try :
        while True:
            results, alert, s = readAirthings()

            if (MODE=='terminal'):
                print(results)

                if alert :
                    print("=== ALERT! ===")
                    print(s)

            time.sleep(SamplePeriod)
            
    except KeyboardInterrupt:
        print(" Keyboard interrupt caught.")

    pubScribe.disconnectPubScribe()
