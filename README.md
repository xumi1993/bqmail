# BQMail


**BQMail** is a Python module for sending mails to apply for seismic data from the IRIS DMC. It is a front-end API of the BREQ_fast.

## Installation
**BQMail** can currently run on Linux and MAC OSX. **BQMail** is running and testing on Python 3.7.
### Installation via PyPI
```
pip install bqmail
```

### Installation from source code
The latest version of the **BQMail** is available on Gitlab:
```
git clone https://git.nju.edu.cn/xumi1993/bqmail2.0.git bqmail
``` 
Then you can install this version:
```
cd bqmail
pip install .
```

## A quick example:
```python
from bqmail.mail import BQMail
from obspy import UTCDateTime

bq = BQMail('xxx@163.com', server='smtp.163.com', password='xxx', username='bqmail')
bq.query_events(starttime=UTCDateTime(2017, 1, 1), endtime=UTCDateTime(2018, 1, 1),
                minmagnitude=5.5, catalog='GCMT')
bq.query_stations(network='CB', station='LZH')
bq.send_mail(time_before=0, time_after=1000)
```