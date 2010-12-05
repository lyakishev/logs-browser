# -*- coding: utf-8 -*-
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import pywintypes
import datetime
import re
 
evt_dict={win32con.EVENTLOG_AUDIT_FAILURE:'AUDIT_FAILURE',
      win32con.EVENTLOG_AUDIT_SUCCESS:'AUDIT_SUCCESS',
      win32con.EVENTLOG_INFORMATION_TYPE:'INFORMATION',
      win32con.EVENTLOG_WARNING_TYPE:'WARNING',
      win32con.EVENTLOG_ERROR_TYPE:'ERROR'}

#----------------------------------------------------------------------
#msg=re.compile('"(.+?)"')
dtre = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")


def getEventLogs(server, logtype):
    try:
        hand = win32evtlog.OpenEventLog(server,logtype)  #!!!!!!
    except pywintypes.error:
	print "Error: %s %s" % (server, logtype)
        return    
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ #!!!!!!
    while 1:
        events=win32evtlog.ReadEventLog(hand,flags,0)
	if events:
		for ev_obj in events:
			yield getEventLog(ev_obj, server, logtype)
	else:
		win32evtlog.CloseEventLog(hand)
		return


def getEventLog(ev_obj, server, logtype):
    log = {}
    the_time = ev_obj.TimeGenerated.Format() #'12/23/99 15:54:09'
    sdt = dtre.search(the_time)
    #strptime has problem with threads
    #dtdate = datetime.datetime.strptime(the_time, '%m/%d/%y %H:%M:%S') #
    dtdate = datetime.datetime(int(sdt.group(3)), int(sdt.group(1)),
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

if __name__ == "__main__":
    import pdb
    pdb.set_trace()
    print len(getEventLogsLast(None, 'Application' , list(evt_dict.itervalues()), 3))
    
 

