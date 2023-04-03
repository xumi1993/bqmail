from obspy.clients.fdsn import Client
from obspy import UTCDateTime, Catalog
from datetime import timedelta
import pandas as pd
import argparse
import sys


def _cat2df(cat):
    cols = ['date', 'evla', 'evlo', 'evdp', 'mag', 'magtype', 'region_name']
    data = [[evt.origins[0].time, evt.origins[0].latitude, 
             evt.origins[0].longitude, evt.origins[0].depth*0.001,
             evt.magnitudes[0].mag, evt.magnitudes[0].magnitude_type,
             evt.event_descriptions[0].text] for evt in cat if evt.origins[0].depth is not None]
    return pd.DataFrame(data, columns=cols)


class Query():
    def __init__(self):
        self.client = Client("IRIS")

    def get_events(self, starttime=UTCDateTime(2000, 1, 1),
                   endtime=UTCDateTime.now(), **kwargs):
        events = Catalog()
        if endtime-starttime < 365 * 86400:
            events += self.client.get_events(starttime=starttime,
                                            endtime=endtime,
                                            orderby='time-asc', **kwargs)
        else:
            chunk_length = 365 * 86400
            while starttime <= endtime:
                if endtime-starttime < chunk_length:
                    nowtime = endtime
                else:
                    nowtime=starttime + chunk_length
                try:
                    events += self.client.get_events(starttime=starttime,
                                                endtime=nowtime,
                                                orderby='time-asc', **kwargs)
                except:
                    starttime += chunk_length
                    continue
                if starttime + chunk_length > endtime:
                    chunk = endtime - starttime
                    if chunk <= 1:
                        break
                starttime += chunk_length
            
        self.events = _cat2df(events)

    def get_stations(self, includerestricted=False, **kwargs):
        self.stations = self.client.get_stations(includerestricted=includerestricted, **kwargs)

    def get_conti(self, starttime, endtime, hours=24):
        self.conti_time = []
        nowtime = starttime
        while nowtime < endtime:
            nexttime = nowtime + timedelta(hours=hours)
            self.conti_time.append([nowtime, nexttime])
            nowtime = nexttime


def get_events():
    parser = argparse.ArgumentParser(description="Get seismic events from IRIS WS")
    parser.add_argument('-b', help='Start time', type=str, default=None)
    parser.add_argument('-e', help='End time', type=str, default=None)
    parser.add_argument('-d', help='Radial geographic constraints with <lat>/<lon>/<minradius>/<maxradius>', type=str, default=None)
    parser.add_argument('-r', help='Box range with <lon1>/<lon2>/<lat1>/<lat2>', type=str, default=None)
    parser.add_argument('-m', help='Magnitude <minmagnitude>[/<maxmagnitude>]', type=str, default=None)
    parser.add_argument('-p', help='Focal depth <mindepth>[/<maxdepth>]', type=str, default=None)
    parser.add_argument('-c', help='Catalog', type=str, default=None)
    arg = parser.parse_args()
    args = {}
    if arg.c is not None:
        args['catalog'] = arg.c
    if arg.p is not None:
        try:
            values = [float(value) for value in arg.p.split('/')]
        except:
            raise ValueError('Error format with focal depth')
        if len(values) == 1:
            args['mindepth'] = values[0]
        elif len(values) == 2:
            args['mindepth'] = values[0]
            args['maxdepth'] = values[1]
        else:
            raise ValueError('Error format with focal depth')
    if arg.m is not None:
        try:
            values = [float(value) for value in arg.m.split('/')]
        except:
            raise ValueError('Error format with magnitude')
        if len(values) == 1:
            args['minmagnitude'] = values[0]
        elif len(values) == 2:
            args['minmagnitude'] = values[0]
            args['maxmagnitude'] = values[1]
        else:
            raise ValueError('Error format with focal depth')
    if arg.r is not None:
        try:
            values = [float(value) for value in arg.r.split('/')]
        except:
            raise ValueError('Error format with box range')
        if len(values) == 4:
            args['minlongitude'] = values[0]
            args['maxlongitude'] = values[1]
            args['minlatitude'] = values[2]
            args['maxlatitude'] = values[3]
        else:
            raise ValueError('Error format with box range')
    elif arg.d is not None:
        try:
            values = [float(value) for value in arg.d.split('/')]
        except:
            raise ValueError('Error format with Radial geographic constraints')
        if len(values) == 4:
            args['latitude'] = values[0]
            args['longitude'] = values[1]
            args['minradius'] = values[2]
            args['maxradius'] = values[3]
        else:
            raise ValueError('Error format with radial geographic constraints')
    else:
        pass
    if arg.b is not None:
        try:
            args['starttime'] = UTCDateTime(arg.b)
        except:
            raise ValueError('-b: Error format with time string')
    if arg.e is not None:
        try:
            args['endtime'] = UTCDateTime(arg.e)
        except:
            raise ValueError('-e: Error format with time string')
    if args == {}:
        parser.print_usage()
        sys.exit(1)
    query = Query()
    query.get_events(**args)
    for i, row in query.events.iterrows():
        print('{} {:.2f} {:.2f} {:.2f} {:.1f} {}'.format(
              row.date.isoformat(), row.evla, row.evlo, row.evdp, row.mag, row.magtype))


