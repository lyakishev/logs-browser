#! -*- coding: utf8 -*-

from parse import parse_filename, parse_logline_re, define_format
import os
import datetime as dt
from buf_read import mmap_block_read
from operator import itemgetter
from  utils import to_unicode

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

def file_preparator(folders):
    flf = []
    for key, value in folders.iteritems():
        for file_ in os.listdir(key):
            fullf = os.path.join(key, file_)
            pfn, ext = parse_filename(file_)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt', 'log') and pfn in value:
                flf.append([fullf, pfn, 'f'])
    return sorted(flf, key=itemgetter(1))


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
        if cdate > dates[1]:
            raise StopIteration
        pformat = date_format(path, log)
        comp = [p for p in path.split(os.sep) if p][0]
        msg = ""
        for string in mmap_block_read(path, 16*1024):
            parsed_date = parse_logline_re(string, cdate, pformat)
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
