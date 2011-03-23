def to_unicode(msg):
    try:
        return msg.decode('utf-8')
    except UnicodeDecodeError:
        return msg.decode('cp1251')
