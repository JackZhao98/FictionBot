#!/usr/bin/python3

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os.path



def sendEmail(From, Auth, To, attFile, title):
    msg = MIMEMultipart()
    msg['Subject'] = "convert"
    msg['From'] = From
    msg['To'] = To

    basename = os.path.basename(attFile)

    att = MIMEText(open(attFile,'rb').read(),'base64','utf-8')
    att.add_header("Content-Disposition", "attachment", filename=("utf-8", "", title))
    msg.attach(att)
        
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.ehlo()
    server.login(From,Auth)
    server.sendmail(From, To, msg.as_string())
    server.quit()
    print(title + " has been sent to " + To + "!")
