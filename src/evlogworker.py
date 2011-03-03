#! -*- coding: utf8 -*-

import datetime
import multiprocessing
import re
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import pywintypes
import time

EVT_DICT = {win32con.EVENTLOG_AUDIT_FAILURE: 'AUDIT_FAILURE',
            win32con.EVENTLOG_AUDIT_SUCCESS: 'AUDIT_SUCCESS',
            win32con.EVENTLOG_INFORMATION_TYPE: 'INFORMATION',
            win32con.EVENTLOG_WARNING_TYPE: 'WARNING',
            win32con.EVENTLOG_ERROR_TYPE: 'ERROR'}

DATETIME_REGEXP = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")
UNICODE_SYMBOL_REGEXP = re.compile(r"\u\w{4}")
DESCRIPTION_REGEXP = re.compile(r'''<The description for'''
                                r'''.+?:\s*u['"](.+)['"]\.>''',
                                re.DOTALL)


def get_event_log(ev_obj, server, logtype):
    log = {}
    the_time = ev_obj.TimeGenerated.Format()  # '12/23/99 15:54:09'
    sdt = DATETIME_REGEXP.search(the_time)
    #strptime has problem with threads
    #dtdate = datetime.datetime.strptime(the_time, '%m/%d/%y %H:%M:%S') #
    dtdate = datetime.datetime(int("20" + sdt.group(3)), int(sdt.group(1)),
                                int(sdt.group(2)), int(sdt.group(4)),
                                int(sdt.group(5)), int(sdt.group(6)))
    log['evt_id'] = str(winerror.HRESULT_CODE(ev_obj.EventID))
    log['computer'] = str(ev_obj.ComputerName)
    log['cat'] = ev_obj.EventCategory
    log['record'] = ev_obj.RecordNumber
    log['msg'] = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))
    log['logtype'] = logtype
    log['server'] = server
    log['source'] = str(ev_obj.SourceName)
    if not ev_obj.EventType in EVT_DICT.keys():
        log['evt_type'] = "unknown"
    else:
        log['evt_type'] = str(EVT_DICT[ev_obj.EventType])
    log['the_time'] = dtdate
    return log


class LogWorker(multiprocessing.Process):
    def __init__(self, queues, stp, fltr):
        super(LogWorker, self).__init__()
        self.fltr = fltr
        self.stop = stp
        self.queues = queues
        self.server, self.logtype = "", ""  # defines in self.run()

    def f_date(self, log):
        if log['the_time'] < self.fltr['date'][0]:
            raise StopIteration
        return (log['the_time'] <= self.fltr['date'][1] and \
            log['the_time'] >= self.fltr['date'][0])

    def f_type(self, log):
        if self.fltr['types']:
            return (log['evt_type'] in self.fltr['types'])
        else:
            return True

    def load(self):
        try:
            hand = win32evtlog.OpenEventLog(self.server, self.logtype)
        except pywintypes.error:
            print "Error: %s %s" % (self.server, self.logtype)
            return
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | \
                win32evtlog.EVENTLOG_SEQUENTIAL_READ
        while 1:
            if self.stop.is_set():
                break
            while 1:
                try:
                    events = win32evtlog.ReadEventLog(hand, flags, 0)
                except pywintypes.error:
                    print "Pause %s %s" % (self.server, self.logtype)
                    hand.Detach()  # need?
                    time.sleep(1)
                    hand = win32evtlog.OpenEventLog(self.server, self.logtype)
                else:
                    break
            if events:
                for ev_obj in events:
                    if self.stop.is_set():
                        break
                    yield get_event_log(ev_obj, self.server, self.logtype)
            else:
                try:
                    win32evtlog.CloseEventLog(hand)
                except pywintypes.error:
                    print "Can't close"

    def filter(self):
        date_filter = (log for log in self.load() if self.f_date(log))
        type_filter = (log for log in date_filter if self.f_type(log))
        for log in type_filter:
            yield log

    def run(self):
        while 1:
            self.server, self.logtype = self.queues[0].get()
            for log in self.filter():
                if UNICODE_SYMBOL_REGEXP.search(log['msg']):
                    msg = log['msg'].decode('unicode-escape', 'replace')
                else:
                    msg = log['msg']
                description = DESCRIPTION_REGEXP.search(msg)
                if description:
                    msg = description.group(1)
                self.queues[1].put((log['the_time'],
                                    log['computer'],
                                    log['logtype'],
                                    log['evt_type'],
                                    log['source'],
                                    msg,
                                    "#FFFFFF",
                                    False))
            self.queues[2].put(1)
