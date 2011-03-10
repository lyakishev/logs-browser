#! -*- coding: utf8 -*-

from parse import parse_filename, parse_logline_re, define_format
import os
import time
import datetime
from collections import deque
from buf_read import mmap_block_read
from operator import itemgetter

def get_time(tm_dt):
    return datetime.datetime(tm_dt.tm_year,
                    tm_dt.tm_mon,
                    tm_dt.tm_mday,
                    tm_dt.tm_hour,
                    tm_dt.tm_min,
                    tm_dt.tm_sec)


def file_preparator(folders):
    flf = []
    for key, value in folders.iteritems():
        for file_ in os.listdir(key):
            fullf = os.path.join(key, file_)
            pfn, ext = parse_filename(file_)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt', 'log') and pfn in value:
                flf.append([fullf, pfn])
    return sorted(flf, key=itemgetter(1))

def filelogworker(dates, path, log):
        try:
            cdate = time.localtime(os.path.getctime(path))
        except WindowsError:
            print "WindowsError: %s" % path
            raise StopIteration
        if get_time(cdate) > dates[1]:
            raise StopIteration
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
        except UnboundLocalError:
            raise StopIteration
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
                    msg = string + msg
                    try:
                        msg = msg.decode('utf-8')
                    except UnicodeDecodeError:
                        msg = msg.decode('cp1251')
                    yield (parsed_date,
                           comp,
                           log,
                           "ERROR" if ("Exception" in msg and "  at " in msg) \
                                   else "?",
                           path,
                           msg)
                msg = ""
