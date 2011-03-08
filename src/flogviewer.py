#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
""" Demonstration using editable and activatable CellRenderers """
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import datetime
from net_time import GetTrueTime
from logworker import *
from widgets.date_time import DateFilter
from widgets.logs_tree import FileServersTree, ServersTree
from widgets.logs_notebook import LogsNotebook
import sys
from multiprocessing import Process, Queue, Event, Manager, freeze_support
from Queue import Empty as qEmpty
import threading
from widgets.status_icon import StatusIcon
if sys.platform == 'win32':
    from evlogworker import *
    from widgets.evt_type import EventTypeFilter


class GUI_Controller:
    """ The GUI class is the controller for our application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200, 800)
        self.tree_frame = gtk.Frame(label="File Logs")

        self.filter_frame = gtk.Frame(label="Filter")
        self.filter_box = gtk.VBox()

        self.date_filter = DateFilter()
        self.status = StatusIcon(self.date_filter, self.root)

        self.logs_frame = gtk.Frame(label="Logs")
        self.button_box = gtk.HButtonBox()
        self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        self.stop_all_btn = gtk.Button('Stop')
        #self.stop_all_btn.connect('clicked', self.stop_all)
        self.main_box = gtk.HPaned()
        self.control_box = gtk.VBox()
        self.serversw1 = FileServersTree()
        self.serversw1.show()
        self.logframe = LogsNotebook(self.serversw1)
        self.log_ntb = gtk.Notebook()
        self.file_label = gtk.Label("Filelogs")
        self.file_label.show()
        self.log_ntb.append_page(self.serversw1, self.file_label)
        self.log_ntb.show_all()
        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.build_interface()
        self.root.show_all()
        #if sys.platform == 'win32':
        #    self.show_ev_widgets()
        return

    def show_ev_widgets(self):
        self.ev_filter = EventTypeFilter(EVT_DICT, 'ERROR')
        self.evt_label = gtk.Label("Eventlogs")
        self.evt_label.show()
        self.log_ntb.connect("switch-page", self.show_hide_ev_filter)
        self.serversw2 = ServersTree()
        self.serversw2.show()
        self.log_ntb.append_page(self.serversw2, self.evt_label)
        self.filter_box.pack_start(self.ev_filter, False, False)
        self.root.show_all()
        self.ev_filter.hide()

    def show_hide_ev_filter(self, notebook, page, page_num):
        if page_num == 0:
            self.ev_filter.hide()
        else:
            self.ev_filter.show()

    def build_interface(self):
        self.filter_frame.add(self.filter_box)
        self.filter_box.pack_end(self.date_filter, False, False)
        self.button_box.pack_start(self.show_button)
        self.button_box.pack_start(self.stop_all_btn)
        self.control_box.pack_start(self.log_ntb, True, True)
        self.control_box.pack_start(self.filter_frame, False, False)
        self.control_box.pack_start(self.button_box, False, False, 5)
        self.control_box.pack_start(self.progressbar, False, False)
        self.main_box.pack1(self.control_box, False, False)
        self.main_box.pack2(self.logframe, True, False)
        self.root.add(self.main_box)

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        self.status.statusicon.set_visible(False)
        gtk.main_quit()
        return

    def progress(self, q, frac, fl_count):
        tm = datetime.datetime.now()
        self.progressbar.set_fraction(0.0)
        self.progressbar.set_text("Working...")
        counter = 0
        while 1:
            curr = self.progressbar.get_fraction()
            q.get()
            counter += 1
            if counter == fl_count:
                gtk.gdk.threads_enter()
                self.progressbar.set_fraction(1.0)
                self.progressbar.set_text("Complete")
                self.show_button.set_sensitive(True)
                gtk.gdk.threads_leave()
                break
            elif counter == fl_count - 1:
                print "Parse: ", datetime.datetime.now()-tm
                self.progressbar.set_text("Filling table...")
                self.stp_compl.set()
            gtk.gdk.threads_enter()
            self.progressbar.set_fraction(curr + frac)
            gtk.gdk.threads_leave()
        print datetime.datetime.now() - tm

    def show_logs(self, params):
        self.cur_view = self.logframe.get_current_view
        self.cur_model = self.logframe.get_current_loglist
        flogs = self.serversw1.model.prepare_files_for_parse()
        try:
            evlogs = [[s[1], s[0]] for s in\
                        self.serversw2.model.get_active_servers()]
        except AttributeError:
            evlogs = []
        if flogs or evlogs:
            loglist = self.logframe.get_current_logs_store
            loglist.clear()
            dates = self.date_filter.get_active() and\
                                       self.date_filter.get_dates or\
                                       (datetime.datetime.min,
                                        datetime.datetime.max)
            if GetTrueTime.time_error_flag:
                GetTrueTime.show_time_warning(self.root)
            n_flogs = file_preparator(flogs)
            fl_count = len(n_flogs) + len(evlogs)
            frac = 1.0 / (fl_count)
            loglist.set_hash([evlogs,flogs,dates,datetime.datetime.now()])
            loglist.create_new_table()
            dt = datetime.datetime.now()
            for path, log in n_flogs:
                loglist.insert_many(filelogworker(dates,path,log))
                loglist.db_conn.commit()
            print datetime.datetime.now() - dt
            loglist.execute("""select date, log, type, source from this group by
                               date order by date desc""""")
            print datetime.datetime.now() - dt
            

if __name__ == '__main__':
    freeze_support()
    gtk.gdk.threads_init()
    myGUI = GUI_Controller()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
