from datetime import datetime, timedelta
from subprocess import Popen, PIPE
import re
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import time
#net time \\nag-tc-01 /set /yes

class GetTrueTime(object):
    true_time_re = re.compile(r"\d{2}\.\d{2}.\d{4}\s\d{1,2}:\d{2}:\d{2}")
    time_delta = timedelta(0)
    time_error_flag = 0

    def __new__(cls):
        now = datetime.now()
        try:
            proc = Popen([r"C:\Windows\System32\net.exe",
                          "time", r"\\nag-tc-01"],
                          stdout=PIPE)
            time_string = proc.communicate()[0]
        except Exception:
            server_time = now + cls.time_delta
            cls.time_error_flag = 1
        else:
            now = datetime.now()
            try:
                s_time = cls.true_time_re.search(time_string)
                server_time = datetime.strptime(s_time.group(0),
                                                "%d.%m.%Y %H:%M:%S")
            except Exception:
                server_time = now
            else:
                cls.time_delta = timedelta(seconds=(now - server_time).seconds)
                cls.time_error_flag = 0
        return time.mktime(server_time.timetuple())

    @classmethod
    def show_time_warning(cls, parent):
        message_dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
            gtk.BUTTONS_CLOSE, "Warning! \nFailed to get a date from the"
               "server.\nWill use the local time with the adjustment of %d"
                " seconds." % cls.time_delta.seconds)
        message_dialog.run()
        message_dialog.destroy()
