#!/usr/bin/env python
#
# Author: Mijian Xu at NJU
#
# Revision History:
#   2015/08/19
#   2015/09/23
#   2016/10/03


import datetime
import os, re
import sys, getopt
import time
import subprocess
from util import generatemsg, sendmail
try:
    import configparser
    config = configparser.ConfigParser()
except:
    import ConfigParser
    config = ConfigParser.ConfigParser()

def Usage():
    print('Usage:')
    print('python bqmail_conti.py -Istation.lst -Yyear1/month1/day1/year2/month2/day2 -Hhour [-Cchannel] [-Fformat] head.cfg')
    print('-I   -- Station list. format: Network station')
    print('-Y   -- Date range.')
    print('-C   -- Channel (e.g., ?H?, HHZ, BH?). Default: BH?')
    print('-H   -- Request continuous wave by hour.')
    print('-F   -- File format (SEED or miniseed). Default: SEED')
    print('head.cfg   -- Config file.')
    print('Example: ./bqmail_conti.py -Iex_sta.lst -Y2003/12/3/2003/12/4 -H24 head.cfg')


head = ''
argv = sys.argv[1:]
for o in argv:
    if os.path.isfile(o):
        print(o)
        head = o
        argv.remove(o)
        break
try:
    opts,args = getopt.getopt(argv, "hI:C:b:e::H:F:c:")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)
ops = [arg[0] for arg in opts]
chan = "BH?"
fformat = "seed"
isrange = True
for op, value in opts:
    if op == "-I":
        infile = value
    elif op == "-H":
        timeval = float(value)
    elif op == "-b":
        starttime = value
    elif op == "-e":
        endtime = value
    elif op == "-C":
        chan = value
    elif op == "-F":
        fformat = value
    elif op == "-c":
        datetimefile = value
        if not os.path.exists(datetimefile):
            print("No such file %s" % datetimefile)
            sys.exit(1)
        else:
            isrange = False
    elif op == "-h":
        Usage()
        sys.exit(1)
    else:
        Usage()
        sys.exit(1)

config.read(head)
eventlst = config.get("lst","eventlst")
NAME = config.get("info","NAME")
INST = config.get("info","INST")
EMAIL = config.get("info","EMAIL")
MEDIA = config.get("info","MEDIA")
ALTERNATEMEDIA = MEDIA
if fformat.lower() == 'seed':
    recipient = 'breq_fast@iris.washington.edu'
elif fformat.lower() == 'miniseed':
    recipient = 'miniseed@iris.washington.edu'
else:
    print('Invalid file format!')
    sys.exit(1)

sta = []
fid = open(infile,'r')
for stainfo in fid.readlines():
    stainfo = stainfo.strip()
    stainfo_sp = stainfo.split()
    if len(stainfo_sp) == 3:
        sta.append([stainfo_sp[0], stainfo_sp[1], stainfo_sp[2]])
    else:
        sta.append([stainfo_sp[0], stainfo_sp[1], ''])
fid.close()

if isrange:    
    if "T" in starttime:
        datemin = datetime.datetime.strptime(starttime,"%Y-%m-%dT%H:%M:%S")
    else:
        try:
            datemin = datetime.datetime.strptime(starttime,"%Y-%m-%d")
        except:
            print ("Wrong format in -b option")
            sys.exit(1)
    if "T" in endtime:
        datemax = datetime.datetime.strptime(endtime,"%Y-%m-%dT%H:%M:%S")
    else:
        try:
            datemax = datetime.datetime.strptime(endtime,"%Y-%m-%d")
        except:
            print ("Wrong format in -e option")
            sys.exit(1)
    nowtime = datemin
    while 1:
        if nowtime >= datemax:
            break
        endtime = nowtime + datetime.timedelta(hours=timeval)
        LABEL = 'IRIS_'+nowtime.strftime('%Y.%m.%d.%H')
        msg = generatemsg(NAME, INST, EMAIL, MEDIA, ALTERNATEMEDIA, LABEL)
        for sta_row in sta:
            msg += sta_row[1]+' '+sta_row[0]+' '+nowtime.strftime('%Y %m %d %H %M %S')+' '+endtime.strftime('%Y %m %d %H %M %S')+' 1 '+chan+' '+sta_row[2]+'\n'
        check_send = sendmail(recipient, msg)
        if check_send:
            print("Successful sending the mail from "+nowtime.strftime('%Y.%m.%d.%H')+" to "+endtime.strftime('%Y.%m.%d.%H')+"!!!")
            time.sleep(5)
        else:
            print("Some error occured")
else:
    with open(datetimefile) as f:
        datelst = [datetime.datetime.strptime(line.strip(), "%Y.%m.%d") for line in f.readlines()]
    for nowtime in datelst:
        endtime = nowtime + datetime.timedelta(hours=timeval)
        LABEL = "IRIS_"+nowtime.strftime('%Y.%m.%d.%H')
        msg = generatemsg(NAME, INST, EMAIL, MEDIA, ALTERNATEMEDIA, LABEL)
        for sta_row in sta:
            msg += sta_row[1]+' '+sta_row[0]+' '+nowtime.strftime('%Y %m %d %H %M %S')+' '+endtime.strftime('%Y %m %d %H %M %S')+' 1 '+chan+' '+sta_row[2]+'\n'
        check_send = sendmail(recipient, msg)
        if check_send:
            print("Successful sending the mail from "+nowtime.strftime('%Y.%m.%d.%H')+" to "+endtime.strftime('%Y.%m.%d.%H')+"!!!")
            time.sleep(5)
        else:
            print("Some error occured")





