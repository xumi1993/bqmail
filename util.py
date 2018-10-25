import smtplib
from email.mime.text import MIMEText
from obspy.clients.fdsn import Client


def wsfetch(server, starttime=None, endtime=None, minlatitude=None,
            maxlatitude=None, minlongitude=None, maxlongitude=None,
            latitude=None, longitude=None, minradius=None,
            maxradius=None, mindepth=None, maxdepth=None,
            minmagnitude=None, maxmagnitude=None, magnitudetype=None,
            includeallorigins=None, includeallmagnitudes=None,
            includearrivals=None, eventid=None, limit=None, offset=None,
            orderby='time-asc', catalog=None, contributor=None):
    if not isinstance(server, str):
        raise TypeError('server name should be \'str\' type')
    locs = locals()
    locs.pop('server')
    client = Client(server)
    cat = client.get_events(**locs)
    data = [[evt.origins[0].time, evt.origins[0].latitude, evt.origins[0].longitude, evt.origins[0].depth * 0.001,
             evt.magnitudes[0].mag] for evt in cat if evt.origins[0].depth is not None]
    return data


def generatemsg(NAME, INST, EMAIL, MEDIA, ALTERNATEMEDIA, LABEL):
    msg = ''
    msg += '.NAME '+NAME+'\n'
    msg += '.INST '+INST+'\n'
    msg += '.MAIL\n'
    msg += '.EMAIL '+EMAIL+'\n'
    msg += '.PHONE\n'
    msg += '.FAX\n'
    msg += '.MEDIA '+MEDIA+'\n'
    msg += '.ALTERNATE MEDIA '+ALTERNATEMEDIA+'\n'
    msg += '.ALTERNATE MEDIA '+ALTERNATEMEDIA+'\n'
    msg += '.LABEL '+LABEL+'\n'
    msg += '.END\n'
    return msg


def sendmail(sender, recipient, contents, server='localhost', port=465, passwd=''):
    msg = MIMEText(contents, 'text')
    msg['Subject'] = 'BREQ_fast'
    msg['From'] = 'bqmail<'+sender+'>'
    msg['To'] = recipient
    if server == 'localhost':
        try:
            smtpObj = smtplib.SMTP(server)
            smtpObj.sendmail(sender, recipient, msg.as_string())
        except smtplib.SMTPException:
            print("Error when send mail by localhost")
    else:
        try:
            smtpObj = smtplib.SMTP_SSL(server, port)
            smtpObj.login(sender, passwd)
            smtpObj.sendmail(sender, recipient, msg.as_string())
        except smtplib.SMTPException:
            print("Error in linking {}".format(server))



