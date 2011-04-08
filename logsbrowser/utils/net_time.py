from datetime import datetime, timedelta
from subprocess import Popen, PIPE
import re
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import time
import config
from ui.dialogs import mwarning

_time_delta = timedelta(0)
_time_error_flag = 0

_format_to_re =dict([('%d', 'd{1,2}'),
                   ('%m', 'd{1,2}'),
                   ('%Y', 'd{4}'),
                   ('%y', 'd{2}'),
                   ('%H', 'd{1,2}'),
                   ('%I', 'd{1,2}'),
                   ('%M', 'd{2}'),
                   ('%S', 'd{2}'),
                   ('%w', 'd{1}'),
                   ('%p', '(AM|PM)'),
                   ('%B', '[A-Za-z]+'),
                   ('%b', '[A-Za-z]+'),
                   ('%a', '[A-Za-z]+'),
                   ('%A', '[A-Za-z]+'),
                   ('%f', 'd+')])

def time_re(time_format):
    for f, re_ in _format_to_re.iteritems():
        time_format=time_format.replace(f, re_)
    return time_format

_true_time_re = re.compile(time_re(config.SERVER_TIME_FORMAT))


def get_true_time():
    if config.SYNCRONIZE_TIME:
        now = datetime.now()
        try:
            proc = Popen([r"C:\Windows\System32\net.exe",
                          "time", config.SYNCRONIZE_SERVER],
                          stdout=PIPE)
            time_string = proc.communicate()[0]
        except Exception:
            server_time = now + _time_delta
            _time_error_flag = 1
        else:
            now = datetime.now()
            try:
                s_time = _true_time_re.search(time_string)
                server_time = datetime.strptime(s_time.group(0),
                                                config.SERVER_TIME_FORMAT)
            except Exception:
                server_time = now
            else:
                _time_delta = timedelta(seconds=(now - server_time).seconds)
                _time_error_flag = 0
        return time.mktime(server_time.timetuple())
    else:
        return time.time()

def syncron_warning():
    text = """Warning! \nFailed to get a date from the
 server.\nWill use the local time with the adjustment of %d
 seconds.""" % _time_delta.seconds
    mwarning(text)

