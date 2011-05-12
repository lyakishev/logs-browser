#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from datetime import datetime
from datetimef import DateFilter
from logstree import LogsTrees
from logsnotebook import LogsNotebook
import sys
from statusicon import StatusIcon
import config
import utils.profiler as profiler
from process import process, mp_process
from db.engine import close_conn
from operator import setitem


class LogsViewer:
    """ The GUI class is the controller for application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Logs Browser")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200, 800)

        self.date_filter = DateFilter()

        options_frame = gtk.Frame("Options")
        self.index_t = gtk.CheckButton(
                                "Full-text index (enables MATCH operator)")
        self.index_t.set_active(config.FTSINDEX)
        options_frame.add(self.index_t)

        self.status = StatusIcon(self.date_filter, self.root)

        self.signals = {'stop': False, 'break': False}
        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        self.stop_all_btn = gtk.Button('Stop')
        self.stop_all_btn.connect('clicked',
                            lambda btn: setitem(self.signals,'stop',True))
        self.stop_all_btn.set_sensitive(False)
        self.break_btn = gtk.Button('Break')
        self.break_btn.connect('clicked',
                            lambda btn: setitem(self.signals,'break',True))
        self.break_btn.set_sensitive(False)

        main_box = gtk.HPaned()
        control_box = gtk.VBox()

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)


        self.source_tree = LogsTrees(self.progressbar, self.fill_tree_sens,
                                     self.signals)

        self.browser = LogsNotebook(self.source_tree, self.show_button)


        button_box.pack_start(self.show_button)
        button_box.pack_start(self.stop_all_btn)
        button_box.pack_start(self.break_btn)
        control_box.pack_start(self.source_tree, True, True)
        control_box.pack_start(self.date_filter, False, False)
        control_box.pack_start(options_frame, False, False)
        control_box.pack_start(button_box, False, False, 5)
        control_box.pack_start(self.progressbar, False, False)
        main_box.pack1(control_box, False, False)
        main_box.pack2(self.browser, True, False)
        self.root.add(main_box)
        self.root.show_all()
        self.source_tree.fill(config.FILL_LOGSTREE_AT_START)

    def fill_tree_sens(self, function):
        def wrapper(*args,**kw):
            self.browser.set_sens(False)
            self.stop_all_btn.set_sensitive(True)
            self.break_btn.set_sensitive(True)
            self.source_tree.set_sensitive(False)
            function(*args, **kw)
            self.browser.set_sens(True)
            self.stop_all_btn.set_sensitive(False)
            self.break_btn.set_sensitive(False)
            self.source_tree.set_sensitive(True)
        return wrapper

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        close_conn()
        self.status.statusicon.set_visible(False)
        gtk.main_quit()
        return

    def prepare_loglist(self):
        logw = self.browser.get_logs_list_window()
        loglist = logw.log_list
        loglist.new_logs(self.index_t.get_active())
        #logw.filter_logs.set_sql()
        return (logw, loglist)

    def callback(self, text="Working..."):
        self.progressbar.set_fraction(self.frac*self.count)
        self.count+=1
        self.progressbar.set_text(text)
        while gtk.events_pending():
            gtk.main_iteration()
        return self.signals['stop'] or self.signals['break']

    def mpcallback(self, e_stop):
        self.progressbar.pulse()
        if self.signals['stop'] or self.signals['break']:
            e_stop.set()
        while gtk.events_pending():
            gtk.main_iteration()
        

    @profiler.time_it
    def show_logs(self, *args):
        self.break_btn.set_sensitive(True)
        self.stop_all_btn.set_sensitive(True)
        self.browser.set_sens(False)
        self.signals['stop'] = False
        self.signals['break'] = False
        sources = self.source_tree.get_log_sources()
        if sources[0] or sources[1]:
            logw, loglist = self.prepare_loglist()
            self.frac = 1.0 / (len(sources[0]+sources[1])+1)
            self.count = 0
            dates = (self.date_filter.get_active() and
                     self.date_filter.get_dates or
                     (datetime.min.isoformat(' '), datetime.max.isoformat(' ')))
            if not config.MULTIPROCESS:
                process(loglist.table, sources, dates, self.callback)
            else:
                self.frac = 0.01 if self.frac < 0.01 else self.frac
                self.progressbar.set_pulse_step(self.frac)
                self.progressbar.set_text("Working...")
                mp_process(loglist.table, sources, dates, self.mpcallback)
            if self.signals['break']:
                loglist.clear()
                self.progressbar.set_fraction(0.0)
                self.progressbar.set_text("")
            else:
                self.break_btn.set_sensitive(False)
                self.stop_all_btn.set_sensitive(False)
                self.progressbar.set_fraction(1 - self.frac)
                self.progressbar.set_text("Executing query...")
                logw.fill()
                self.progressbar.set_fraction(1.0)
                self.progressbar.set_text("Complete")
        else:
            self.break_btn.set_sensitive(False)
            self.stop_all_btn.set_sensitive(False)
        self.browser.set_sens(True)
