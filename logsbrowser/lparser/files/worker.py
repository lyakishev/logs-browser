#! -*- coding: utf8 -*-

from parse import define_format
import os
import time
from readers import mmap_block_read
from operator import itemgetter
from lparser.utils import to_unicode, isoformat
import config


def get_start_date(file_, pformat, cdate, pfunc):
    for line in file_:
        start_date = pfunc(line, cdate, pformat)
        if start_date:
            return start_date


def filelogworker(dates, path, log, funcs):
    pformat, pfunc, need_date = funcs
    if need_date:
        try:
            cdate = time.localtime(os.path.getctime(path))
        except WindowsError:
            print "WindowsError: %s" % path
            raise StopIteration
    else:
        cdate = None
    try:
        with open(path, 'r') as file_:
            start_date = get_start_date(file_, pformat, cdate, pfunc)
            if start_date > dates[1]:
                raise StopIteration
            comp = [p for p in path.split(os.sep) if p][0]
            msg = ""
            clines = 0
            for string in mmap_block_read(file_.fileno(), 8*1024):
                parsed_date = pfunc(string, cdate, pformat)
                if not parsed_date:
                    msg = string + msg
                    clines += 1
                else:
                    if parsed_date < dates[0]:
                        raise StopIteration
                    if parsed_date <= dates[1]:
                        msg = to_unicode(string + msg)
                        clines += 1
                        yield (parsed_date,
                               comp,
                               log,
                               ("ERROR" if ("Exception" in msg and "  at " in msg)
                                       else "?"),
                               path,
                               0,
                               msg), clines
                    msg = ""
                    clines = 0
    except IOError:
        raise StopIteration
        
