import time

def isoformat(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', t)

def to_unicode(msg):
    try:
        return msg.decode('utf-8')
    except UnicodeDecodeError:
        return msg.decode('cp1251', 'ignore')

def from_unicode(msg):
    try:
        return msg.encode('cp1251')
    except UnicodeEncodeError:
        return msg.encode('utf-8')

