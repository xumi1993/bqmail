#!/usr/bin/env python
#
#
#
import urllib.request as rq
import os
import re
import sys, getopt

def Usage():
    print('Usage:')
    print('python matchsta.py -Nnetwork -Rlon1/lon2/lat1/lat2 -K > network.lst')



try:
    opts,args = getopt.getopt(sys.argv[1:], "hN:R:K")
except:
    print('arguments are not found!')
    Usage()
    sys.exit(1)

islalo = 0
ismap = 0
for op, value in opts:
    if op == "-N":
        network = value
    elif op == "-R":
        lat_lon = value
        islalo = 1
    elif op == "-K":
        ismap = 1
    elif op == "-h":
        Usage()
        sys.exit(1)
    else:
        Usage()
        sys.exit(1)

if islalo:
    lalo_split = lat_lon.split('/')
    lon1 = float(lalo_split[0])
    lon2 = float(lalo_split[1])
    lat1 = float(lalo_split[2])
    lat2 = float(lalo_split[3])


url = 'http://ds.iris.edu/mda/'+network
response = rq.urlopen(url)
html = str(response.read())
find_re = re.compile(r'TITLE.+?</A></TD>.+?</TR>',re.DOTALL)


for info in find_re.findall(html):
    find_sta = re.compile('\w+</A></TD>.+?</TR>',re.DOTALL)
    sta_info = find_sta.findall(info)
    if sta_info == []:
        continue
    sta_info = sta_info[0]
    info_s1 = sta_info.split('<')
    staname = info_s1[0]
    info_s2 = re.split('</TD>.+?>',sta_info)
    stlat = float(info_s2[2])
    stlon = float(info_s2[3])
    stel = float(info_s2[4])
    yrange1 = info_s2[5]
    yrange2 = info_s2[6]
    if islalo:
        if lat1<=stlat<=lat2 and lon1<=stlon<=lon2:
            print(staname+' '+str(stlat)+' '+str(stlon)+' '+info_s2[4]+' '+yrange1+' '+yrange2)            
    else:
        print(staname+' '+str(stlat)+' '+str(stlon)+' '+info_s2[4]+' '+yrange1+' '+yrange2)

if ismap:
    google = open(network+'.kml','w+')
    google.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.google.com/earth/kml/2.0"><NetworkLink><name>Selected stations</name><description>'+network+'</description><Link><href>http://www.iris.edu/cgi-bin/kmlstationinfo/'+network+'</href><refreshMode>onInterval</refreshMode><refreshInterval>86400</refreshInterval></Link></NetworkLink></kml>')
   


