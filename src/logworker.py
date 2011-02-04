#! -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from parse import parse_filename, parse_logline_re, define_format
import os
import time
import datetime
from itertools import groupby
from collections import deque
import re
import multiprocessing
import threading
from operator import itemgetter as ig
import Queue
from buf_read import mmap_read, mmap_block_read


def datetime_intersect(t1start, t1end, t2start, t2end):
    return (t1start <= t2start and t2start <= t1end) or \
           (t2start <= t1start and t1start <= t2end)

def get_time(ed):
    return datetime.datetime(ed.tm_year,
                    ed.tm_mon,
                    ed.tm_mday,
                    ed.tm_hour,
                    ed.tm_min,
                    ed.tm_sec)

def queue_filler(evlogs, queue):
    for i in evlogs:
        queue.put(i)

def file_preparator(folders, fltr):
    #size = os.path.getsize
    flf = []
    for key, value in folders.iteritems():
        for f in os.listdir(key):
            fullf = os.path.join(key,f)
            pfn, ext = parse_filename(f)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt','log') and pfn in value:
                    flf.append([fullf, pfn])
    return flf

class FileLogWorker(multiprocessing.Process):
    def __init__(self, in_q, out_q, c_q, stp, fltr, f_cache):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_q
        self.out_queue = out_q
        self.stop = stp
        self.fltr = fltr
        self.completed_queue = c_q
        self.formats = f_cache

    def load(self):
        try:
            cdate = time.localtime(os.path.getctime(self.path))
        except WindowsError:
            print "WindowsError: %s" % self.path
            raise StopIteration
        if get_time(cdate)>self.fltr['date'][1]:
            raise StopIteration
        pformat = self.formats.get(self.Log)
        if not pformat:
            try:
                f = open(self.path, 'r')
            except IOError:
                print "IOError: %s" % self.path
                raise StopIteration
            line = True
            while line:
                line = f.readline()
                pformat = define_format(line)
                if pformat:
                    self.formats[self.Log] = pformat
                    break
            if f.tell() == 0:
                f.close()
                raise StopIteration
            else:
                f.close()
        if not pformat:
            print "Not found the format for file %s" % self.path
            raise StopIteration
        at = [0,0]
        buff = deque()
        for string in mmap_block_read(self.path, 8192):
            if self.stop.is_set():
                break
            #if string.lstrip().startswith("at"):
            if "at" in string.lstrip()[:2]:
                at[0]+=1
            if "Exception" in string:
                at[1]+=1
            parsed_s = parse_logline_re(string, cdate, pformat)
            if not parsed_s:
                buff.appendleft(string)
            else:
                l_type = (at[0]>0 and at[1]>0) and "ERROR" or "?"
                buff.appendleft(string)
                msg = "".join(buff)
                yield (parsed_s[0], "", self.Log, l_type , self.path, msg, "#FFFFFF", False)
                buff.clear()
                at = [0,0]

    def filter(self):
        def f_date(l):
            ndate = self.fltr['date']
            #try:
            if l[0]<ndate[0]:
                raise StopIteration
            #except TypeError:
            #    self.deq.clear()
            #    raise StopIteration
            return ndate[0]<=l[0]<=ndate[1]

        for l in (l1 for l1 in self.load() if f_date(l1)):
            yield l

    def group(self):
        for k, g in groupby(self.filter(), ig(0,1,2,3,4)):
            yield (k[0], k[1], k[2], k[3], k[4],\
                "".join(reversed([m[5] for m in g])),
                "#FFFFFF", False)

    def run(self):
        while 1:
            self.path, self.Log = self.in_queue.get()
            for l in self.group():
                self.out_queue.put(l)
            self.completed_queue.put(1)

class LogListFiller(threading.Thread):
    def __init__(self, q, model, view, stp, comp_q):#, pg):
        threading.Thread.__init__(self)
        self.queue = q
        self.model = model
        self.view = view
        self.c_q = comp_q
        self.stp = stp

    def run(self):
        self.view.freeze_child_notify()
        self.view.set_model(None)
        app = self.model.insert_after
        thr_ent = gtk.gdk.threads_enter
        thr_leave = gtk.gdk.threads_leave
        sib = None
        get = self.queue.get
        while 1:
            if self.stp.is_set():
                break
            try:
                l = get(True, 1)
                thr_ent()
                sib = app(sib,l)
                thr_leave()
            except Queue.Empty:
                pass
        get = self.queue.get_nowait
        while 1:
            try:
                l = get()
                thr_ent()
                sib=app(sib, l)
                thr_leave()
            except Queue.Empty:
                break
        self.model.set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        self.view.set_model(self.model)
        self.view.thaw_child_notify()
        self.c_q.put(1)
