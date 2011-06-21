#! -*- coding: utf8 -*-

import datetime
import re
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import pywintypes
import time
from lparser.utils import to_unicode


EVT_DICT = {win32con.EVENTLOG_AUDIT_FAILURE: 'AUDIT_FAILURE',
            win32con.EVENTLOG_AUDIT_SUCCESS: 'AUDIT_SUCCESS',
            win32con.EVENTLOG_INFORMATION_TYPE: 'INFORMATION',
            win32con.EVENTLOG_WARNING_TYPE: 'WARNING',
            win32con.EVENTLOG_ERROR_TYPE: 'ERROR'}

_flags = (win32evtlog.EVENTLOG_BACKWARDS_READ |
         win32evtlog.EVENTLOG_SEQUENTIAL_READ)

DATETIME_REGEXP = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")
UNICODE_SYMBOL_REGEXP = re.compile(r"\u\w{4}")
DESCRIPTION_REGEXP = re.compile(r'''<The description for'''
                                r'''.+?:\s*u['"](.+)['"]\.>''',
                                re.DOTALL)


def get_event_log(ev_obj, server, logtype):
    log = {}
    the_time = ev_obj.TimeGenerated.Format()  # '12/23/99 15:54:09'
    parsed_dt= DATETIME_REGEXP.search(the_time)
    dt_group = parsed_dt.group
    dtdate = datetime.datetime(int("20" + dt_group(3)), int(dt_group(1)),
                                int(dt_group(2)), int(dt_group(4)),
                                int(dt_group(5)), int(dt_group(6)))
    #log['evt_id'] = str(winerror.HRESULT_CODE(ev_obj.EventID))
    #log['cat'] = ev_obj.EventCategory
    #log['record'] = ev_obj.RecordNumber
    log['computer'] = str(ev_obj.ComputerName)
    log['msg'] = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))
    log['logtype'] = logtype
    log['server'] = server
    log['source'] = str(ev_obj.SourceName)
    if not ev_obj.EventType in EVT_DICT.keys():
        log['evt_type'] = "unknown"
    else:
        log['evt_type'] = str(EVT_DICT[ev_obj.EventType])
    log['the_time'] = dtdate.isoformat(' ')
    return log

def log_for_insert(log):
    msg = log['msg']
    if UNICODE_SYMBOL_REGEXP.search(msg):
        msg = msg.decode('unicode-escape', 'replace')
    description = DESCRIPTION_REGEXP.search(msg)
    if description:
        msg = description.group(1)
    return (log['the_time'],
            log['computer'],
            log['logtype'],
            log['evt_type'],
            log['source'],
            1,
            to_unicode(msg))


def evlogworker(dates, server, logtype, funcs=None):
    try:
        hand = win32evtlog.OpenEventLog(server, logtype)
    except pywintypes.error:
        raise StopIteration
    while 1:
        for attempt in xrange(6):
            try:
                events = win32evtlog.ReadEventLog(hand, _flags, 0)
            except pywintypes.error:
                #hand.Detach()  # need?
                time.sleep(1)
            else:
                if events:
                    break
                else:
                    raise StopIteration
        else:
            print "Can't read eventlogs: %s %s " % (serve,logtype)
            try:
                win32evtlog.CloseEventLog(hand)
            except pywintypes.error:
                pass
            finally:
                raise StopIteration
        for ev_obj in events:
            log = get_event_log(ev_obj, server, logtype)
            if log['the_time'] < dates[0]:
                raise StopIteration
            if log['the_time'] <= dates[1]:
                yield log_for_insert(log), 1

