#!/usr/bin/env python
#
# This is a example of bqmail for request data from network YA.


import os

network = 'YA'
for sta in os.popen('matchsta.py -N'+network+' -R95/110/20/40'):
    sta_sp = sta.split()
    staname = sta_sp[0]
    date_begin = sta_sp[4]
    date_end = sta_sp[5]
    os.system('bqmail -NYA -S'+staname+' -Y'+date_begin+'/'+date_end+' head.cfg')
