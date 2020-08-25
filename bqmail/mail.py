from bqmail.query import Query
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients.iris import Client
import smtplib
from email.mime.text import MIMEText
from email.header import Header 
from .distaz import distaz
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
        self.header = generatemsg(username, inst, mailname, media)

    def query_stations(self, **kwargs):
        self.query.get_stations(**kwargs)

    def query_events(self, **kwargs):
        self.query.get_events(**kwargs)

    def send_mail(self, arrange='events', write_mail=False, **kwargs):
        if arrange == 'events':
            self.event_mail(**kwargs)
        elif arrange == 'continue':
            self.conti_mail(**kwargs)
        else:
            raise ValueError('variable arrange must be in \'events\' and \'continue\'')
        smtpobj = loginmail(self.mailname, server=self.server,
                            password=self.password)
        succ = sendmail(smtpobj, self.mailname, self.msgs)
        if succ:
            print('successfully send {}'.format(self.label))
        else:
            print('Error in sending {}'.format(self.label))
        if write_mail:
            with open('msg.{}'.format(self.label), 'w') as f:
                f.write(self.msgs)

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
        self.msgs = self.header
        self.label = 'Evts_{}'.format(UTCDateTime.now().strftime('%Y.%m.%dT%H%M%S'))
        self.msgs += '.LABEL {}\n.END\n'.format(self.label)
        for net in self.query.stations:
            for sta in net:
                if mark == 'o':
                    for i, evt in self.query.events.iterrows():
                        b_time = (evt['date'] + time_before).strftime('%Y %m %d %H %M %S')
                        e_time = (evt['date'] + time_after).strftime('%Y %m %d %H %M %S')
                        self.msgs += '{} {} {} {} 1 {} {}\n'.format(
                                     sta.code, net.code, b_time, e_time,
                                     channel, location)
                else:
                    for i, evt in self.query.events.iterrows():
                        ttime = self.get_ttime(evt, sta, phase=mark)
                        if ttime is None:
                            continue
                        else:
                            b_time = (evt['date'] + ttime + time_before).strftime('%Y %m %d %H %M %S')
                            e_time = (evt['date'] + ttime + time_after).strftime('%Y %m %d %H %M %S')
                            self.msgs += '{} {} {} {} 1 {} {}\n'.format(
                                         sta.code, net.code, b_time, e_time,
                                         channel, location)

    def get_ttime(self, evt, obspy_station, phase='P'):
        da = distaz(obspy_station.latitude, obspy_station.longitude,
                    evt.evla, evt.evlo)
        arr = model.get_travel_times(evt.evdp, da.delta, phase_list=[phase])
        if len(arr) == 0:
            return None
        else:
            return arr[0].time

