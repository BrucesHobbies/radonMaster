#!/usr/bin/env python

"""
Copyright(C) 2020, BrucesHobbies
All Rights Reserved

AUTHOR: BruceHobbies
DATE: 12/5/2020
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------


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
#
def importCsv(filename) :
    print("Reading " + filename)

    with open(filename, 'r') as csvfile :
        data = list(csv.reader(csvfile))

    header = data[0]
    print(header)

    a = np.array(data[1:], dtype=np.float)

    print("Elements: ", a.size)
    print("Rows    : ", len(a[:,0]))
    print("Cols    : ", len(a[0,:]))

    return header, a

#
# Plot Short-Term and Long-Term radon levels
#   thresholds(y_value,"label")
#
def plotRadon(thresholds) :
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(t, a[:,1], 'b', label='ST')
    ax1.plot(t, a[:,2], 'r', label='LT')
    # ax1.plot(t, a[:,1], 'b', marker='d', label='ST')
    # ax1.plot(t, a[:,2], 'r', marker='d', label='LT')

    for item in thresholds :
        ax1.plot([t[0], t[len(t)-1]], [item[0], item[0]], item[1])

    ax1.set_title("Radon")
    ax1.set_xlabel('Time')
    ax1.set_ylabel(header[1][9:])
    ax1.legend(loc='upper right', shadow=True)

    ax1.grid(which='both')
    plt.gcf().autofmt_xdate()    # slant labels
    dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(dateFmt)

    plt.show(block=False)

#
# Plot VOC, CO2, Temperature, Relative, Humidity, and air pressure
#
def plotSingle(var, ylabel, title) :
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(t, var)
    # ax1.plot(t, var, marker='d')

    ax1.set_title(title)
    ax1.set_xlabel('Time')
    ax1.set_ylabel(ylabel)
    
    ax1.grid(which='both')
    plt.gcf().autofmt_xdate()    # slant labels
    dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(dateFmt)

    plt.show(block=False)

#
# Plot two files
#
if __name__ == "__main__" :

    # --- Radon Short-term and Long-term ---
    #  (time in column 0, data in columns 1 - 2)
    # filename = "radonLogFile.csv"
    filename = "waveLogFile.csv"
    header, a = importCsv(filename)

    tstamp = []
    for item in a[:,0] :
        tstamp.append(item)
    t = [datetime.datetime.fromtimestamp(ts) for ts in tstamp]

    plotRadon([(1.3, 'g--'),(2.7, 'y--'),(4.0, 'r--')])

    # Plot remaining data from WavePlus (columns 4 - 8)
    for col in range(3, len(header)-1) :
        plotSingle(a[:,col],header[col],header[col])


    # --- Mitigation fan pressure ---
    filename = "radonMaster.csv"
    header, a = importCsv(filename)

    tstamp = []
    for item in a[:,0] :
        tstamp.append(item)
    t = [datetime.datetime.fromtimestamp(ts) for ts in tstamp]

    plotSingle(a[:,1],'Inches W.C.','Mitigation Fan Vacuum')

    # Pause to close plots
    input("Press [enter] key to close plots...")
    print("Done...")
