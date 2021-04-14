#!/usr/bin/env python

"""
Copyright(C) 2020, BrucesHobbies
All Rights Reserved

AUTHOR: Bruce
DATE: 12/1/2020
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2021/03/01  BrucesHobbies   Updated to pubScripe.py
  2021/04/01  BrucesHobbies   Changed wavePlus alert message format
  2021/04/14  BrucesHobbies   Added support for variable tone buzzer
                              Added high pressure alert

OVERVIEW:
    RadonMaster(TM) is a system to montior a radon mitigation fan
    for drawing a sufficient vacuum. Radon is the second leading cause of
    lung cancer, behind smoking, and a failed radon mitigation system. An
    alert of a failed radon mitigation system is important. Redundancy
    is important with multiple independent systems. This program is designed
    to provide an understanding of pressure sensors, I2C and SPI buses, Python,
    and the Raspberry Pi hobby computer. 

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
import os
import time
import datetime
from threading import Timer
import math
import subprocess

# RadonMaster imports
import sensorHnyAbp
import pubScribe

#
AIRTHINGS = 0      # Default = 0, which is monitoring and logging disabled
if AIRTHINGS :
    import wave    # Added 12/4/2020

#
# --- User pressure/vacuum sensor configuration parameters ---
#
# abp = sensorHnyAbp.SensorHnyAbp("001PDS")    # -1 to +1 psi diff SPI often found in DIP package
# abp = sensorHnyAbp.SensorHnyAbp("001PG2")    # -1 to +1 psi diff I2C
abp = sensorHnyAbp.SensorHnyAbp("060MG2")    # 0 to 60 mbar gage I2C but often found in surface mount package

tInterval = 1	       # time interval in seconds between fan vacuum measurements (default: 1, 
                       #     possible values: 1, 2, 3, 4, 5, 6, 10, 15, 20, and 30).

# Wind gusts
tAverage = 60          # averaging time in measurements, recommend multiple measurements due to wind gusts

# --- Fan speed alert settings ---
# Be sure and account for variations for wind gust effects on vent opening
pDeltaLowSide  = 0.4    # delta inches water column 
pDeltaHighSide = 0.4    # delta inches water column
pLowPressAlert = 0.5    # Absolute value in case auto calibration is off      
pHighPressAlert = 5.0    # Absolute value in case auto calibration is off      

#
#--- User Email Alerts Configuration ---
#
# First time program starts, it will ask you for the sender's email
# this should be an email that you have established for sending alerts from this program
# gmail is suggested with "Less Secure App Access" turned on. This is required for Python on the RPI.
# If you change passwords, please delete cfgData.json so that this program will again ask for the password.
#
#

pressAlertsEnabled = 1          # non zero enables sending of email messages
waveAlertsEnabled = 1           # non zero enables sending of alerts for Wave Plus readings

statusMsgEnabled = 1
statusMsgHHMM  = [12, 5]        # Status message time to send [hh, mm]
statusInterval = 1              # Interval in days (0=use DOW, 1=every day, 2=every other day, 7=weekly, etc.)
statusDOM      = 0              # Day of month if non-zero
statusDOW      = 0              # Day of week if interval and DOM are not used (0=Mon, 1=Tue, etc)

minIntervalBtwAlerts = 3600     # Wait this long before sending another email - seconds

# End of user configuration


#
# Basic check of user entered configuration parameters
#
def paramCheck() :
    global statusInterval, minIntervalBtwAlerts

    # Status message interval
    if (statusInterval < 0) or (statusInterval > 180) :
        print("Error (statusInterval): status message interval should be in the range of 0 - 180 days.")
        print("0 = use Day Of Month or Day Of Week.")
        sys.exit(" Exit")

    elif (statusDOM < 0) or (statusDOM > 30) :
        print("Error (statusDOM): status message Day Of Month should be in the range of 0 - 30.")
        print("0 = use Day Of Week if statusInterval is also zero.")
        sys.exit(" Exit")

    elif (statusDOW < 0) or (statusDOW > 6) :
        print("Error (statusDOW): status message Day Of Week should be in the range of 0 - 6 (Monday-Sunday).")
        sys.exit(" Exit")

    if (minIntervalBtwAlerts < 0) or (minIntervalBtwAlerts>86400) :
        minIntervalBtwAlerts = 3600
        print("Warning (minIntervalBtwAlerts): Set minimal interval between alert messages to 1 hour.")

    # Status message time
    if (statusMsgHHMM[0]<0) or (statusMsgHHMM[0]>23) :
        print("Error (statusMsgHHMM[0]): status message hour should be in the range of 0 - 23.")
        sys.exit(" Exit")
    
    if (statusMsgHHMM[1]<0) or (statusMsgHHMM[1]>59) :
        print("Error (statusMsgHHMM[1]): status message minute should be in the range of 0 - 59.")
        sys.exit(" Exit")

    # Measurement interval and averaging
    if not tInterval in [1, 2, 3, 4, 5, 6, 10, 15, 20, 30] :
        print("Error (tInterval): check sampling interval.")
        sys.exit(" Exit")

    if (tAverage < 10) or (tAverage> 300) :
        print("Error (tAverage): Measurement averaging should be in range of 10 - 300 measurements.")
        sys.exit(" Exit")

    # Alert levels in inches of water column
    if (pDeltaLowSide < 0.1) or (pDeltaLowSide > 1.0) :
        print("Error (pDeltaLowSide): Vacuum delta should be in range of 0.1 - 1.0 inches of water column.")
        sys.exit(" Exit")

    if (pDeltaHighSide < 0.1) or (pDeltaHighSide > 1.0) :
        print("Error (pDeltaHighSide): Vacuum delta should be in range of 0.1 - 1.0 inches of water column.")
        sys.exit(" Exit")

    if (pLowPressAlert < 0.1) or (pLowPressAlert > pHighPressAlert ) :
        print("Error (pLowPressAlert): Minimum vacuum should be in range of 0.1 - pHighPressAlert inches of water column.")
        sys.exit(" Exit")

    if (pHighPressAlert > 10.0) :
        print("Error (pHighPressAlert): Maximum vacuum should be less than 10.0 inches of water column.")
        sys.exit(" Exit")

# end paramCheck()


#
#--- Global Variables: program use only ---
#
count = 0                            # Count of reads in window of time
lastReadTime = 0                     # Seconds since epoch
sensorSum = 0                        # summation of sensor readings used to form average over interval

pFiltered = 0                        # Filtered readings
calCount = 30                        # Number of averaged readings to form long term average
calLength = calCount

statusIntervalCntDn = 0
lastStatusTime = 0                   # Last time status was sent
lastAlertTime = 0                    # Last time an alert


#
# Display functions
#
def clearWindow() : 
    #define clear() printf("\033[H\033[J")
    # ESC[H moves cursor to top left corner
    # ESC[J clears screen from the cursor to the end of screen
    print("\033[H\033[J")	

def clearDown() :
    print("\033[J")

def printRowCol(row,col,arg="") :
    CSI = "\033["
    print( CSI + str(row) + ";" + str(col) + 'H' + str(arg))

def formatGmTimeSeconds(seconds): 
    # return str(datetime.timedelta(seconds = seconds))
    return time.strftime("%H:%M:%S", time.gmtime(seconds)) 

def formatLocalTime() :
    # timeStr = str(datetime.datetime.now())    # yyyy-mm-dd hh:mm:ss.ssssss
    # return timeStr[:-7]
    return time.strftime("%a, %Y-%b-%d, %H:%M:%S", time.localtime())	#%b=abbr mo, %B=mo name, %m=m as decimal



#
# Calibration algorithm and alert check
#
def radonAlg(sensorAvg) :
    global pFiltered, calCount

    s = "Program logic fault"

    if calCount :
        pFiltered = pFiltered + sensorAvg / calLength
        calCount = calCount - 1
        if calCount :
            s = "Cal in process " + str(calCount)
        else :
            s = "Cal completed"

    else :
        if (sensorAvg < (pFiltered-pDeltaLowSide)) or (sensorAvg > (pFiltered+pDeltaLowSide)) :
            s = "Alert: vacuum delta."
        elif (abs(sensorAvg) < pLowPressAlert) :
            s = "Alert: vacuum less than low limit (pLowPressAlert)."
        elif (abs(sensorAvg) > pHighPressAlert) :
            s = "Alert: vacuum greater than high limit (pHighPressAlert)."
        else :
            s = ""    # Nominal: no alert

    return s


#
# Start timer
#
def startTimer():
    global timer
    t = datetime.datetime.now()
    # Timer(60 - t.second-t.microsecond/1000000., myTimer).start()                  # next minute
    # Timer(1-t.microsecond/1000000., myTimer).start()                              # next second
    Timer(tInterval-(t.second%tInterval)-t.microsecond/1000000.0, myTimer).start()  # next tInterval aligned within minute


#
# Timer
#
stopFlag = 0
firstTimeAirthings = 1
lastPressMsg = ""
lastWaveMsg = ""

def myTimer() :
    global timer, count, sensorSum, lastReadTime, statusIntervalCntDn, lastAlertTime
    global firstTimeAirthings
    global lastPressMsg, lastWaveMsg
   
    t = datetime.datetime.now()

    # Measure vacuum
    status, result = abp.readAbpStatus()
    if status == 0 : 
        sensorSum = sensorSum + abp.pres2inwc(-result)       # change sign to convert pressure to vacuum
        count = count + 1

    # Calculate average vacuum over interval, log data, and check for alert conditions
    if (count>=(tAverage*0.8) and t.second==0) :
        sensorAvg = sensorSum/count
        sensorSum = 0
        count = 0

        # Append interval data to CSV file
        topic = "RadonMaster/PresSensor"
        pubScribe.pubRecord(pubScribe.CSV_FILE, topic, str(round(sensorAvg,2)), "Inches w.c.")
        """ MS-Excel UNIX seconds to date and time
        date from seconds : =FLOOR(A2/86400,1)+DATE(1970,1,1)
        HH:MM from seconds: =MOD(A2,86400)/86400
        """
 
        sAlg = radonAlg(sensorAvg)

        lastPressMsg = '{0:s} Vacuum: {1:7.2f} in.wc'.format(formatLocalTime(), round(sensorAvg, 2))
        print(lastPressMsg + " " + sAlg)

        if not( sAlg=="" or sAlg[:3]=="Cal" ) :
            alertMsg = "Alert " + lastPressMsg

            if pressAlertsEnabled :
                tsec = time.time()
                if ((tsec-lastAlertTime) > minIntervalBtwAlerts) :
                    lastAlertTime = tsec
                    topic = "RadonMaster/Alert"
                    pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, alertMsg)

                # pubScribe.pubRecord(pubScribe.BUZZER, 'Buzzer', {'Frequency': 700, 'Dutycycle': 10, 'Duration': 10})

            else :
                print(alertMsg)

    #
    if AIRTHINGS and (not (t.minute % 15)) and (t.second==30) :
        if firstTimeAirthings :
            firstTimeAirthings = 0
            wave.writeHeaders()

        try :
            lastWaveMsg, alert = wave.readAirthings()

            if alert and waveAlertsEnabled :
                topic = "RadonMaster/Alert"
                pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, lastWaveMsg)
            else :
                print(lastWaveMsg)

            lastWaveMsg = time.strftime("%a, %d %b %Y %H:%M:%S \n", time.localtime()) + lastWaveMsg

        except :
            print("Exception with Bluepy Airthings Wave...")
        

    # Send status message
    if (statusMsgEnabled and t.hour==statusMsgHHMM[0] and t.minute==statusMsgHHMM[1] and t.second==0) :
        sendStatus = 0

        # Send status message every n days, after sending first status message
        if statusInterval :
            statusIntervalCntDn = statusIntervalCntDn - 1
            if statusIntervalCntDn <= 0 :
                statusIntervalCntDn = statusInterval
                sendStatus = 1

        # Send status message on a day of the month
        elif statusDOM :
            if t.day==statusDOM :
                sendStatus = 1

        # Send status message on a day of the week
        elif t.weekday() == statusDOW :
            sendStatus = 1

        if sendStatus :
            s = "Reporting at " + time.strftime("%a, %d %b %Y %H:%M:%S \n", time.localtime())
            s = s + lastPressMsg + "\n" + lastWaveMsg
            topic = "RadonMaster/Status"
            pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, s)
    

    if not stopFlag :
        t = datetime.datetime.now()
        Timer(tInterval - t.microsecond/1000000., myTimer).start()	# every tInterval seconds



#
# Main
#

if __name__ == '__main__':
    # clearWindow()
    print("\nPress CTRL+C to exit...\n")    ##

    paramCheck()
    
    # Display sensor results on program startup 
    status, result, tempC = abp.readAbpStatusTemp()

    # change sign of result to convert pressure to vacuum
    s = 'Status: {0:d}  Vacuum: {1:7.3f} {2:s} {3:7.2f} in.wc {4:5.1f} degF\n'.format(
        status, round(-result,3), abp.PRES_UNITS, round(abp.pres2inwc(-result),2), round(abp.c2f(tempC),1))
    print(s)

    pubScribe.connectPubScribe()

    if statusMsgEnabled :
        topic = "RadonMaster/Status"
        pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, "Program start\n" + s)

    startTimer()

    print("First averaged set of measurement will display in a few minutes...\n") # chg 2020-12-03

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        #timer.cancel()
        stopFlag = 1
        time.sleep(tInterval+1)

    pubScribe.disconnectPubScribe()

