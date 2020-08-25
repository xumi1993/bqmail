from bqmail.mail import BQMail
from obspy import UTCDateTime

bq = BQMail('xxx@xxx.com', server='smtp.xxx.com', password='xxxxx', username='bqmail')
bq.query_events(starttime=UTCDateTime(2010, 1, 1), endtime=UTCDateTime(2010, 3, 1),
                minmagnitude=5.5, catalog='GCMT')
bq.query_stations(network='CB', station='*')
bq.send_mail(mark="P", time_before=-100, time_after=300, arrange='events')
