#!/usr/bin/env python
#
#Author: Mijian Xu at NJU
#
#Revision History:
#   2015/08/19
#

def Usage():
    print('Usage:')
    print('python bqmail.py -Istation.lst -Yyear1/month1/day1/year2/month2/day2 -Cchannel -Hhour -Fformat head.cfg')
    print('-N   -- Station list. format: Network station')
    print('-Y   -- Date range.')
    print('-C   -- Channel (e.g., ?H?, HHZ, BH?). Default: BH?')
    print('-H   -- Request continuous wave by hour.')
    print('-F   -- File format (SEED or miniseed). Default: SEED')
    print('head.cfg   -- Config file.')
    print('Example: ./bqmail.py -NCB -SNJ2 -Y2015/2/3/2015/4/3 -B0/1000 head.cfg')
    print('         ./bqmail.py -NCB -SNJ2 -Y2015/2/3/2015/4/3 -s1 -Fminiseed head.cfg')


import datetime
import os, re
import sys, getopt
from smtplib import SMTP
try:
    import configparser
    config = configparser.ConfigParser()
except:
    import ConfigParser
    config = ConfigParser.ConfigParser()


try:
    opts,args = getopt.getopt(sys.argv[1:], "hI:C:Y:H:F:")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)
chan = "BH?"
fformat = "seed"
for op, value in opts:
    if op == "-I":
        infile = value
    elif op == "-H":
        timeval = float(value)
    elif op == "-Y":
        yrange = value
        isyrange = 1
    elif op == "-C":
        chan = value
    elif op == "-F":
        fformat = value
    elif op == "-h":
        Usage()
        sys.exit(1)
    else:
        Usage()
        sys.exit(1)

head = []
for o in sys.argv[1:]:
    if os.path.isfile(o):
        head = o
        break
if head == []:
    print("Head file are not exist!")
    Usage()
    sys.exit(1)
    
if isyrange:
   y_split = yrange.split('/')
   year1 = int(y_split[0])
   mon1 = int(y_split[1])
   day1 = int(y_split[2])
   year2 = int(y_split[3])
   mon2 = int(y_split[4])
   day2 = int(y_split[5])
   datemin=datetime.datetime(year1,mon1,day1)
   datemax=datetime.datetime(year2,mon2,day2)


config.read(head)
eventlst = config.get("lst","eventlst")
NAME = config.get("info","NAME")
INST = config.get("info","INST")
EMAIL = config.get("info","EMAIL")
MEDIA = config.get("info","MEDIA")
ALTERNATEMEDIA = config.get("info","ALTERNATEMEDIA")
hosts = config.get("smtp","hosts")
port =  config.get("smtp","port")
passwd = config.get("smtp","passwd")
recipient = 'breq_fast@iris.washington.edu'

sta = []
fid = open(infile,'r')
for stainfo in fid.readlines():
    stainfo = stainfo.strip()
    stainfo_sp = stainfo.split()
    sta.append([stainfo_sp[0], stainfo_sp[1]])

smtp = SMTP(host=hosts, port=port)
smtp.set_debuglevel(0)
smtp.login(EMAIL, passwd)


nowtime = datemin
while 1:
    if nowtime >= datemax:
        break
    endtime = nowtime + datetime.timedelta(hours=timeval)
    LABEL = 'IRIS_'+nowtime.strftime('%Y')+'.'+nowtime.strftime('%m')+'.'+nowtime.strftime('%d')+'.'+nowtime.strftime('%H')
    head = ("From: %s\r\nTo: %s\r\n\r\n" % (EMAIL, recipient))
    msg = head
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
    for sta_row in sta:
        msg += sta_row[1]+' '+sta_row[0]+' '+nowtime.strftime('%Y')+' '+nowtime.strftime('%m')+' '+nowtime.strftime('%d')+' '+nowtime.strftime('%H')+' '+nowtime.strftime('%M')+' 00.0 '+endtime.strftime('%Y')+' '+endtime.strftime('%m')+' '+endtime.strftime('%d')+' '+endtime.strftime('%H')+' '+endtime.strftime('%M')+' 00.0 1 '+chan+'\n'
    if fformat.lower() == 'seed':
        smtp.sendmail(EMAIL, 'breq_fast@iris.washington.edu', msg)
    elif fformat.lower() == 'miniseed':
        smtp.sendmail(EMAIL, 'miniseed@iris.washington.edu', msg)
    else:
        print('Invalid file format!')
        sys.exit(1)
    print("Successful sending the mail between "+nowtime.strftime('%Y')+'.'+nowtime.strftime('%m')+'.'+nowtime.strftime('%d')+'.'+nowtime.strftime('%H')+" and "+endtime.strftime('%Y')+'.'+endtime.strftime('%m')+'.'+endtime.strftime('%d')+'.'+endtime.strftime('%H')+"!!!")
    nowtime = nowtime + datetime.timedelta(hours=timeval)    
smtp.quit()
