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

def time_re(time_format):
    return time_format.replace('%d', '\d{1,2}').\
                       replace('%m', '\d{1,2}').\
                       replace('%Y', '\d{4}').\
                       replace('%y', '\d{2}').\
                       replace('%H', '\d{1,2}').\
                       replace('%I', '\d{1,2}').\
                       replace('%M', '\d{2}').\
                       replace('%S', '\d{2}').\
                       replace('%w', '\d{1}').\
                       replace('%p', '(AM|PM)').\
                       replace('%B', '[A-Za-z]+').\
                       replace('%b', '[A-Za-z]+').\
                       replace('%a', '[A-Za-z]+').\
                       replace('%A', '[A-Za-z]+').\
                       replace('%f', '\d+')

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
    text = "Warning! \nFailed to get a date from the"\
           " server.\nWill use the local time with the adjustment of %d"\
           " seconds." % _time_delta.seconds
    mwarning(text)

