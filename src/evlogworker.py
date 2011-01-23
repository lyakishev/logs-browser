#! -*- coding: utf8 -*-

import datetime
import multiprocessing
import re
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import pywintypes

evt_dict={win32con.EVENTLOG_AUDIT_FAILURE:'AUDIT_FAILURE',
      win32con.EVENTLOG_AUDIT_SUCCESS:'AUDIT_SUCCESS',
      win32con.EVENTLOG_INFORMATION_TYPE:'INFORMATION',
      win32con.EVENTLOG_WARNING_TYPE:'WARNING',
      win32con.EVENTLOG_ERROR_TYPE:'ERROR'}

dtre = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")
uc_re = re.compile(r"\u\w{4}")
descr_re = re.compile(r'''<The description for.+?:\s*u['"](.+)['"]\.>''', re.DOTALL)

def getEventLog(ev_obj, server, logtype):
    log = {}
    the_time = ev_obj.TimeGenerated.Format() #'12/23/99 15:54:09'
    sdt = dtre.search(the_time)
    #strptime has problem with threads
    #dtdate = datetime.datetime.strptime(the_time, '%m/%d/%y %H:%M:%S') #
    dtdate = datetime.datetime(int("20"+sdt.group(3)), int(sdt.group(1)),
                                int(sdt.group(2)), int(sdt.group(4)),
                                int(sdt.group(5)),int(sdt.group(6)))
    log['evt_id'] = str(winerror.HRESULT_CODE(ev_obj.EventID))
    log['computer'] = str(ev_obj.ComputerName)
    log['cat'] = ev_obj.EventCategory
    log['record'] = ev_obj.RecordNumber
    log['msg'] = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))
    log['logtype'] = logtype
    log['server'] = server
    log['source'] = str(ev_obj.SourceName)
    if not ev_obj.EventType in evt_dict.keys():
	log['evt_type'] = "unknown"
    else:
	log['evt_type'] = str(evt_dict[ev_obj.EventType])
    log['the_time'] = dtdate
    return log


class LogWorker(multiprocessing.Process):
    def __init__(self, in_q, out_q, c_q, stp, fltr):
        super(LogWorker,self).__init__()
        self.fltr = fltr
        self.stop = stp
        self.in_queue = in_q
        self.out_queue = out_q
        self.completed_queue = c_q

    def f_date(self, l):
        if l['the_time']<self.fltr['date'][0]:
            raise StopIteration
        return (l['the_time']<=self.fltr['date'][1] and \
            l['the_time']>=self.fltr['date'][0])

    def f_type(self, l):
        if self.fltr['types']:
            return (l['evt_type'] in self.fltr['types'])
        else:
            return True

    def load(self):
        try:
            hand = win32evtlog.OpenEventLog(self.server, self.logtype)  #!!!!!!
        except pywintypes.error:
            print "Error: %s %s" % (self.server, self.logtype)
            return
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
        while 1:
            if self.stop.is_set():
                break
            while 1:
                try:
                    events=win32evtlog.ReadEventLog(hand,flags,0)
                except pywintypes.error:
                    print "Pause %s %s" % (self.server, self.logtype)
                    hand.Detach() #need?
                    time.sleep(1)
                    hand = win32evtlog.OpenEventLog(self.server, self.logtype)  #!!!!!!
                else:
                    break
            if events:
                    for ev_obj in events:
                        if self.stop.is_set():
                            break
                        yield getEventLog(ev_obj, self.server, self.logtype)
            else:
                    try:
                        win32evtlog.CloseEventLog(hand)
                    except pywintypes.error:
                        print "Can't close"
                    finally:
                        return

    def filter(self):
        self.f1 = (l for l in self.load() if self.f_date(l))
        self.f2 = (l for l in self.f1 if self.f_type(l))
        for l in self.f2:
            yield l

    def run(self):
        while 1:
            self.server, self.logtype = self.in_queue.get()
            for l in self.filter():
                if uc_re.search(l['msg']):
                    msg = l['msg'].decode('unicode-escape', 'replace')
                else:
                    msg = l['msg']
                ds = descr_re.search(msg)
                if ds:
                    msg = ds.group(1)
                self.out_queue.put((l['the_time'], l['computer'], l['logtype'], \
                    l['evt_type'], l['source'], msg, "#FFFFFF", False))
            self.completed_queue.put(1)


