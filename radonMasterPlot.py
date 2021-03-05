#!/usr/bin/env python

"""
Copyright(C) 2020, BrucesHobbies
All Rights Reserved

AUTHOR: BruceHobbies
DATE: 12/5/2020
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2021/03/01  BrucesHobbies   Revised default log file names
  2021/03/05  BrucesHobbies   Updated for pubScribe


OVERVIEW:
    RadonMaster(TM) is a system to montior a radon mitigation fan
    for drawing a sufficient vacuum. Radon is the second leading cause of
    lung cancer, behind smoking, and a failed radon mitigation system.

    This program plots the measured radon mitigation fan vacuum and 
    from AirThings WavePlus the short-term and long-term radon levels,
    Volatile Organic Compounds (VOC) levels, Carbon Dioxide (CO2) levels,
    temperature, relative humidity, and air pressure.

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

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import math
import time
import datetime
import csv


#
# Read in a comma seperated variable file. Assumes a header row exists.
#   Time series with time in seconds in first column.
#   Ignore text string with date/time from second column
#   data is columns [2:]
#
def importCsv(filename) :
    print("Reading " + filename)

    with open(filename, 'r') as csvfile :
        csvData = list(csv.reader(csvfile))

    hdr = csvData[0]
    print(hdr)

    tStamp = []
    for row in csvData[1:] :
        tStamp.append(float(row[0]))

    data = {name : [] for name in hdr[2:]}
    # print(data)

    for row in csvData[1:] :
        for idx in range(2,len(hdr)) :
            n = float(row[idx])
            if n == -99 :
                n = np.nan
            data[hdr[idx]].append(n)

    return hdr[2:], tStamp, data


#
# Plot single or multiple variables {"key":[]} on common subplot
#
def plotMultiVar(tStamp, data, title) :

    t = [datetime.datetime.fromtimestamp(ts) for ts in tStamp]

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    for item in data :
        # print(item)
        ax1.plot(t, data[item], label=item)
        # ax1.plot(t, data[item], marker='d', label=item)

    ax1.set_title(title)

    if len(data) > 1 :
        ax1.legend(loc='upper right', shadow=True)
    else :
        ax1.set_ylabel(item)

    ax1.grid(which='both')

    plt.gcf().autofmt_xdate()    # slant labels
    dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(dateFmt)


#
# Plot single variable {"item":[]}
#
def plotSingleVar(tStamp, data, title, item) :

    t = [datetime.datetime.fromtimestamp(ts) for ts in tStamp]

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(t, data[item], label=item)
    # ax1.plot(t, data[item], marker='d', label=item)

    ax1.set_title(title)
    ax1.set_ylabel(item)

    ax1.grid(which='both')

    plt.gcf().autofmt_xdate()    # slant labels
    dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(dateFmt)


#
# Plot two files
#
if __name__ == "__main__" :

    # --- WavePlus data ---
    #  (time in column 0, data in columns 2:)
    filename = "RadonMaster_WavePlus.csv"
    header, tStamp, data = importCsv(filename)

    for item in data :
        plotSingleVar(tStamp, data, filename[:-4], item)

    # --- Mitigation fan pressure ---
    filename = "RadonMaster_PresSensor.csv"
    header, tStamp, data = importCsv(filename)

    plotMultiVar(tStamp, data, 'Mitigation Fan Vacuum')

    # Pause to close plots
    plt.show(False)    # Blocks, user must close plot window
    print("")
    input("Press [enter] key to close plots...")
    print("Done...")
