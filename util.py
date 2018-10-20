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


def sendmail(sender, recipient, contents, server='localhost', port=465, passwd=''):
    msg = MIMEText(contents, 'text')
    msg['Subject'] = 'BREQ_fast'
    msg['From'] = 'bqmail<'+sender+'>'
    msg['To'] = recipient
    if server == 'localhost':
        try:
            smtpObj = smtplib.SMTP(server)
            smtpObj.sendmail(sender, recipient, msg.as_string())
        except smtplib.SMTPException:
            print("Error when send mail by localhost")
    else:
        try:
            smtpObj = smtplib.SMTP_SSL(server, port)
            smtpObj.login(sender, passwd)
            smtpObj.sendmail(sender, recipient, msg.as_string())
        except smtplib.SMTPException:
            print("Error in linking {}".format(server))
