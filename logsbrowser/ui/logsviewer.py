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

class LogsViewer:
    """ The GUI class is the controller for application """
    def __init__(self, process):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Logs Browser")
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

        self.source_tree = LogsTrees()

        self.browser = LogsNotebook(self.source_tree, self.show_button)

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

        button_box.pack_start(self.show_button)
        button_box.pack_start(stop_all_btn)
        button_box.pack_start(break_btn)
        control_box.pack_start(self.source_tree, True, True)
        control_box.pack_start(self.date_filter, False, False)
        control_box.pack_start(options_frame, False, False)
        control_box.pack_start(button_box, False, False, 5)
        control_box.pack_start(self.progressbar, False, False)
        main_box.pack1(control_box, False, False)
        main_box.pack2(self.browser, True, False)
        self.root.add(main_box)
        self.root.show_all()
        self.process = process

    def stop_all(self, *args):
        self.stop = True

    def break_all(self, *args):
        self.break_ = True

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
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
        self.progressbar.set_fraction(self.frac*self.count-1)
        self.count+=1
        self.progressbar.set_text(text)
        while gtk.events_pending():
            gtk.main_iteration()
        return self.stop or self.break_

    def show_logs(self, *args):
        self.browser.set_sens(False)
        self.stop = False
        self.break_ = False
        logw, loglist = self.prepare_loglist()
        sources = self.source_tree.get_log_sources()
        self.frac = 1.0 / (len(sources[0]+sources[1])+1)
        print self.frac
        self.count = 1
        dates = (self.date_filter.get_active() and
                 self.date_filter.get_dates or
                 (datetime.min, datetime.max))
        self.process(loglist.table, sources, dates, self.callback)
        if self.break_:
            loglist.clear()
            self.progressbar.set_fraction(0.0)
            self.progressbar.set_text("")
        else:
            self.progressbar.set_text("Filling table...")
            logw.fill()
            self.progressbar.set_fraction(1.0)
            self.progressbar.set_text("Complete")
        self.browser.set_sens(True)