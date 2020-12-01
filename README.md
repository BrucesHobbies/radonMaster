# radonMaster™
Copyright(C) 2020, BrucesHobbies,
All Rights Reserved

Radon mitigation monitoring for homes and buildings - This is a DIY project for the Raspberry Pi or similar system using an inexpensive Honeywell sensor with a couple of wires. The software is written in Python and runs under Linux.
# Preface
According to the US Environmental Protection Agency (EPA), radon gas is the major cause of lung cancer amongst non-smokers killing about 21,000 people each year in the USA and 20,000 in the European Union. Radon gas is part of the breakdown chain of naturally occurring radioactive materials in the ground beneath our homes.  It seeps into our homes through the tiniest of openings including tiny cracks in our basement floors, crawl spaces, and building foundations. It is invisible, odorless, colorless, and tasteless. Worse yet, it clings to dust and surfaces and is easily inhaled making it a severe health hazard. Scientists estimate that half the radiation we are exposed to in our lifetimes comes from radon gas. More than what we are exposed to from cosmic rays, medical / dental screening, food, and drink combined!
When I recently bought a house I was told that radon was not an issue. I then bought a radon detector. It measured over 8 pCi/L whereas outdoor levels are typically only around 0.3 pCi/L. Urgent action was required! A review of mitigation systems offered alternatives from venting to active fan systems that either pressurize the whole house with outside air or under home depressurization (vacuum).  The home already had an under concrete slab vent system so it was time to get an active fan system. The  fan systems usually connect a sump well, drain tile, or sub-membrane beneath the building foundation or slab to a fan that then vacuums the vapors including radon gas to the outside where is disperses. The vent area should not be above or below a living area nor within 10 feet of windows, doors, or openings.  I installed a radon fan for mitigation and the measured radon levels started to drop over the next few weeks from over 8 to under 1 pCi/L. Radon has a half-life of 3.8 days so it takes a while to dissipate.  The levels are now running around the typical outdoor level. However, if the radon mitigation fan should ever fail, I would silently be exposed to very high levels of radioactive radon. 

