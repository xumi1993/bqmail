from bqmail.query import Query
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients.iris import Client
import smtplib
from email.mime.text import MIMEText
from email.header import Header 
from .distaz import distaz
import time
model = TauPyModel()
cld = Client()


def connectsmtp(server, port, sender, password):
    smtpObj = smtplib.SMTP_SSL(server, port)
    smtpObj.login(sender, password)
    return smtpObj


def loginmail(sender, server='localhost', password='', port=465, test_num=5):
    test_it = 1
    while test_it <= test_num:
        if test_it > 1:
            print('Try to link to {} in {} times'.format(server, test_it))
        try:
            smtpObj = connectsmtp(server, port, sender, password)
        except:
            test_it += 1
            continue
        else:
            break
    if test_it > test_num:
        raise ConnectionError("Error in linking {}".format(server))
    else:
        return smtpObj


def sendmail(smtpObj, sender, contents,
             recipient='breq_fast@iris.washington.edu'):
    msg = MIMEText(contents, 'text')
    msg['Subject'] = Header('batch request seismic data', 'utf-8')
    msg['From'] = Header(sender)
    msg['To'] = Header(recipient)
    try:
        smtpObj.sendmail(sender, recipient, msg.as_string())
        return True
    except Exception as e:
        print('Error in sending mail: {}'.format(e))
        return False


def generatemsg(username, inst, mailname, media):
    msg = ''
    msg += '.NAME '+username+'\n'
    msg += '.INST '+inst+'\n'
    msg += '.MAIL\n'
    msg += '.EMAIL '+mailname+'\n'
    msg += '.PHONE\n'
    msg += '.FAX\n'
    msg += '.MEDIA '+media+'\n'
    msg += '.ALTERNATE MEDIA '+media+'\n'
    msg += '.ALTERNATE MEDIA '+media+'\n'
    return msg


def check_succ(succ, label):
    if succ:
        print('successfully send {}'.format(label))
    else:
        print('Error in sending {}'.format(label))

