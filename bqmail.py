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
#

def Usage():
    print('Usage:')
    print('python bqmail.py -Nnetwork -Sstation -Yyear1/month1/day1/year2/month2/day2 -Bsec_begin/sec_end [-Cchannel] [-Plat/lon/phase] [-Llocation] [-cdatetimefile] [-Fformat] [-Mmagmin/magmax] head.cfg')
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
    print('         ./bqmail.py -NIC -SBJT -Y2015/2/3/2015/4/3 -B-100/600 -L10 -Fminiseed head.cfg')


import datetime
import os, re
import sys, getopt
import time
import taup
import distaz
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
    opts,args = getopt.getopt(argv, "hN:S:C:Y:B:L:c:F:P:M:")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)

isph = 0
iscustom = 0
isyrange = 0
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
        sec=int(evenum_split[6])
        lat=float(evenum_split[7])
        lon=float(evenum_split[8])
        dep=float(evenum_split[9])
        mw=float(evenum_split[10])
        if mw < magmin or mw > magmax:
            continue
        evt_time = datetime.datetime(year,mon,day,hour,min,sec)
        if datemin <= evt_time <= datemax:
            if isph == 1:
                dis = distaz.distaz(stla, stlo, lat, lon).delta
                arr = mod.get_travel_times(source_depth_in_km=dep, distance_in_degree=dis, phase_list=[phase])
                if len(arr) != 0:
                    arr_time = evt_time + datetime.timedelta(seconds=arr[0].time)
                    date = arr_time - datetime.timedelta(seconds=btime)
                    dateend = arr_time + datetime.timedelta(seconds=etime)
            else:
                date = evt_time + datetime.timedelta(seconds=btime)
                dateend = evt_time + datetime.timedelta(seconds=etime)
            event.append([date.strftime('%Y %m %d %H %M %S'), dateend.strftime('%Y %m %d %H %M %S')])
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
for row in event:
    msg += station+' '+network+' '+row[0]+' '+row[1]+' 1 '+chan+' '+loca+'\n'
with open('tmp.bq','w') as fid_msg:
    fid_msg.write(msg)
os.system('mail '+recipient+'<tmp.bq')
print("Successful sending the mail of "+network+"."+station+" to IRIS DMC!!!")
os.system('rm tmp.bq')
time.sleep(4)

