#! -*- coding: utf8 -*-

import os
import time
from readers import mmap_block_read, seek_block_read, mmap_block_read2
from operator import itemgetter
from utils.common import to_unicode, isoformat
import config
from collections import deque


def get_start_date(file_, pformat, cdate, pfunc):
    for line in file_:
        start_date = pfunc(line, cdate, pformat)
        if start_date:
            return start_date


def filelogworker2(dates, path, log, funcs):
    pformat, pfunc, need_date = funcs
    if need_date:
        try:
            cdate = time.localtime(os.path.getctime(path))
        except WindowsError:
            #print "WindowsError: %s" % path
            raise StopIteration
    else:
        cdate = None
    try:
        with open(path, 'rU') as file_:
            start_date = get_start_date(file_, pformat, cdate, pfunc)
            if start_date > dates[1]:
                raise StopIteration
            comp = [p for p in path.split(os.sep) if p][0]
            path = to_unicode(path)
            msg_deque = deque()
            for string in mmap_block_read(file_, 16*1024):
                parsed_date = pfunc(string, cdate, pformat)
                if not parsed_date:
                    msg_deque.appendleft(string)
                else:
                    if parsed_date < dates[0]:
                        raise StopIteration
                    if parsed_date <= dates[1]:
                        msg_deque.appendleft(string)
                        msg = to_unicode("".join(msg_deque))
                        yield (parsed_date,
                               comp,
                               log,
                               ("ERROR" if ("Exception" in msg and "  at " in msg)
                                       else "?"),
                               path,
                               0,
                               msg), len(msg)
                    msg_deque.clear()
    except IOError:
        raise StopIteration

def filelogworker(dates, path, log, funcs):
    pformat, pfunc, need_date = funcs
    if need_date:
        try:
            cdate = time.localtime(os.path.getctime(path))
        except WindowsError:
            #print "WindowsError: %s" % path
            raise StopIteration
    else:
        cdate = None
    try:
        with open(path, 'rU') as file_:
            start_date = get_start_date(file_, pformat, cdate, pfunc)
            if start_date > dates[1]:
                raise StopIteration
            comp = [p for p in path.split(os.sep) if p][0]
            path = to_unicode(path)
            reader = mmap_block_read2(file_, 16*1024)
            for string in reader:
                parsed_date = pfunc(string, cdate, pformat)
                if parsed_date:
                    if parsed_date < dates[0]:
                        raise StopIteration
                    if parsed_date <= dates[1]:
                        msg, chars = reader.send(1)
                        yield (parsed_date,
                               comp,
                               log,
                               ("ERROR" if ("Exception" in msg and "  at " in msg)
                                       else "?"),
                               path,
                               0,
                               to_unicode(msg)), chars
                    else:
                        reader.send(0)
    except IOError:
        raise StopIteration
