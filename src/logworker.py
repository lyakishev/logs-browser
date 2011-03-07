#! -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from parse import parse_filename, parse_logline_re, define_format
import os
import time
import datetime
from itertools import islice
from collections import deque
import multiprocessing
import threading
from operator import itemgetter as ig
import Queue
from buf_read import mmap_block_read
import sys

def get_time(tm_dt):
    return datetime.datetime(tm_dt.tm_year,
                    tm_dt.tm_mon,
                    tm_dt.tm_mday,
                    tm_dt.tm_hour,
                    tm_dt.tm_min,
                    tm_dt.tm_sec)


def queue_filler(logs, queue):
    for i in logs:
        queue.put(i)


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
    return flf


class FileLogWorker(multiprocessing.Process):
    def __init__(self, queues, stp, dates):
        multiprocessing.Process.__init__(self)
        self.queues = queues
        self.stop = stp
        self.dates = dates
        self.formats = {}#f_cache
        self.path, self.common_log_name = "", "" # defines in self.run()

    def load(self):
        try:
            cdate = time.localtime(os.path.getctime(self.path))
        except WindowsError:
            #print "WindowsError: %s" % self.path
            raise StopIteration
        if get_time(cdate) > self.dates[1]:
            raise StopIteration
        pformat = self.formats.get(self.common_log_name)
        if not pformat:
            try:
                file_ = open(self.path, 'r')
            except IOError:
                #print "IOError: %s" % self.path
                raise StopIteration
            line = True
            while line and (not pformat):
                line = file_.readline()
                pformat = define_format(line)
            self.formats[self.common_log_name] = pformat
            file_.close()
        if not pformat:
            #print "Not found the format for file %s" % self.path
            raise StopIteration
        at_err = [0, 0]
        buff = deque()
        for string in mmap_block_read(self.path, 8192):
            if self.stop.is_set():
                break
            at_err[0] += string.lstrip().startswith("at")
            at_err[1] += ("Exception" in string)
            parsed_s = parse_logline_re(string, cdate, pformat)
            if not parsed_s:
                buff.appendleft(string)
            else:
                date = parsed_s[0]
                if date < self.dates[0]:
                    buff.clear()
                    raise StopIteration
                if date <= self.dates[1]:
                    l_type = (at_err[0] > 0 and at_err[1] > 0) and "ERROR" or "?"
                    buff.appendleft(string)
                    msg = "".join(buff)
                    yield (parsed_s[0],
                           "",
                           self.common_log_name,
                           l_type,
                           self.path,
                           msg)
                buff.clear()
                at_err = [0, 0]

    def run(self):
        while 1:
            self.path, self.common_log_name = self.queues[0].get()
            for log in self.load():
                self.queues[1].put(log)
            self.queues[2].put(1)


class LogListFiller(threading.Thread):
    def __init__(self, queues, stp, loglist):  # , pg):
        threading.Thread.__init__(self)
        self.queues = queues
        self.stp = stp
        self.loglist = loglist

    def run(self):
        now = datetime.datetime.now
        self.loglist.create_new_table()
        insert = self.loglist.insert
        get = self.queues[0].get
        dt = now()
        while 1:
            try:
                log = get(True, 1)
            except Queue.Empty:
                break
            else:
                insert(log)
        print "Insert: ", now() - dt
        #get = self.queues[0].get_nowait
        #while 1:
        #    try:
        #        log = get()
        #        insert(log)
        #        self.count+=1
        #    except Queue.Empty:
        #        break
        self.loglist.db_conn.commit()
        self.loglist.execute("""select date, log, type, source from this
                                group by date
                                ;""")
        self.queues[1].put(1)
