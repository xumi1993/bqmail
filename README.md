# BQMail
[![PyPI](https://img.shields.io/pypi/v/bqmail)](https://pypi.org/project/bqmail/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bqmail)]()
[![PyPI - License](https://img.shields.io/pypi/l/bqmail)]()
[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/xumi1993/bqmail)](https://github.com/xumi1993/bqmail/tags)

![GitHub forks](https://img.shields.io/github/forks/xumi1993/bqmail?style=social)
![GitHub stars](https://img.shields.io/github/stars/xumi1993/bqmail?style=social)

**BQMail** is a Python module for sending mails to apply for seismic data from the [IRIS DMC](http://www.ds.iris.edu/ds/nodes/dmc/). It is a front-end API of the [BREQ_fast](http://ds.iris.edu/ds/nodes/dmc/manuals/breq_fast/).

For **Chinese users**, please refer to our [chinese blog](https://blog.xumijian.me/tags/bqmail/).
## Installation
**BQMail** can currently run on Linux and MAC OSX. **BQMail** is running and testing on Python 3.9/3.10/3.11.

### Installation via PyPI
```
pip install bqmail
```

### Installation from source code
The latest version of the **BQMail** is available on Gitlab:
```
git clone https://github.com/xumi1993/bqmail.git bqmail
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

bq = BQMail('xxx@xxx.com', server='smtp.xxx.com', password='xxx', username='bqmail')
bq.query_events(starttime=UTCDateTime(2017, 1, 1), endtime=UTCDateTime(2018, 1, 1),
                minmagnitude=5.5, catalog='GCMT')
bq.query_stations(network='CB', station='LZH')
bq.send_mail(time_before=0, time_after=1000)
```
