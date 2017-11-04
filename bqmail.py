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
#   2015/09/26
#   2015/11/06
#   2017/09/11
#

def Usage():
    print('Usage:')
    print('python bqmail.py -Nnetwork -Sstation -b -Bsec_begin/sec_end [-Cchannel] [-Plat/lon/phase] [-Llocation] [-cdatetimefile] [-Fformat] [-Mmagmin/magmax] head.cfg')
    print('-N   -- Network.')
    print('-S   -- Station.')
    print('-b   -- Limit to events occurring on or after the specified start time.\n'
          '        Date and time format: YYYY-MM-DDThh:mm:ss (e.g., 1997-01-31T12:04:32)\n'
          '                              YYYY-MM-DD (e.g., 1997-01-31)')
    print('-e   -- Limit to events occurring on or before the specified end time\n'
          '        with the same date and time format as \"-b\".')
    print('-B   -- Time before/after origal time of events in seconds.')
    print('-C   -- Channel (e.g., ?H?, HHZ, BH?). Default: BH?')
    print('-P   -- specify the lat/lon of station and require data by phase. e.g., 20/100/SKS')
    print('-L   -- Location identifier.')
    print('-c   -- Directory of date time file. format: "2015,01,04,1,0,0 2015,01,04,10,0,0"')
    print('-F   -- File format (SEED or miniseed). Default: SEED')
    print('-M   -- Magnitude range.')
    print('head.cfg   -- Config file.')
    print('Example: bqmail -NCB -SNJ2 -b2015-2-3 -e2015-4-3 -P32.05/118.85/P -B-200/1000 head.cfg')
    print('         bqmail -NIC -SBJT -b2015-2-3T00:12:23 -e2015-4-3 -B-100/600 -L10 -Fminiseed head.cfg')


import datetime
import os, re
import sys, getopt
import time
from obspy import taup
import distaz
from util import sendmail,generatemsg
try:
    import configparser
    config = configparser.ConfigParser()
except:
    import ConfigParser
    config = ConfigParser.ConfigParser()

head = ''
argv = sys.argv[1:]
for o in argv:
    if os.path.isfile(o):
        head = o
        argv.remove(o)
        break

try:
    opts,args = getopt.getopt(argv, "hN:S:C:b:e:B:L:c:F:P:M:")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)

isph = 0
isyrange = 1
chan = "BH?"
fformat = "seed"
loca = ''
magmin = 0
magmax = 10
for op, value in opts:
    if op == "-N":
        network = value
    elif op == "-S":
        station = value
    elif op == "-b":
        starttime = value
    elif op == "-e":
        endtime = value
    elif op == "-c":
        datetimefile = value
        isyrange = 0
    elif op == "-B":
        timerange = value
    elif op == "-C":
        chan = value
    elif op == "-L":
        loca = value
    elif op == "-F":
        fformat = value
    elif op == "-P":
        stla = float(value.split('/')[0])
        stlo = float(value.split('/')[1])
        phase = value.split('/')[2]
        isph = 1
        mod=taup.TauPyModel(model='iasp91')
    elif op == "-M":
        magmin = float(value.split('/')[0])
        magmax = float(value.split('/')[1])
    elif op == "-h":
        Usage()
        sys.exit(1)
    else:
        Usage()
        sys.exit(1)

if head == '':
    print("Head file are not exist!")
    Usage()
    sys.exit(1)

ops = [op for op, value in opts]
if '-b' in ops and '-e' in ops:
    isyrange = 1
elif '-c' in ops:
    isyrange = 0
else:
    print('-b and -e must be set at same time otherwise please set -c as custom')
    sys.exit(1)

if isyrange:
    if "T" in starttime:
        strfmt = "%Y-%m-%dT%H:%M:%S"
    else:
        strfmt = "%Y-%m-%d"
    try:
        datemin = datetime.datetime.strptime(starttime,strfmt)
    except:
        print("Wrong format in -b option")
        sys.exit(1)
    if "T" in endtime:
        strfm = "%Y-%m-%dT%H:%M:%S"
    else:
        strfmt = "%Y-%m-%d"
    try:
        datemax = datetime.datetime.strptime(endtime,strfmt)
    except:
        print("Wrong format in -e option")
        sys.exit(1)

event=[]
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

if isyrange:
   LABEL = 'IRIS_'+datemin.strftime('%Y')+"_"+datemax.strftime('%Y')+"_"+network+"_"+station
else:
   LABEL = 'IRIS_'+network+"_"+station

if not isyrange:
    EVENT = open(datetimefile,'r')
    for evenum in EVENT.readlines():
        evenum = evenum.strip('\n')
        evenum_sp = re.split('\W|\s',evenum)
        date_beg = datetime.datetime(int(evenum_sp[0]),int(evenum_sp[1]),int(evenum_sp[2]),int(evenum_sp[3]),int(evenum_sp[4]),int(evenum_sp[5]))
        date_end = datetime.datetime(int(evenum_sp[6]),int(evenum_sp[7]),int(evenum_sp[8]),int(evenum_sp[9]),int(evenum_sp[10]),int(evenum_sp[11]))
        event.append([date_beg.strftime('%Y %m %d %H %M %S'), date_end.strftime('%Y %m %d %H %M %S')])
else:
    trange_sp = timerange.split('/')
    btime = float(trange_sp[0])
    etime = float(trange_sp[1])
    EVENT = open(eventlst,'r')
    for evenum in EVENT:
        evenum = evenum.strip()
        (year, mon, day, jjj, hour, min, sec, lat, lon, dep, mw) = evenum.split()
        year = int(year)
        mon = int(mon)
        day = int(day)
        jjj = int(jjj)
        hour = int(hour)
        min = int(min)
        sec = int(sec)
        lat = float(lat)
        lon = float(lon)
        dep = float(dep)
        mw = float(mw)
        if mw < magmin or mw > magmax:
            continue
        evt_time = datetime.datetime(year,mon,day,hour,min,sec)
        if datemin <= evt_time <= datemax:
            if isph == 1:
                dis = distaz.distaz(stla, stlo, lat, lon).delta
                arr = mod.get_travel_times(source_depth_in_km=dep, distance_in_degree=dis, phase_list=[phase])
                if len(arr) != 0:
                    arr_time = evt_time + datetime.timedelta(seconds=arr[0].time)
                    date = arr_time + datetime.timedelta(seconds=btime)
                    dateend = arr_time + datetime.timedelta(seconds=etime)
            else:
                date = evt_time + datetime.timedelta(seconds=btime)
                dateend = evt_time + datetime.timedelta(seconds=etime)
            event.append([date.strftime('%Y %m %d %H %M %S'), dateend.strftime('%Y %m %d %H %M %S')])
    if event == []:
        print('No events found in the range')

msg = generatemsg(NAME, INST, EMAIL, MEDIA, ALTERNATEMEDIA, LABEL)
for row in event:
    msg += station+' '+network+' '+row[0]+' '+row[1]+' 1 '+chan+' '+loca+'\n'
try:
    sendmail(recipient, msg)
    print("Successful sending the mail of "+network+"."+station+" to IRIS DMC!!!")
    time.sleep(4)
except:
    print('ERROR in sending mail')
    sys.exit(1)
