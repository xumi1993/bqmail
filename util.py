#!/usr/bin/env python

import subprocess
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart

def generatemsg(NAME, INST, EMAIL, MEDIA, ALTERNATEMEDIA, LABEL):
    msg = ''
    msg += '.NAME '+NAME+'\n'
    msg += '.INST '+INST+'\n'
    msg += '.MAIL\n'
    msg += '.EMAIL '+EMAIL+'\n'
    msg += '.PHONE\n'
    msg += '.FAX\n'
    msg += '.MEDIA '+MEDIA+'\n'
    msg += '.ALTERNATE MEDIA '+ALTERNATEMEDIA+'\n'
    msg += '.ALTERNATE MEDIA '+ALTERNATEMEDIA+'\n'
    msg += '.LABEL '+LABEL+'\n'
    msg += '.END\n'
    return msg

def sendmail(recipient, contents): 
    msg = MIMEText(contents, 'text')
    msg['Subject'] = 'BREQ_fast'
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail('localhost', recipient, msg.as_string())
    except smtplib.SMTPException:
        print("Error when send mail")
