#!/usr/bin/env python
#
# Author: Mijian Xu at NJU
#
# Revision History:
#   2014/11/06
#   2015/01/05
#   2015/02/11
#   2015/04/29
#   2015/07/19
#   2015/09/26
#

import distaz, math
try:
    import urllib.request as rq
except:
    import urllib as rq
import os
import re
import sys, getopt
import glob

def Usage():
    print('Usage: python searchDMC.py -NNetwork -Sstation -Rlon1/lon2/lat1/lat2 -Dlat/lon/dis1/dis2 -Yyear1/mon1/day1/year2/mon2/day2 -Cchannel -K -G')
    print('-N   -- Network.')
    print('-S   -- Station.')
    print('-R   -- Search range.')
    print('-D   -- Search by distance.')
    print('-Y   -- Date range')
    print('-C   -- Channel (e.g., BHZ)')
    print('-K   -- Output Google Earth kml file.')
    

try:
    opts,args = getopt.getopt(sys.argv[1:], "hR:D:KY:C:N:S:G")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)

iskml = 0
islalo = 0
isyrange = 0
isgmt = 0
lat_lon = ''
yrange = ''
chan = ''
network = ''
station = ''
lalo_label = ''
for op, value in opts:
    if op == "-R":
        lat_lon = value
        islalo = 1
    elif op == "-N":
        network = 'net='+value+'&'
    elif op == "-S":
        station = 'sta='+value+'&'
    elif op == "-K":
        iskml = 1
    elif op == "-D":
        lat_lon = value
    elif op == "-Y":
        yrange = value
        isyrange = 1
    elif op == "-C":
        chan = 'chan='+value+'&'
    elif op == "-G":
        isgmt = 1
    elif op == "-h":
        Usage()
        sys.exit(1)
    else:
        Usage()
        sys.exit(1)

if lat_lon != '':
    lat_lon_split = lat_lon.split('/')    
    if islalo:
        lon1 = lat_lon_split[0]
        lon2 = lat_lon_split[1]
        lat1 = lat_lon_split[2]
        lat2 = lat_lon_split[3]
        lalo = lon1+'_'+lon2+'_'+lat1+'_'+lat2
        lalo_label = 'minlat='+lat1+'&maxlat='+lat2+'&minlon='+lon1+'&maxlon='+lon2+'&'
    else:
        lon = lat_lon_split[1]
        lat = lat_lon_split[0]
        dis1 = float(lat_lon_split[2])
        dis2 = float(lat_lon_split[3])
        lon1 = str(0)
        lat1 = str(-90)
        lon2 = str(0)
        lat2 = str(90)
        lalo = lon+'_'+lat+'_'+lat_lon_split[2]
        lalo_label = 'minlat='+lat1+'&maxlat='+lat2+'&minlon='+lon1+'&maxlon='+lon2+'&'

url = 'http://ds.iris.edu/cgi-bin/xmlstationinfo?'
if isyrange:
    yrange_sp = yrange.split("/")
    year1 = yrange_sp[0]
    mon1 = yrange_sp[1]
    day1 = yrange_sp[2]
    year2 = yrange_sp[3]
    mon2 = yrange_sp[4]
    day2 = yrange_sp[5]
    yrange = 'timewindow='+year1+'/'+mon1+'/'+day1+'-'+year2+'/'+mon2+'/'+day2+'&'

url += network+station+lalo_label+yrange+chan+'archive=on'

response = rq.urlopen(url)
html = str(response.read())
find_re = re.compile(r'<station\s.+?"/>',re.DOTALL)
stations = []
for info in find_re.findall(html):
    sta_info = re.split('\w+="|"\s+?\w+="|"\s/>',info)
    if sta_info == []:
        continue
    netname = sta_info[1]
    staname = sta_info[2]
    stlat = sta_info[4]
    stlon = sta_info[5]
    if sta_info[-2] == 'No archive data':
        continue
    yrange1 = sta_info[-5]
    yrange2 = sta_info[-4]
    if not islalo and lat_lon != '':
        delta = distaz.distaz(float(lat),float(lon),float(stlat),float(stlon))
        if dis1 < delta.delta < dis2:
            stations.append([netname, staname, float(stlat), float(stlon), yrange1, yrange2])           
    else:
        stations.append([netname, staname, float(stlat), float(stlon), yrange1, yrange2])       
for sta_r in stations:
    print('%s %s %5.2f %5.2f %s %s' % (sta_r[0], sta_r[1], sta_r[2], sta_r[3], sta_r[4], sta_r[5]))

if isgmt:
    with open('Stations.gmt', 'w+') as gmt:
        if not islalo and lat_lon != '':
            center = [float(lat), float(lon)]            
        elif islalo:
            center = [(float(lat1)+float(lat2))/2, (float(lon1)+float(lon2))/2]
        else:
            netlats = []
            netlons = []
            for sta in stations:
                netlats.append(sta[2])
                netlons.append(sta[3])
            center = [(max(netlats)+min(netlats))/2, (max(netlons)+min(netlons))/2]
        gmt.write('#!/bin/sh\n')
        gmt.write('ps=stations.ps\n\n')
        gmt.write('gmt pscoast -Rg -JN0/10i -Ba30 -Dc -A10000 -Glightgray -Wthinnest -K > $ps\n' % (center[1], center[0]))
        gmt.write('gmt psxy -R -K -O -J -St0.03i -Gred3 -W0.3p >> $ps << eof\n')
        for sta in stations:
            gmt.write('%5.2f %5.2f\n' % (sta[3], sta[2]))
        gmt.write('eof\n')


if iskml:
    if network != '':
        Knetwork = network+'amp;'
        netname = re.split('[=|&]', network)[1]
    else:
        Knetwork = network
    if station != '':
        Kstation = station+'amp;'
    else:
        Kstation = station
    if yrange != '':
        Kyrange = yrange+'amp;'
    else:
        Kyrange = yrange
    if chan != '':
        Kchan = chan+'amp;'
    else:
        Kchan = chan
    if islalo:
        href = 'http://www.iris.edu/cgi-bin/kmlstationinfo?minlat='+lat1+'&amp;maxlat='+lat2+'&amp;minlon='+lon1+'&amp;maxlon='+lon2+'&amp;'+Knetwork+Kstation+Kyrange+Kchan+'kmz=1'
        with open('Station_'+lalo+'.kml','w+') as google:
            google.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.google.com/earth/kml/2.0"><NetworkLink><name>Selected stations</name><description>Station List</description><Link><href>'+href+'</href><refreshMode>onInterval</refreshMode><refreshInterval>86400</refreshInterval></Link></NetworkLink></kml>')
        print('Seccessfully create the Google Earth file: Station_'+lalo+'.kml')
    else:
        try:
            href = 'http://www.iris.edu/cgi-bin/kmlstationinfo?'+Knetwork+Kstation+Kyrange+Kchan+'kmz=1'
            with open('Station_'+netname+'.kml','w+') as google:
                google.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.google.com/earth/kml/2.0"><NetworkLink><name>Selected stations</name><description>Station List</description><Link><href>'+href+'</href><refreshMode>onInterval</refreshMode><refreshInterval>86400</refreshInterval></Link></NetworkLink></kml>')
            print('Seccessfully create the Google Earth file: Station_'+netname+'.kml')
        except:
            print('Cannot creat the .kml file, "-R" or "-N" is required.')
  