![Figure 1: Radon Mitigation System Components (source: [Minnesota Department of Health: Radon Mitigation](https://www.health.state.mn.us/communities/environment/air/radon/mitigationsystem.html#:~:text=Three%20of%20the%20most%20common,placed%20on%20the%20sump%20baskets))](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure1.png)

I installed a u-tube manometer to measure the suction of the radon mitigation fan system as shown in the figure. A manometer uses the difference in water height in a U-shaped tube to show the pressure difference. They are available for about $10 - $20 USD. However, most people don’t spend a lot of time in the basement or under their home in a crawl space looking at a manometer on their radon mitigation system. There are commercial alarm systems that are available for about $80 USD that sound an alarm if the radon mitigation system loses pressure. However, I noticed that when we have windy days,  the wind gusts as seen on the manometer are large. I was looking for something that was better. I wanted something that I could adjust the alert levels and also something that wouldn’t sound an alarm in the middle of the night, which would be worse than a smoke detector’s low battery chirp in the middle of the night. I wanted a system that would send an alert to my cell phone as a text message that I could then quickly follow up on the next day.

Websites for further reading:

[US EPA: Find Information About Local Radon Zones](https://www.epa.gov/radon/find-information-about-local-radon-zones-and-state-contact-information#radonmap)

[US EPA: 2013 Consumers Guide to Radon Reduction](https://www.epa.gov/sites/production/files/2016-02/documents/2013_consumers_guide_to_radon_reduction.pdf)

[Minnesota Department of Health: Radon Mitigation](https://www.health.state.mn.us/communities/environment/air/radon/mitigationsystem.html#:~:text=Three%20of%20the%20most%20common,placed%20on%20the%20sump%20baskets)

[Wikipedia: Radon](https://en.wikipedia.org/wiki/Radon)

# RadonMaster™ Project Overview
The Raspberry Pi looked like an ideal platform to monitor the radon mitigation pressure. This project uses a small inexpensive digital pressure sensor from Honeywell with a Raspberry Pi to monitor and send alerts for a radon mitigation fan loss of vacuum. The alerts can be an email or SMS message sent via email. Feel free to contribute with custom alert options such as MQTT, IFTT, etc.  RadonMaster™ logs the pressure sensor readings to a Comma Separated Variable (CSV) file that can be plotted using MatPlobLib or in a spreadsheet. The program is written in Python and can be ported to additional platforms, but the RPI is one of the most common platforms.

# Required Hardware 
## RadonMaster
-	Honeywell ABP pressure sensor available from Digikey, Mouser, Arrow, etc. for around $13 USD 
-	Plastic tube
-	Wire, soldering iron, and solder

I used the ABPDRRV001PDSA3 which is a 3-wire SPI bus interface in a DIP package (Dual-Inline Package found with breadboards). I have also used the ABPMRR060MG2A3 which is a 2-wire I2C bus interface but in a surface mount package which requires soldering. Both are 3.3 Vdc supply voltage. The I2C pull up resistors are not required when used with the RPI.
## Raspberry Pi system (if you don’t already own one)
- Raspberry Pi (any of the following)
  - RPI-Zero
  - RPI 3B+
  - RPI 4
- Power adapter for your Raspberry Pi
- Heatsinks (optional)
- SD-Card

For installing the Raspberry Pi operating system, you may want a USB keyboard and USB mouse along with an HDMI cable and monitor. If using the RPI4, a Micro-HDMI to HDMI adapter may be needed. It is possible to install the operating system without a keyboard, mouse, and monitor, but simpler is sometimes better. Once installed and configured you may want to switch to SSH or remote desktop so that you can remove the monitor, mouse, and keyboard.

## Optional Hardware
A professionally installed Radon Mitigation system can cost around $2,000 USD or more. I installed mine for several hundred dollars in an afternoon and had excellent results. The Airthings Wave Plus radon monitor is outstanding. Here is what I purchased for radon detection and mitigation:
- Radon monitor: Airthings Wave - Radon detector with free app and no lab fees – battery operated
- Radon mitigation fans: RadonAway 23030-1 RP145 Radon Mitigation Fan, 4"
- Manometer: RadonAway 50018 Easy Read Manometer
- 3” to 4” Couplers depending on pipe size you plan to use from the sump well
- Butyl tape to seal sump well. Many people are recommending various silicon sealants which are messy and difficult to remove. An alternative is Butyl tape since it is easy to remove to service the sump pump inside the sump well. My sump well has a backup pump inside the sump well in case the primary pump inside the sump well fails.

# Pressure sensor wiring and installation
## Wiring
Each Honeywell pressure sensor is either i2c or SPI, but not both. The ABPDRRV001PDSA3 which is a 3-wire SPI bus interface is recommended as it is a DIP package.

**RASPBERRY PI SPI PINS to ABP PRESSURE SENSOR (5-wires total):**
RPI 40-pin|SPI ABP (From Table 8 in Honeywell Data Sheet)|
-------------:|------------------------------------------|
Pin 17 (+3.3 VDC) =|Pin 2 (+3.3 Vsupply)|
Pin 21 (SPI_MISO) =|Pin 5 (MISO)|
Pin 23 (SPI_CLK) =|Pin 6 (SCLK)|
Pin 24 (SPI_CE0_N) =|Pin 3 (SS)|
Pin 25 (GND) =|Pin 1 (GND)|
  
**RASPBERRY PI PINS to ABP I2C PRESSURE SENSOR (4-wires total):**
RPI 40-pin|I2C ABP (From Table 8 in Honeywell Data Sheet)|
-------------:|------------------------------------------|
Pin  1 (+3.3 VDC) =| Pin 2 (Vsupply)|
Pin  3 (SDA1) =| Pin 5 (SDA)|
Pin  5 (SCL1) =| Pin 6 (SCL)|
Pin  6 (GND) =| Pin 1 (GND)|

The 3.3 VDC pressure sensors are recommended but, if you purchased a 5.0 VDC pressure sensor then the 5 VDC supply on the pressure sensor pin 2 would go to the RPI Pin 2 (+5.0 VDC). You will need to convert the ABP’s 5 volt bus signals to the RPI bus 3.3 volt levels so this is not as straight forward as using the 3.3 VDC pressure sensor.

## Wiring photo at pressure sensor and RPI
You will purchase either an SPI or I2C pressure sensor, not both. The SPI version is recommended but both sets of photos are included to provide choices.

![Figure 2: SPI Pressure Sensor Wiring – Note tube is attached to P1 port which is designed for liquids.](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure2.png)

![Figure 3: SPI Wiring on RPI – Note white wire looks gray in this photo.](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure3.png)

![Figure 4: I2C power pins](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure4.png)

![Figure 5: I2C bus pins](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure5.png)

![Figure 6: I2C Wiring on RPI](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure6.png)

## Mount pressure sensor to mitigation fan pipe photo
Here is an example of an existing manometer that was installed on the mitigation pipe. You can replace the manometer tube with a tube that runs to the Honeywell pressure sensor port P1 (shown in photo) or you can drill a new hole that fits the tube size. 

![Figure 7: Tube installation](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure7.png)

# Software Installation
## Step 1: Setup the Raspberry Pi Operating System.
Here are the instructions to install the Raspberry Pi Operating System.
[Raspberry Software Install Procedure](https://www.raspberrypi.org/software/operating-systems/)

## Step 2: Install the I2C bus library
If using a Honeywell I2C pressure sensor you will need this library. I would recommend installing it as you may want to use I2C in this project or others. If you don’t install python3-smbus, you will need to comment out the appropriate lines in the program code.

    sudo apt-get install python3-smbus

## Step 3: Enable SPI and/or I2C buses on RPI 
    sudo raspi-config
    
Under interface options, enable either or both the SPI and I2C interfaces depending on the Honeywell ABP pressure sensor that you purchased. In general it is better to enable both so that the interfaces are available for use with projects.
To verify i2c operation, if you have an i2c Honeywell pressure sensor type the following command which should result in the i2c device address 0x28 being displayed:

    sudo i2cdetect –y 1
    
To verify SPI operation, type the following command which should result in the SPI bus being listed:

    ls /dev/*spi*

## Step 4: Download RadonMaster software
There are 4 python files: radonMaster, sensorHnyAbp, sendEmail, and cfgData. To get a copy of the source files type in the following git command assuming you have already installed git:

    git clone https://github.com/BrucesHobbies/radonMaster

## Step 5: Software Configuration
If you desire, you may edit radonMaster.py and change the user configuration section at the beginning of the file.

### Pressure Sensor Configuration
Edit the RadonMaster.py program file if you used a different sensor than the ABPDRRV001PDSA3. Please change the statement to match the variable range, units, and output type of the sensor you purchased. For example if you purchased the ABPMRRV060MG2A3 change from “001PDS” to “060MG2”. Again, this statement is in the radonMaster.py file. More complete details are found in  “sensorHnyAbp.py”.

    sensor = sensorHnyAbp.SensorHnyAbp("001PDS")
    
### Alert Options Configuration
To disable alert messages, change the alertsEnabled value to 0 in “radonMaster.py”.

    alertsEnabled  = 1        # non zero enables sending of email messages

## Step 6: Gmail Configuration
You can use Google Gmail to send status and alert emails. Others have also used Microsoft Live/Outlook/Hotmail, Yahoo, Comcast, ATT, Verizon, and other email servers. 
Currently, status and alert messages are sent by email which can also be sent as an SMS text to your cell phone.  Gmail works with Python on the Raspberry Pi if you set the Gmail security settings to low. As such, you can create a separate Gmail account to send messages from. Under your Gmail account settings you will need to make the following change to allow “Less secure app access”.

![Figure 8: Gmail Less Secure App Access](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure8.png)


Then click on “Turn on access (not recommended)” by moving the slider to ON. Then click the back arrow.

![Figure 9: Enable Less Secure App Access](https://github.com/BrucesHobbies/radonMaster/blob/main/figures/Figure9.png)

# Running The Program From A Terminal Window 
When your first email is sent at program startup, Google will ask you to confirm that it is you. You will need to sign into the device email account that you created and go to the critical security email that Google sent you and confirm you originated the email before Google will allow emails to be sent from your Python program.

Once you have created an account, start the radonMaster™ program.   Type:

    python3 radonMaster.py

The first time the program starts up it will ask you for your gmail user id and password for the account that you just created to work with this program. The password will be saved to a file called cfgData.json.  Please be careful to not send that file to others. If you ever change your password you will need to delete cfgData.json so that the program will ask you for your password again. 

    Enter sender’s device email userid (sending_userid@gmail.com):
    sending_userid@gmail.com

    Enter password:
    password

Next the program will ask you for the recipient email address.  This can either be the same email address, your primary email address or your SMS cell number carrier’s gateway.  To email an SMS to your cell phone construct the recipient email depending on your cell phone carrier:
Carrier|Format
-------|-------|
AT&T|number@txt.att.net|
Verizon|number@vtext.com|
Sprint PCS|number@messaging.sprintpcs.com|
T-Mobile|number@tmomail.net|
VirginMobile|number@vmobl.com|

    Enter recipient’s device email userid (receiving_userid@something.com):
    Receiving_userid@something.com
 
## Status Options Configuration
If alerts are enabled (alertsEnabled=1) and you have entered valid email information you can choose to have a status message sent for a RPI well-being check. To change the time of day for the status message from noon local time, edit the hour and minute. Entering values outside the expected values will allow you to disable status messages. Range for HH is 0 -23 and for MM is 0 – 59.

    statusMsgHHMM  = [12, 0]  # Status message time to send [hh, mm]

Status messages are sent in one of three ways: fixed interval in days, on a specific day of month, or specific day of the week. 

    # Interval in days 
    # (0=use DOW, else 1=every day, 2=every other day, 7=weekly, etc.)
    statusInterval = 1        

    # Day of month if non-zero, 1=first day of month, up to 28, or 30 some # months. 
    statusDOM      = 0        

    # Day of week if interval and DOM are not used (0=Mon, 1=Tue, etc)
    statusDOW      = 0        

If alerts are enabled, you can choose to throttle the alerts. The interval can be as short or long as you like. Default is 3600 seconds which is one hour.

    # Wait this long before sending another email - seconds
    minIntervalBtwAlerts = 3600  

# Future Alert and Status Options
Please feel free to fork and contribute or provide feedback on priorities and features

- Relay / buzzer
- MQTT
  - OpenHab
  - Home Assistant
  - Domoticz
- IFTT
- PubNub
- Twilio
- Cellular
- APRS

# Test Your Configuration and Email Setup
On the first time RadonMaster™ program starts, it will ask you for your email userid and password for the email account that you created to use for the alerts and status messages. Once you have entered a password the program will send an email message indicating the program has started up.

RadonMaster™ will then display the first reading from the pressure sensor including status and temperature according to the type of sensor you selected.

RadonMaster™ will then establish a baseline vacuum as measured by the sensor. Let it complete the calibration. To then test the alert feature, partially remove the tube from the pipe. An alert should be generated. Reinsert the tube into the pipe. Averaged readings should return to normal.

To test the status feature, wait for the status time and verify that you received a status message.

# Optional configuration
While not required or recommended, you can change the following configuration parameters.
    # time interval in seconds between fan vacuum measurements
    # (default: 1, possible values: 1, 2, 3, 4, 5, 6, 10, 15, 20, and 30).
    tInterval = 1	  

    # Wind gusts averaging time in measurements,
    # recommend multiple measurements due to wind gusts and 
    # water sloshing in sump well
    tAverage = 60

    # --- Fan speed alert settings ---
    # Be sure and account for variations for wind 
    # gust effects on vent opening and sump pumping
    pDeltaLowSide  = 0.4    # delta inches water column 
    pDeltaHighSide = 0.4    # delta inches water column
    pLowPressAlert = 0.5    # Abs value in case auto calibration is off      

# Auto Start at Boot
Type the following command:

    sudo crontab –e
    
Select the type of editor you are familiar with. I used nano. Add the following line at the end of the file and then press ctrl+O to write the file and ctrl+X to exit the nano editor.

    @reboot sleep 60 && cd radonMaster && python3 radonMaster.py

# Feedback
Let us know what you think of this project and any suggestions for improvements. Feel free to contribute to this open source project.
