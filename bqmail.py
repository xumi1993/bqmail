#!/usr/bin/env python
#
#Author: Mijian Xu at NJU
#
#Revision History:
#   2014/11/06
#   2015/01/05
#   2015/02/11
#   2015/04/29
#   2015/05/01
#

def Usage():
    print('Usage:')
    print('python bqmail.py -Nnetwork -Sstation -Yyear1/month1/day1/year2/month2/day2 -Bsec_begin/sec_end -Cchannel -Llocation -cdatetimefile -Fformat head.cfg')
    print('-N   -- Network.')
    print('-S   -- Station.')
    print('-Y   -- Date range.')
    print('-B   -- Time before/after origal time of events in seconds.')
    print('-C   -- Channel (e.g., ?H?, HHZ, BH?). Default: BH?')
    print('-L   -- Location identifier.')
    print('-c   -- Directory of date time file. formaat: "2015,01,04,1,0,0 2015,01,04,10,0,0"')
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
    opts,args = getopt.getopt(sys.argv[1:], "hN:S:C:Y:B:L:c:F:")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)


iscustom = 0
isyrange = 0
chan = "BH?"
fformat = "seed"
loca = ''
for op, value in opts:
    if op == "-N":
        network = value
    elif op == "-S":
        station = value
    elif op == "-Y":
        yrange = value
        isyrange = 1
    elif op == "-c":
        datetimefile = value
        iscustom = 1
    elif op == "-B":
        timerange = value
    elif op == "-C":
        chan = value
    elif op == "-L":
        loca = value
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

event=[]
config.read(head)
eventlst = config.get("lst","eventlst")
NAME = config.get("info","NAME")
INST = config.get("info","INST")
EMAIL = config.get("info","EMAIL")
MEDIA = config.get("info","MEDIA")
ALTERNATEMEDIA = MEDIA
hosts = config.get("smtp","hosts")
port =  config.get("smtp","port")
passwd = config.get("smtp","passwd")
if fformat.lower() == 'seed':
    recipient = 'breq_fast@iris.washington.edu'
elif fformat.lower() == 'miniseed':
    recipient = 'miniseed@iris.washington.edu'
else:
    print('Invalid file format!')
    sys.exit(1)

if isyrange:
   LABEL = 'IRIS_'+str(year1)+"_"+str(year2)+"_"+network+"_"+station
else:
   LABEL = 'IRIS_'+network+"_"+station
   
if iscustom:
    EVENT = open(datetimefile,'r')
    for evenum in EVENT:
        evenum = evenum.strip('\n')
        evenum_sp = re.split('\W|\s',evenum)
        event.append(evenum_sp)
else:
    trange_sp = timerange.split('/')
    btime = float(trange_sp[0])
    etime = float(trange_sp[1])
    EVENT = open(eventlst,'r+')
    for evenum in EVENT:
        evenum_split = evenum.split()
        year=int(evenum_split[0])
        mon=int(evenum_split[1])
        day=int(evenum_split[2])
        jjj=int(evenum_split[3])
        hour=int(evenum_split[4])
        min=int(evenum_split[5])
        sec=float(evenum_split[6])
        lat=float(evenum_split[7])
        lon=float(evenum_split[8])
        dep=float(evenum_split[9])
        mw=float(evenum_split[10])
        date = datetime.datetime(year,mon,day,hour,min,sec) + datetime.timedelta(seconds=btime)
        dateend = datetime.datetime(year,mon,day,hour,min,sec) + datetime.timedelta(seconds=etime)
        if datemin <= date <= datemax:
            event.append([date.strftime('%Y'),date.strftime('%m'),date.strftime('%d'),date.strftime('%H'),date.strftime('%M'),date.strftime('%S'),dateend.strftime('%Y'),dateend.strftime('%m'),dateend.strftime('%d'),dateend.strftime('%H'),dateend.strftime('%M'),dateend.strftime('%S')])


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
for row in event:
    msg += station+' '+network+' '+row[0]+' '+row[1]+' '+row[2]+' '+row[3]+' '+row[4]+' '+row[5]+' '+row[6]+' '+row[7]+' '+row[8]+' '+row[9]+' '+row[10]+' '+row[11]+' 1 '+chan+' '+loca+'\n'

smtp = SMTP(host=hosts, port=port)
smtp.set_debuglevel(0)
smtp.login(EMAIL, passwd)
smtp.sendmail(EMAIL, recipient, msg)
smtp.quit()
print("Successful sending the mail of "+network+"."+station+" to IRIS DMC!!!")

