from bqmail.mail import BQMail
from obspy import UTCDateTime

bq = BQMail('xxx@xxx.com', server='smtp.xxx.com', password='xxxxxx', username='bqmail')
bq.query_events(starttime=UTCDateTime(2003, 1, 1), endtime=UTCDateTime(2004, 12, 31),
                minmagnitude=5.5, catalog='GCMT', latitude=40, longitude=118.3389, minradius=25, maxradius=95)
bq.query_stations(network='ZX', station='2*')
bq.send_mail(mark="P", time_before=-100, time_after=300, arrange='events', write_evtinfo=True)
