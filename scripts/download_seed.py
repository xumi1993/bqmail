#!/usr/bin/env python
#
# Download seed file from IRIS DMC. Duplicate files from server would be check.
#
# Author: Mijian Xu @ Nanjing University
# 
# History: 2016-09-29, Init Code, Mijian Xu
# 

import os
try:
    import urllib.request as rq
except:
    import urllib as rq
import re
from multiprocessing.dummy import Pool as ThreadPool 
import subprocess
import sys
import getopt

def Usage():
    print("Usage: download_seed.py  -u<user-name> [-n<thread-num>] [-P<out-path>] [filename]")
    print("    -P Specify out path of downloaded seed files.")
    print("       Default: current dirctory")
    print("    -n Specify thread number at parallel downloading")
    print("    -u Specify username in user directory on the IRIS.")

def wget(url_path):
    url = url_path[0]
    path = url_path[1]
    resp = subprocess.Popen("wget -c -nc -P "+path+" "+url, shell=True)
    resp.wait()

thread = 1
argv = sys.argv[1:]
if argv == []:
    Usage()
    sys.exit(1)
path = "./"
filename = None
try:
    opts, args = getopt.getopt(argv, "u:n:P:")
except:
    print("Arguments are not found!")
    Usage()
    sys.exit(1)
for op, value in opts:
    if op == "-n":
        thread = int(value)
    elif op == "-u":
        username = value
    elif op == "-P":
        path = value
    else:
        Usage()
        sys.exit(1)

for op in argv:
    if op[0] != '-':
        thread = 1
        filename = op

url = "http://ds.iris.edu/pub/userdata/"+username
html = rq.urlopen(url)
content = html.read().decode()
lst = []
print(filename)
if filename == None:
    find_re = re.compile(r'href=".+?">',re.DOTALL)
    for line in find_re.findall(content):
        if line.find("mseed") > 0:
            lst.append(line[6:-2])
else:
    lst.append(filename)
lstpath = os.path.join(os.path.expanduser("~"),".IRIS.lst")
if os.path.exists(lstpath):
    with open(lstpath, "r+") as f:
        oldlst = [line.strip() for line in f.readlines()]
else:
    oldlst = []
with open(lstpath, "w+") as f:
    for line in lst:
        f.write(line+"\n")
same_item = list(set(oldlst) & set(lst))

for item in same_item:
    lst.remove(item)
if lst == []:
    print("The whole date were downloaded from IRIS DMC.")
    sys.exit(1)
link_lst = [[url+"/"+line, path] for line in lst]
pool = ThreadPool(thread)
print("start downloading")
results = pool.map(wget, link_lst)
pool.close() 
pool.join()

    
