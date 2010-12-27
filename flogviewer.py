#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
""" Demonstration using editable and activatable CellRenderers """
import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from servers_log import logs
#from evs import *
import datetime
#import threading
import net_time
from logworker import *
import logworker
from widgets.date_time import DateFilter
from widgets.evt_type import EventTypeFilter
from widgets.content import ContentFilter
from widgets.quantity import QuantityFilter
from widgets.logs_tree import FileServersTree, ServersTree
#import Queue
from widgets.logs_notebook import LogsNotebook
import time
import sys
from multiprocessing import Process, Queue, Event, Manager

class GUI_Controller:
    """ The GUI class is the controller for our application """
    def __init__(self):
        # setup the main window
        self.proc_queue = Queue()
        self.list_queue = Queue()
        self.evt_queue = Queue()
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200,800)
        self.tree_frame = gtk.Frame(label="File Logs")

        self.filter_frame = gtk.Frame(label="Filter")
        self.filter_box = gtk.VBox()

        self.date_filter = DateFilter()
        self.content_filter = ContentFilter()


        self.logs_frame = gtk.Frame(label="Logs")
        self.button_box = gtk.HButtonBox()
        self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        self.progress = gtk.ProgressBar()
        self.progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.stop_all_btn = gtk.Button('Stop')
        self.stop_all_btn.connect('clicked', self.stop_all)
        self.allstop = threading.Event()
        self.main_box = gtk.HBox()
        self.control_box = gtk.VBox()
        self.logframe = LogsNotebook()
        self.serversw1 = FileServersTree()
        self.serversw1.show()
        self.serversw2 = ServersTree(logs)
        self.serversw2.show()
        self.log_ntb = gtk.Notebook()
        self.file_label = gtk.Label("Filelogs")
        self.evt_label = gtk.Label("Eventlogs")
        self.file_label.show()
        self.evt_label.show()
        self.log_ntb.append_page(self.serversw2, self.evt_label)
        self.log_ntb.append_page(self.serversw1, self.file_label)
        self.log_ntb.show_all()
        self.build_interface()
        self.root.show_all()
        self.stop_evt = Event()
        self.init_threads()
        return

    def init_threads(self):
        self.manager = Manager()
        self.LOGS_FILTER = self.manager.dict()
        self.event_process = LogWorker(self.evt_queue, self.list_queue, self.stop_evt, self.LOGS_FILTER)
        self.event_process.start()
        self.threads = []
        for t in range(3):
             t=FileLogWorker(self.proc_queue,self.list_queue,self.stop_evt, self.LOGS_FILTER)
             self.threads.append(t)
             t.start()
        self.filler = LogListFiller(self.list_queue)
        self.filler.start()

    def stop_all(self, *args):
        def queue_clear():
            while not self.proc_queue.empty():
                try:
                    self.proc_queue.get_nowait()
                except Queue.Empty:
                    break
        threading.Thread(target=queue_clear).start()
        self.stop_evt.set()
        #print ServersStore.prepare_files_for_parse()

    def build_interface(self):
        self.filter_frame.add(self.filter_box)
        self.filter_box.pack_start(self.date_filter, False, False)
        self.filter_box.pack_start(self.content_filter, False, False)
        self.button_box.pack_start(self.show_button)
        self.button_box.pack_start(self.stop_all_btn)
        self.control_box.pack_start(self.log_ntb, True, True)
        self.control_box.pack_start(self.filter_frame, False, False)
        self.control_box.pack_start(self.button_box, False, False, 5)
        self.control_box.pack_start(self.progress, False, False)
        self.main_box.pack_start(self.control_box, False, False)
        self.main_box.pack_start(self.logframe, True, True)
        self.root.add(self.main_box)

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        gtk.main_quit()
        return

    def show_logs(self, params):
        self.stop_evt.clear()
        flogs = self.serversw1.model.prepare_files_for_parse()
        evlogs = [[s[1], s[0]] for s in self.serversw2.model.get_active_servers()]
        if flogs or evlogs:
            self.logframe.get_current_loglist.clear()
            self.filler.model = self.logframe.get_current_loglist
            #fl_count = len(flogs)
            #frac = 1.0/(fl_count)

            self.LOGS_FILTER['date'] = self.date_filter.get_active() and self.date_filter.get_dates or ()
            self.LOGS_FILTER['types'] = [] #self.evt_type_filter.get_active() and self.evt_type_filter.get_event_types or []
            if net_time.time_error_flag:
                net_time.show_time_warning(self.root)
            self.LOGS_FILTER['content'] = self.content_filter.get_active() and self.content_filter.get_cont or ("","")
            self.LOGS_FILTER['last'] = 0 #self.quantity_filter.get_active() and self.quantity_filter.get_quant or 0

            pr1 = Process(target=evl_preparator, args=(evlogs,self.evt_queue,))
            pr1.start()
            pr2 = Process(target=file_preparator, args=(flogs,self.LOGS_FILTER,self.proc_queue,))
            pr2.start()

if __name__ == '__main__':
    gtk.gdk.threads_init()
    myGUI = GUI_Controller()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
