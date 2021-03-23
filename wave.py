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
#
radonBrackets = ((4.0,"Red"),(2.7,"Yellow"),(0.0,"Green"))
vocBrackets   = ((2000.0,"Red"),(250.0,"Yellow"),(0.0,"Green"))
co2Brackets   = ((2000.0,"Red"),(800.0,"Yellow"),(250.0,"Poor"),(0.0,"Good"))
#humidityBrackets are a separate function
tempBrackets  = ((77.0,"Red"),(64.0,"Green"),(-99.9,"Blue"))


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


def checkAlerts(radonValue, vocValue, co2Value, tempValue, rhValue) :
    global radonAlertTime, vocAlertTime, co2AlertTime, tempAlertTime, humidityAlertTime

    alert = 0
    s = ""

    tsec = time.time()

    if radonAlertEnabled :
        i, result = compareValue(radonValue, radonBrackets)
        s = s + "Radon: " + result + "\n"

        if i==len(radonAlertTime)-1 :
            if radonAlertTime[i]==0 :    # send alert once on transition into good bracket
                radonAlertTime[i] = tsec
                alert = 1
        elif (tsec > radonAlertTime[i]+THROTTLE_TIME) :
            radonAlertTime[i] = tsec
            alert = 1
            radonAlertTime[len(radonAlertTime)-1] = 0    # reset 

    if vocAlertEnabled :
        i, result = compareValue(vocValue, vocBrackets)
        s = s+ "VOC  : " + result + "\n"

        if i==len(vocAlertTime)-1 :
            if vocAlertTime[i]==0 :    # send alert once on transition into good bracket
                vocAlertTime[i] = tsec
                alert = 1
        elif (tsec > vocAlertTime[i]+THROTTLE_TIME) :
            vocAlertTime[i] = tsec
            alert = 1
            vocAlertTime[len(vocAlertTime)-1] = 0    # reset 

    if co2AlertEnabled :
        i, result = compareValue(co2Value, co2Brackets)
        s = s + "CO2  : " + result + "\n"

        if i==len(co2AlertTime)-1 :
            if co2AlertTime[i]==0 :    # send alert once on transition into good bracket
                co2AlertTime[i] = tsec
                alert = 1
        elif (tsec > co2AlertTime[i]+THROTTLE_TIME) :
            co2AlertTime[i] = tsec
            alert = 1
            co2AlertTime[len(co2AlertTime)-1] = 0    # reset 

    if tempAlertEnabled :
        i, result = compareValue(tempValue, tempBrackets)
        s = s + "Temp : " + result + "\n"

        if i==1 :
            if tempAlertTime[i]==0 :    # send alert once on transition into good bracket
                tempAlertTime[i] = tsec
                alert = 1
        elif (tsec > tempAlertTime[i]+THROTTLE_TIME) :
            tempAlertTime[i] = tsec
            alert = 1
            tempAlertTime[len(tempAlertTime)-1] = 0    # reset 

    if humidityAlertEnabled :
        i, result = compareRH(rhValue)
        s = s + "RH   : " + result + "\n"

        if i==len(humidityAlertTime)-1 :
            if humidityAlertTime[i]==0 :    # send alert once on transition into good bracket
                humidityAlertTime[i] = tsec
                alert = 1
        elif (tsec > humidityAlertTime[i]+THROTTLE_TIME) :
            humidityAlertTime[i] = tsec
            alert = 1
            humidityAlertTime[len(humidityAlertTime)-1] = 0    # reset 

    """
    if (MODE=='terminal'):
        print(s)
    """

    return alert, s


def sensor2StringUnits(sensors) :
    s = ""
    humidity     = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_HUMIDITY))             + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_HUMIDITY))
    radon_st_avg = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_RADON_SHORT_TERM_AVG)) + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_RADON_SHORT_TERM_AVG))
    radon_lt_avg = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_RADON_LONG_TERM_AVG))  + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_RADON_LONG_TERM_AVG))
    temperature  = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_TEMPERATURE))          + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_TEMPERATURE))
    pressure     = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_REL_ATM_PRESSURE))     + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_REL_ATM_PRESSURE))
    CO2_lvl      = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_CO2_LVL))              + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_CO2_LVL))
    VOC_lvl      = str(sensors.getValue(read_waveplus2c.SENSOR_IDX_VOC_LVL))              + " " + str(sensors.getUnit(read_waveplus2c.SENSOR_IDX_VOC_LVL))
        
    data = [radon_st_avg, radon_lt_avg, VOC_lvl, CO2_lvl, temperature, humidity, pressure]
    return data


hdrRow = ""


#
# Log wave data to csv file
#
def write2Csv(s) :
    csvFile = open(wpLogFilename, "a")
    csvFile.write(s + "\n")
    csvFile.close()



def formatLocalTime() :
    # timeStr = str(datetime.datetime.now())    # yyyy-mm-dd hh:mm:ss.ssssss
    # return timeStr[:-7]
    return time.strftime("%a, %Y-%b-%d, %H:%M:%S", time.localtime())	#%b=abbr mo, %B=mo name, %m=m as decimal


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
    s = ""

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

        # extract
        humidity     = sensors.getValue(read_waveplus2c.SENSOR_IDX_HUMIDITY)
        radon_st_avg = sensors.getValue(read_waveplus2c.SENSOR_IDX_RADON_SHORT_TERM_AVG)
        radon_lt_avg = sensors.getValue(read_waveplus2c.SENSOR_IDX_RADON_LONG_TERM_AVG)
        temperature  = sensors.getValue(read_waveplus2c.SENSOR_IDX_TEMPERATURE)
        pressure     = sensors.getValue(read_waveplus2c.SENSOR_IDX_REL_ATM_PRESSURE)
        CO2_lvl      = sensors.getValue(read_waveplus2c.SENSOR_IDX_CO2_LVL)
        VOC_lvl      = sensors.getValue(read_waveplus2c.SENSOR_IDX_VOC_LVL)

        if LOGGING_ENABLED :
            data = [radon_st_avg, radon_lt_avg, VOC_lvl, CO2_lvl, temperature, humidity, pressure]
            topic = "RadonMaster/WavePlus"
            pubScribe.pubRecord(pubScribe.CSV_FILE, topic, data, hdrRow)
        
            results = formatLocalTime() + " " + str(sensor2StringUnits(sensors))

            alert, s = checkAlerts(radon_st_avg, VOC_lvl, CO2_lvl, temperature, humidity)

        if MCP4725_ENABLED :
            fanValue = dac.alg(data)
            data = [fanValue]
            # print("FanValue: ", fanValue)
            topic = "RadonMaster/Fan"
            hdr = "FanSetting"
            pubScribe.pubRecord(pubScribe.CSV_FILE, topic, fanValue, hdr)


    except :
        print("Exception!!!")
        waveplus.disconnect()

    return results, alert, s


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
