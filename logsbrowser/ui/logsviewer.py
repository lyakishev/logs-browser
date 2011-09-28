#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap

VERSION = 'DEV'

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from datetime import datetime
from datetimef import DateFilter
from logstree import SourceManagerUI
from logsnotebook import LogsNotebook
import sys
from statusicon import StatusIcon
import config
import utils.profiler as profiler
from process import process, mp_process
from db.engine import close_conn
from operator import setitem
import os
import subprocess
from utils.monitor import ConfigMonitor
try:
    from imp import reload
except ImportError:
    pass


def reload_config():
    reload(config)

monitor = ConfigMonitor("config/logsbrowser.cfg")
monitor.register_action(reload_config)


class LogsViewer:
    """ The GUI class is the controller for application """

    ui = """<ui>
          <menubar name="MenuBar">
            <menu action="File">
              <menuitem action="Quit"/>
            </menu>
            <menu action="Settings">
                <menu action="Configuration">
                  <menuitem action="Application"/>
                  <menuitem action="Sources"/>
                  <menuitem action="Queries"/>
                  <menuitem action="Actions"/>
                </menu>
            </menu>
            <menu action="?">
              <menuitem action="Help"/>
              <menuitem action="About"/>
            </menu>
          </menubar>
          </ui>
        """

    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Logs Browser")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(config.WIDTH_MAIN_WINDOW, config.HEIGHT_MAIN_WINDOW)

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

        self.source_tree = SourceManagerUI(self.progressbar, self.fill_tree_sens,
                                     self.signals, self.root)

        self.browser = LogsNotebook(self.source_tree, self.show_button)
        self.source_tree.fill_combo()


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
        uimanager = gtk.UIManager()
        accelgroup = uimanager.get_accel_group()
        self.root.add_accel_group(accelgroup)
        actiongroup = gtk.ActionGroup('LogsBrowser')
        self.actiongroup = actiongroup
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Quit', None,
                                  'Quit the Program', self.destroy_cb),
                                 ('File', None, '_File'),
                                 ('?', None, '_?'),
                                ('Settings', None, '_Settings'),
                                ('Configuration', None, '_Configuration'),
                                  ("Application", None,
                                      "_Application", None, None,
                                      self.edit_config),
                                  ("Sources", None, "_Sources", None, None,
                                      self.edit_config),
                                  ("Queries", None, "_Queries", None, None,
                                      self.edit_config),
                                  ("Actions", None, "_Actions", None, None,
                                      self.edit_config),
                                ('Help', gtk.STOCK_HELP, '_Help', None,
                                  'Manual', self.show_help),
                                  ('About', gtk.STOCK_ABOUT, '_About', None,
                                  'About', self.show_about)])

        uimanager.insert_action_group(actiongroup, 0)
        merge_id = uimanager.add_ui_from_string(self.ui)
        menubar = uimanager.get_widget('/MenuBar')

        menu_box = gtk.VBox()
        menu_box.pack_start(menubar, False, False)
        menu_box.pack_start(main_box)
        self.root.add(menu_box)
        self.root.show_all()
        #self.source_tree.fill(config.FILL_LOGSTREE_AT_START)

    def edit_config(self, action):
        name = action.get_name()
        if name == "Application":
            command = "%s %s" % (config.PROGRAM_CONFIG_EDITOR, "config/logsbrowser.cfg")
        elif name == "Sources":
            command = "%s %s" % (config.SOURCES_XML_EDITOR, config.SOURCES_XML)
        elif name == "Queries":
            command = "%s %s" % (config.QUERIES_FILE_EDITOR, config.QUERIES_FILE)
        elif name == "Actions":
            command = "%s %s" % (config.SELECTS_EDITOR, config.SELECTS)
        subprocess.Popen(command)


    def set_from_date(self):
        self.date_filter.fromto_option.from_date.set_now()

    def set_to_date(self):
        self.date_filter.fromto_option.to_date.set_now()

    def show_help(self, *args):
        subprocess.Popen('start %s' % config.HELP_INDEX)

    def show_about(self, *args):
        about = gtk.AboutDialog()
        about.set_property('authors', ['Lyakishev Andrey <lyakav@gmail.com>',
                                       'Chizhikov Vladimir <vladimir.chizh@gmail.com>'])
        about.set_property('version', VERSION)
        about.set_property('website', 'http://bitbucket.org/andy87/logs-browser')
        about.set_name('LogsBrowser')
        about.run()
        about.destroy()

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

    def mpcallback(self, e_stop, val):
        while gtk.events_pending():
            gtk.main_iteration()
        self.progressbar.set_fraction(self.frac*val)
        if self.signals['stop'] or self.signals['break']:
            e_stop.set()


    @profiler.time_it
    def show_logs(self, *args):
        import pdb
        pdb.set_trace()
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
