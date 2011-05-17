#! -*- coding: utf8 -*-

from parse import define_format
import os
import time
from readers import mmap_block_read
from operator import itemgetter
from lparser.utils import to_unicode, isoformat
import config


def date_format(file_, path):
    pfunc = True
    for n, line in enumerate(file_):
        if n < config.MAX_LINES_FOR_DETECT_FORMAT:
            pformat, pfunc, need_date = define_format(line)
            if pformat:
                return (pformat, pfunc, need_date, line)
        else:
            break
    if not pfunc:
        print "Not found format for file %s" % path
    raise StopIteration
    

def filelogworker(dates, path, log):
    try:
        with open(path, 'r') as file_:
            pformat, pfunc, need_date, startl = date_format(file_, path)
            if need_date:
                try:
                    cdate = time.localtime(os.path.getctime(path))
                except WindowsError:
                    print "WindowsError: %s" % path
                    raise StopIteration
            else:
                cdate = None
            start_date = pfunc(startl, cdate, pformat)
            if start_date > dates[1]:
                raise StopIteration
            comp = [p for p in path.split(os.sep) if p][0]
            msg = ""
            for string in mmap_block_read(file_.fileno(), 8*1024):
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
    except IOError:
        raise StopIteration
        
