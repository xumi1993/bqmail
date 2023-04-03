from bqmail.mail import BQMail
from obspy import UTCDateTime

bq = BQMail('gomijianxu@163.com', server='smtp.163.com', password='UYBECNASZQWCDFNF', username='mijian')
bq.query_events(starttime=UTCDateTime(2009, 6, 1), endtime=UTCDateTime(2019, 1, 1),
                minmagnitude=5.8, catalog='GCMT', latitude=0, longitude=100, minradius=25, maxradius=95)
bq.query_stations(network='MS', minlatitude=-6, maxlatitude=6.8, minlongitude=94, maxlongitude=107.4, channel='BH?', location='02')
bq.send_mail(time_before=0, time_after=1000, arrange='events')
