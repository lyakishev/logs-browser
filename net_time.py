from datetime import datetime, timedelta
import subprocess
import re
import pygtk
pygtk.require("2.0")
import gtk, gobject, gio

true_time_re = re.compile(r"\d{2}\.\d{2}.\d{4}\s\d{2}:\d{2}:\d{2}")

TimeDelta = timedelta(0)
time_error_flag = 0

def get_true_time():
    global TimeDelta
    global time_error_flag
    try:
        time_string = subprocess.check_output(r"net time \\msk-app-v0190")
    except:
        server_time = datetime.now() + TimeDelta
        time_error_flag = 1
    else:
        server_time = datetime.strptime(true_time_re.search(time_string).group(0), "%d.%m.%Y %H:%M:%S")
        TimeDelta = server_time - datetime.now()
        time_error_flag = 0
    finally:
        return server_time


def show_time_warning(parent):
    md = gtk.MessageDialog(parent,
        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
        gtk.BUTTONS_CLOSE, "Warning! \nFailed to get a date from the"
           "server.\nWill use the local time with the adjustment of %d" 
            " seconds." % TimeDelta.seconds)
    md.run()
    md.destroy()
    