def get_stations():
    parser = argparse.ArgumentParser(description="Get stations from IRIS WS")
    parser.add_argument('-n', help='Network', type=str, default=None)
    parser.add_argument('-s', help='Station', type=str, default=None)
    parser.add_argument('-r', help='Box range with <lon1>/<lon2>/<lat1>/<lat2>', type=str, default=None)
    parser.add_argument('-d', help='Radial geographic constraints with <lat>/<lon>/<minradius>/<maxradius>', type=str, default=None)
    parser.add_argument('-b', help='Start time', type=str, default=None)
    parser.add_argument('-e', help='End time', type=str, default=None)
    parser.add_argument('-c', help='Channel', type=str, default=None)
    arg = parser.parse_args()
    args = {}
    if arg.n is not None:
        args['network'] = arg.n
    if arg.s is not None:
        args['station'] = arg.s
    if arg.r is not None:
        try:
            values = [float(value) for value in arg.r.split('/')]
        except:
            raise ValueError('Error format with box range')
        if len(values) == 4:
            args['minlongitude'] = values[0]
            args['maxlongitude'] = values[1]
            args['minlatitude'] = values[2]
            args['maxlatitude'] = values[3]
        else:
            raise ValueError('Error format with box range')
    elif arg.d is not None:
        try:
            values = [float(value) for value in arg.d.split('/')]
        except:
            raise ValueError('Error format with Radial geographic constraints')
        args['latitude'] = values[0]
        args['longitude'] = values[1]
        args['minradius'] = values[2]
        args['maxradius'] = values[3]
    else:
        pass
    if arg.b is not None:
        try:
            args['starttime'] = UTCDateTime(arg.b)
        except:
            raise ValueError('-b: Error format with time string')
    if arg.e is not None:
        try:
            args['endtime'] = UTCDateTime(arg.e)
        except:
            raise ValueError('-e: Error format with time string')
    if arg.c is not None:
        args['channel'] = arg.c
    if args == {}:
        parser.print_usage()
        sys.exit(1)
    query = Query()
    query.get_stations(**args)
    for net in query.stations:
        for sta in net:
            print('{} {} {:.4f} {:.4f} {} {} {}'.format(net.code, sta.code,
                  sta.latitude, sta.longitude, sta.elevation, sta.start_date, sta.end_date,
                  sta.restricted_status))


if __name__ == "__main__":
    query = Query()
    # query.get_events(minmagnitude=7, catalog='GCMT')
    # query.get_stations(network='3J')
    # query.get_stations(network='3J', minlatitude=20,
    #                    minlongitude=97, maxlatitude=40,
    #                    maxlongitude=110)
    query.get_conti(UTCDateTime(2011,1,1), UTCDateTime(2011,2,1))
    print(query.conti_time)
    # print(query.stations)
