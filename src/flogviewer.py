#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from datetime import datetime
from net_time import GetTrueTime
from logworker import filelogworker, file_preparator
from widgets.date_time import DateFilter
from widgets.logs_tree import LogsTrees
from widgets.logs_notebook import LogsNotebook
import sys
from itertools import chain
from widgets.status_icon import StatusIcon
if sys.platform == 'win32':
    from evlogworker import evlogworker
import profiler


def logworker(dates,path,log,type_):
    if type_ == 'e':
        return evlogworker(dates,path,log)
    elif type_ == 'f':
        return filelogworker(dates,path,log)


class LogViewer:
    """ The GUI class is the controller for application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200, 800)

        self.date_filter = DateFilter()

        options_frame = gtk.Frame("Options")
        self.index_t = gtk.CheckButton(
                                "Full-text index (enables MATCH operator)")
        self.index_t.set_active(True)
        options_frame.add(self.index_t)

        self.status = StatusIcon(self.date_filter, self.root)

        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        stop_all_btn = gtk.Button('Stop')
        stop_all_btn.connect('clicked', self.stop_all)
        break_btn = gtk.Button('Break')
        break_btn.connect('clicked', self.break_all)

        main_box = gtk.HPaned()
        control_box = gtk.VBox()

        self.log_ntb = LogsTrees()

        self.logs_notebook = LogsNotebook(self.log_ntb, self.show_button)

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

        button_box.pack_start(self.show_button)
        button_box.pack_start(stop_all_btn)
        button_box.pack_start(break_btn)
        control_box.pack_start(self.log_ntb, True, True)
        control_box.pack_start(self.date_filter, False, False)
        control_box.pack_start(options_frame, False, False)
        control_box.pack_start(button_box, False, False, 5)
        control_box.pack_start(self.progressbar, False, False)
        main_box.pack1(control_box, False, False)
        main_box.pack2(self.logs_notebook, True, False)
        self.root.add(main_box)
        self.root.show_all()

    def stop_all(self, *args):
        self.stop = True

    def break_all(self, *args):
        self.break_ = True

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        self.status.statusicon.set_visible(False)
        gtk.main_quit()
        return

    def prepare_loglist(self, evlogs, flogs, dates):
        logw = self.logs_notebook.get_logs_list_window()
        loglist = logw.log_list
        loglist.clear()
        loglist.set_hash([evlogs,flogs,dates,datetime.now()])
        loglist.create_new_table(self.index_t.get_active())
        #logw.filter_logs.set_sql()
        return (logw, loglist)

    @profiler.time_it
    def show_logs(self, *args):
        self.stop = False
        self.break_ = False
        self.logs_notebook.set_sens(False)
        flogs, evlogs = self.log_ntb.get_log_sources()
        if flogs or evlogs:
            dates = (self.date_filter.get_active() and
                     self.date_filter.get_dates or
                     (datetime.min, datetime.max))
            logw, loglist = self.prepare_loglist(evlogs,flogs,dates)
            #if GetTrueTime.time_error_flag:
            #    GetTrueTime.show_time_warning(self.root)
            flogs_pathes = file_preparator(flogs)
            frac = 1.0 / (len(flogs_pathes) + len(evlogs) + 1)
            for n, (path, log, type_) in enumerate(chain(flogs_pathes,evlogs)):
                self.progressbar.set_text(log)
                loglist.insert_many(logworker(dates,path,log,type_))
                self.progressbar.set_fraction(frac*n)
                if self.stop or self.break_:
                    break
                while gtk.events_pending():
                    gtk.main_iteration()
            if self.break_:
                loglist.clear()
                self.progressbar.set_fraction(0.0)
                self.progressbar.set_text("")
            else:
                self.progressbar.set_text("Filling table...")
                logw.execute()
                self.progressbar.set_fraction(1.0)
                self.progressbar.set_text("Complete")
        self.logs_notebook.set_sens(True)
        

if __name__ == '__main__':
    log_viewer = LogViewer()
    gtk.main()
