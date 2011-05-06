#! -*- coding: utf8 -*-

from parse import define_format
import os
import time
from readers import mmap_block_read
from operator import itemgetter
from lparser.utils import to_unicode, isoformat

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
        with open(path, 'r') as file_:
            pfunc = True
            for line in file_:
                pformat, pfunc, need_date = define_format(line)
                if pformat:
                    return (pformat, pfunc, need_date)
            if not pfunc:
                print "Not found format for file %s" % path
            raise StopIteration
    except IOError:
        raise StopIteration
    

def filelogworker(dates, path, log):
    pformat, pfunc, need_date = date_format(path, log)
    if need_date:
        try:
            cdate = time.localtime(os.path.getctime(path))
        except WindowsError:
            print "WindowsError: %s" % path
            raise StopIteration
    else:
        cdate = None
    comp = [p for p in path.split(os.sep) if p][0]
    msg = ""
    for string in mmap_block_read(path, 16*1024):
        parsed_date = pfunc(string, cdate, pformat)
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
                       ("ERROR" if ("Exception" in msg and "  at " in msg)
                               else "?"),
                       path,
                       0,
                       msg)
            msg = ""
