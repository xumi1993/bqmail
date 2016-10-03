#!/usr/bin/env python

import subprocess

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

def sendmail(recipient, msg):
    p = subprocess.Popen(["mail",recipient], stdin=subprocess.PIPE)
    try:
        p.communicate(msg.encode())
        p.wait()
        return True
    except:
        return False
