import time
import smtplib

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

GENERAL INFO
  gmail email account security setting must be set to low!
    gmail password can only contain a-z, A-Z, and 0-9. No special characters.

  To send a text message to your phone, use one of the following email addresses 
      depending for your carrier:
  AT&T:		number@txt.att.net
  Sprint PCS: 	number@messaging.sprintpcs.com
  T-Mobile: 	number@tmomail.net
  Verizon: 	number@vtext.com
  VirginMobile:	number@vmobl.com

  SMTP server domain names:
  smtp.gmail.com (port 587 TLS)
  smtp-mail.outlook.com (port 587 TLS)
  smtp.live.com (port 587 TLS)		# alias for Outlook/Hotmail
  smtp.mail.yahoo.com
  smtp.comcast.net
  smtp.mail.att.net (port 465 SSL)
  smtp.verizon.net (port 465 SSL)
"""

# SMTPSERVER = 'smtp.gmail.com'
SMTPSERVERTLSPORT = 'smtp.gmail.com:587'

# SMTPTLSPORT = 587		# For TLS, newer than SSL
# SMTPSSLPORT = 465		# For SSL


#
# --- Send text message ---
#
def send_mail(userID, passwd, to, subject, text): 
    print("Sending email on " + time.strftime("%a, %d %b %Y %H:%M:%S \n", time.localtime()))
    msg = 'To: ' + to + '\nFrom: ' + userID + '\nSubject: ' + subject + '\n\n' + text + '\n\n'
    print(msg)

    if (userID!="") and (passwd!="") and (to!="") :
        try:
            server = smtplib.SMTP(SMTPSERVERTLSPORT)
            server.starttls()
            server.login(userID, passwd)
            server.sendmail(userID, to, msg)
            
            """ SSL alternative instead of TLS...
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTPSERVER, SMTPSSLPORT, context=context) as server:
                server.login(userID, passwd)
                server.sendmail(userID, to, msg)
            """

            print("--- End of message ---")

        except Exception as e:
            print(e)

        finally:
            server.quit()    # TLS quit

    else :
        print("No userids and a password - local message only!\n")


if __name__ == '__main__':
    # User specific settings
    GMAIL_USER= 'userid@gmail.com'
    GMAIL_PASS= 'your_device_email_password'

    # Addressee
    TO= 'email@something.com'
    SUBJECT = 'Subj of Alert!'
    TEXT = 'Alert Message!'

    send_mail(GMAIL_USER, GMAIL_PASS, TO, SUBJECT, TEXT)
    time.sleep(1)
    print("Done.")