class BQMail():
    def __init__(self, mailname, username='bqmail',
                 inst='', media='Electronic (FTP)',
                 server='localhost', password=''):
        self.query = Query()
        self.mailname = mailname
        self.server = server
        self.password = password
        self.username = username
        self.inst = inst
        self.media = media
        self.msgs = ''
        self.label = ''
        self.evtinfo = ''
        self.header = generatemsg(username, inst, mailname, media)

    def query_stations(self, **kwargs):
        self.query.get_stations(**kwargs)

    def query_events(self, **kwargs):
        self.query.get_events(**kwargs)

    def send_mail(self, arrange='events', write_mail=False, write_evtinfo=False, **kwargs):
        """Send mail to Breq_fase

        :param arrange: Arrangement of earthquakes and stations, defaults to 'events'
        :type arrange: str, optional
        :param write_mail: write mail to ASCII file, defaults to False
        :type write_mail: bool, optional
        :param write_evtinfo: write event information to ASCII file. Only valid for stations and events, defaults to False
        :type write_evtinfo: bool, optional
        """
        smtpobj = loginmail(
            self.mailname,
            server=self.server,
            password=self.password
        )
        if arrange == 'stations':
            self.station_mail(**kwargs)
            succ = sendmail(smtpobj, self.mailname, self.msgs)
            check_succ(succ, self.label)
        elif arrange == 'continue':
            if write_evtinfo:
                raise ValueError('\'write_evtinfo\' can only be used when arrange=\'events\'')
            self.conti_mail(**kwargs)
            succ = sendmail(smtpobj, self.mailname, self.msgs)
            check_succ(succ, self.label)
        elif arrange == 'events':
            self.event_mail(**kwargs)
            self.send_mail_loop(smtpobj)
        else:
            raise ValueError('variable arrange must be in \'events\' and \'continue\'')
        if write_mail:
            with open('msg.{}'.format(self.label), 'w') as f:
                f.write(self.msgs)
        if write_evtinfo:
            with open('evtinfo.{}'.format(self.label), 'w') as f:
                f.write(self.evtinfo)

    def send_mail_loop(self, smtpobj):
        for key, value in self.msgs.items():
            succ = sendmail(smtpobj, key, value)
            check_succ(succ, self.label[key])
            time.sleep(4)

    def conti_mail(self, starttime=UTCDateTime(2000, 1, 1),
                   endtime=UTCDateTime.now(), time_val_in_hours=24,
                   channel='BH?', location=''):
        self.query.get_conti(starttime, endtime, hours=time_val_in_hours)
        self.msgs = self.header
        self.label = '{}_{}'.format(starttime.strftime('%Y.%m.%d'),
                                    endtime.strftime('%Y.%m.%d'))
        self.msgs += '.LABEL {}\n.END\n'.format(self.label)
        for sdt, edt in self.query.conti_time:
            for net in self.query.stations:
                for sta in net:
                    self.msgs += '{} {} {} {} 1 {} {}\n'.format(
                                 sta.code, net.code, sdt.strftime('%Y %m %d %H %M %S'),
                                 edt.strftime('%Y %m %d %H %M %S'), channel, location)

    def event_mail(self, time_before=0, time_after=1000,
                   mark='o', channel='BH?', location=''):
        self.msgs = {}
        self.label = {}
        for _, evt in self.query.events.iterrows():
            evt_date = evt['date'].strftime('%Y-%m-%dT%H:%M:%S')
            self.msgs[evt_date] = self.header
            self.label[evt_date] = 'Evts_{}'.format(evt_date)
            self.msgs[evt_date] += '.LABEL {}\n.END\n'.format(self.label[evt_date])
            self.msgs[evt_date] += '.HYPO ~{}~{:.4f}~{:.4f}~{:.1f}~0~0~{}\n'.format(
                evt['date'].strftime('%Y %m %d %H %M %S.%f'),
                evt['evla'],
                evt['evlo'],
                evt['region_name']
            )
            self.msgs[evt_date] += '.MAGNITUDE ~{:.1f}~{}~\n'.format(
                evt['mag'],
                evt['magtype']
            )
            for net in self.query.stations:
                for sta in net:
                    if mark != 'o':
                        ttime = self.get_ttime(evt, sta, phase=mark)
                        if ttime is None:
                            continue
                    else:
                        ttime = 0
                    b_time = evt['date'] + ttime + time_before
                    e_time = evt['date'] + ttime + time_after
                    self.evtinfo += '{} {} {} {} {:.3f} {:.3f} {:.3f} {:.1f} {}\n'.format(
                        sta.code, net.code,
                        b_time.strftime('%Y-%m-%dT%H:%M:%S'),
                        evt['date'].strftime('%Y-%m-%dT%H:%M:%S'),
                        evt['evla'], evt['evlo'], evt['evdp'], evt['mag'],
                        evt['magtype']
                    )
                    self.msgs[evt_date] += '{} {} {} {} 1 {} {}\n'.format(
                        sta.code, 
                        net.code,
                        b_time.strftime('%Y %m %d %H %M %S.%f'),
                        e_time.strftime('%Y %m %d %H %M %S.%f'),
                        channel,
                        location
                    )

    def station_mail(self, time_before=0, time_after=1000,
                   mark='o', channel='BH?', location=''):
        self.msgs = self.header
        self.label = 'Evts_{}'.format(UTCDateTime.now().strftime('%Y.%m.%dT%H%M%S'))
        self.msgs += '.LABEL {}\n.END\n'.format(self.label)
        for net in self.query.stations:
            for sta in net:
                if mark == 'o':
                    for _, evt in self.query.events.iterrows():
                        b_time = evt['date'] + time_before
                        b_time_str = b_time.strftime('%Y %m %d %H %M %S')
                        e_time_str = (evt['date'] + time_after).strftime('%Y %m %d %H %M %S')
                        self.evtinfo += '{} {} {} {} {:.3f} {:.3f} {:.3f} {:.1f} {}\n'.format(
                                        sta.code, net.code,
                                        b_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                        evt['date'].strftime('%Y-%m-%dT%H:%M:%S'),
                                        evt['evla'], evt['evlo'], evt['evdp'], evt['mag'],
                                        evt['magtype'])
                        self.msgs += '{} {} {} {} 1 {} {}\n'.format(
                                     sta.code, net.code, b_time_str, e_time_str,
                                     channel, location)
                else:
                    for _, evt in self.query.events.iterrows():
                        ttime = self.get_ttime(evt, sta, phase=mark)
                        if ttime is None:
                            continue
                        else:
                            b_time = evt['date'] + ttime + time_before
                            b_time_str = b_time.strftime('%Y %m %d %H %M %S')
                            e_time_str = (evt['date'] + ttime + time_after).strftime('%Y %m %d %H %M %S')
                            self.evtinfo += '{} {} {} {} {:.3f} {:.3f} {:.3f} {:.1f} {}\n'.format(
                                            sta.code, net.code,
                                            b_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                            evt['date'].strftime('%Y-%m-%dT%H:%M:%S'),
                                            evt['evla'], evt['evlo'], evt['evdp'], evt['mag'],
                                            evt['magtype'])
                            self.msgs += '{} {} {} {} 1 {} {}\n'.format(
                                         sta.code, net.code, b_time_str, e_time_str,
                                         channel, location)

    def get_ttime(self, evt, obspy_station, phase='P'):
        da = distaz(obspy_station.latitude, obspy_station.longitude,
                    evt.evla, evt.evlo)
        arr = model.get_travel_times(evt.evdp, da.delta, phase_list=[phase])
        if len(arr) == 0:
            return None
        else:
            return arr[0].time

