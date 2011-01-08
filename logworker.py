#! -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk, gobject
from parse import parse_filename, parse_logline_re, define_format
import os
import time
import datetime
from itertools import islice, groupby
from collections import deque
import re
import multiprocessing
import threading
#import codecs
from operator import itemgetter as ig
import Queue

#error_flag = re.compile(r"^at")
dtre = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")
uc_re = re.compile(r"\u\w{4}")
descr_re = re.compile(r'''<The description for.+?:\s*u['"](.+)['"]\.>''', re.DOTALL)

def datetime_intersect(t1start, t1end, t2start, t2end):
    return (t1start <= t2start and t2start <= t1end) or \
           (t2start <= t1start and t1start <= t2end)

def get_time(path, ed):
    #deq = deque()
    #f = open(path, 'r')
    #deq.extend(f.readlines())
    #f.close()
    #while deq:
    #    string = deq.pop()
    #    parsed_s = parse_logline(string,cdate)
    #    if parsed_s:
    #        return parsed_s[0]
    #ed = cdate
    return datetime.datetime(ed.tm_year,
                    ed.tm_mon,
                    ed.tm_mday,
                    ed.tm_hour,
                    ed.tm_min,
                    ed.tm_sec)

def queue_filler(evlogs, queue):
    for i in evlogs:
        queue.put(i)

def file_preparator(folders, fltr):#, queue):
    flf = []
    ltime = time.localtime
    for key, value in folders.iteritems():
        for f in os.listdir(key):
            fullf = os.path.join(key,f)
            if os.path.isfile(fullf):
                pfn, ext = parse_filename(f)
                if not pfn:
                    pfn = "undefined"
                if ext in ('txt','log') and pfn in value:
                    f_start_date = get_time(fullf, \
                        ltime(os.path.getctime(fullf)))
                    if f_start_date<=fltr['date'][1]:
                        flf.append([fullf, pfn])
                        #queue.put(fullf)
    return flf


class FileLogWorker(multiprocessing.Process):
    def __init__(self, in_q, out_q, c_q, stp, fltr):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_q
        self.out_queue = out_q
        self.stop = stp
        self.fltr = fltr
        self.completed_queue = c_q

    def load(self):
        cdate = time.localtime(os.path.getctime(self.path))
        deq = deque()
        buf_deq = deque()
        f = open(self.path, 'r')
        #f = codecs.open(self.path, 'r', 'cp1251')
        deq.extend(f.readlines())
        f.close()
        pformat = None
        while deq:
            line = deq.popleft()
            pformat = define_format(line)
            buf_deq.append(line)
            if pformat:
                break
        if not pformat:
            if buf_deq:
                print "Not found the format for file %s" % self.path
            else:
                print "File %s is empty." % self.path
            raise StopIteration
        else:
            while buf_deq:
                deq.appendleft(buf_deq.pop())
        at = [0,0]
        while deq:
            if self.stop.is_set():
                break
            string = deq.pop()#.decode('cp1251', 'replace')
            if "at" in string.lstrip()[:2]:#.startswith("at"):
                at[0]+=1
            if "Exception" in string:
                at[1]+=1
            parsed_s = parse_logline_re(string, cdate, pformat)
            if not parsed_s:
                buf_deq.appendleft(string)
            else:
                l_type = (at[0]>0 and at[1]>0) and "ERROR" or "?"
                at = [0,0]
                buf_deq.appendleft(string)
                msg = "".join(buf_deq)
                buf_deq.clear()
                yield (parsed_s[0], "", self.Log, l_type , self.path, msg, "#FFFFFF", False)

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
