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
            for line in file_:
                pformat, pfunc = define_format(line)
                if pformat:
                    return (pformat, pfunc)
            print "Not found format for file %s" % path
            raise StopIteration
    except IOError:
        raise StopIteration
    

def filelogworker(dates, path, log):
        try:
            file_stat = os.stat(path)
        except WindowsError:
            print "WindowsError: %s" % path
            raise StopIteration
        else:
            if not file_stat.st_size:
                raise StopIteration
            cdate = time.localtime(file_stat.st_ctime)
        if isoformat(cdate) > dates[1]:
            raise StopIteration
        pformat, pfunc = date_format(path, log)
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
