#! -*- coding: utf8 -*-

from parse import parse_logline, define_format
import os
import datetime as dt
from readers import mmap_block_read
from operator import itemgetter
from lparser.utils import to_unicode

_formats = {}

def memoize_format(function):
    def wrapper(path, log):
        pformat = _formats.get(log)
        if pformat:
            return pformat
        else:
            pformat = function(path, log)
            _formats[log] = pformat
            return pformat
    return wrapper


@memoize_format
def date_format(path, log):
    try:
        file_ = open(path, 'r')
    except IOError:
        raise StopIteration
    for line in file_:
        pformat = define_format(line)
        if pformat:
            break
    file_.close()
    try:
        if not pformat:
            print "Not found format for file %s" % path
            raise StopIteration
        else:
            return pformat
    except UnboundLocalError:
        raise StopIteration
    

def filelogworker(dates, path, log):
        try:
            cdate = dt.datetime.fromtimestamp(os.path.getctime(path))
        except WindowsError:
            print "WindowsError: %s" % path
            raise StopIteration
        if cdate.isoformat(' ') > dates[1]:
            raise StopIteration
        pformat = date_format(path, log)
        comp = [p for p in path.split(os.sep) if p][0]
        msg = ""
        for string in mmap_block_read(path, 16*1024):
            parsed_date = parse_logline(string, cdate, pformat)
            if not parsed_date:
                msg = string + msg
            else:
                if parsed_date < dates[0]:
                    raise StopIteration
                if parsed_date <= dates[1]:
                    msg = to_unicode(string + msg)
                    yield (parsed_date,
                           comp,
                           log,
                           "ERROR" if ("Exception" in msg and "  at " in msg) \
                                   else "?",
                           path,
                           msg)
                msg = ""
