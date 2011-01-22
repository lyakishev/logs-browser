# vim: ts=4:sw=4:tw=78:nowrap
""" Demonstration using editable and activatable CellRenderers """
import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
#from evs import *
import datetime
#import threading
import net_time
from logworker import *
import logworker
from widgets.date_time import DateFilter
from widgets.evt_type import EventTypeFilter
#from widgets.content import ContentFilter
#from widgets.quantity import QuantityFilter
from widgets.logs_tree import FileServersTree, ServersTree
#import Queue
from widgets.logs_notebook import LogsNotebook
import time
import sys
from multiprocessing import Process, Queue, Event, Manager, freeze_support
from Queue import Empty as qEmpty
import threading
from widgets.status_icon import StatusIcon

class GUI_Controller:
    """ The GUI class is the controller for our application """
    def __init__(self):
        # setup the main window
        self.proc_queue = Queue()
        self.list_queue = Queue()
        self.evt_queue = Queue()
        self.compl_queue = Queue()
        self.stp_compl = threading.Event()
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200,800)
        self.tree_frame = gtk.Frame(label="File Logs")

        self.filter_frame = gtk.Frame(label="Filter")
        self.filter_box = gtk.VBox()

        self.date_filter = DateFilter()
        self.status = StatusIcon(self.date_filter, self.root)
        self.ev_filter = EventTypeFilter(evt_dict, 'ERROR')


        self.logs_frame = gtk.Frame(label="Logs")
        self.button_box = gtk.HButtonBox()
        self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        self.stop_all_btn = gtk.Button('Stop')
        self.stop_all_btn.connect('clicked', self.stop_all)
        self.allstop = threading.Event()
        self.main_box = gtk.HPaned()
        self.control_box = gtk.VBox()
        self.logframe = LogsNotebook()
        self.serversw1 = FileServersTree()
        self.serversw1.show()
        self.serversw2 = ServersTree()
        self.serversw2.show()
        self.log_ntb = gtk.Notebook()
        self.log_ntb.connect("switch-page", self.show_hide_ev_filter)
        self.file_label = gtk.Label("Filelogs")
        self.evt_label = gtk.Label("Eventlogs")
        self.file_label.show()
        self.evt_label.show()
        self.log_ntb.append_page(self.serversw1, self.file_label)
        self.log_ntb.append_page(self.serversw2, self.evt_label)
        self.log_ntb.show_all()
        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.build_interface()
        self.root.show_all()
        self.ev_filter.hide()
        self.stop_evt = Event()
        self.init_threads()
        return

    def show_hide_ev_filter(self, notebook, page, page_num):
        if page_num == 0:
            self.ev_filter.hide()
        else:
            self.ev_filter.show()
            

    def init_threads(self):
        self.manager = Manager()
        self.LOGS_FILTER = self.manager.dict()
        self.f_manager = Manager()
        self.formats = self.f_manager.dict()
        self.event_process = LogWorker(self.evt_queue, self.list_queue,self.compl_queue, self.stop_evt, self.LOGS_FILTER)
        self.event_process.start()
        self.threads = []
        for t in range(3):
             t=FileLogWorker(self.proc_queue,self.list_queue,
                             self.compl_queue, self.stop_evt,
                             self.LOGS_FILTER, self.formats)
             self.threads.append(t)
             t.start()

    def stop_all(self, *args):
        def queue_clear():
            while not self.proc_queue.empty():
                try:
                    self.proc_queue.get_nowait()
                except qEmpty:
                    break
                else:
                    self.compl_queue.put(1)
            while not self.evt_queue.empty():
                try:
                    self.evt_queue.get_nowait()
                except qEmpty:
                    break
                else:
                    self.compl_queue.put(1)
        threading.Thread(target=queue_clear).start()
        self.stop_evt.set()

    def build_interface(self):
        self.filter_frame.add(self.filter_box)
        self.filter_box.pack_start(self.ev_filter, False, False)
        self.filter_box.pack_start(self.date_filter, False, False)
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
        for t in self.threads:
            t.terminate()
        self.event_process.terminate()
        gtk.main_quit()
        sys.exit()
        return

    def progress(self, q, frac, fl_count):
        tm = datetime.datetime.now()
        self.progressbar.set_fraction(0.0)
        self.progressbar.set_text("Working...")
        counter = 0
        check_half_frac=1.0-frac/2.
        while 1:
            curr = self.progressbar.get_fraction()
            piece = q.get()
            counter += 1
            if counter == fl_count:
                gtk.gdk.threads_enter()
                self.progressbar.set_fraction(1.0)
                self.progressbar.set_text("Complete")
                self.show_button.set_sensitive(True)
                gtk.gdk.threads_leave()
                break
            elif counter == fl_count-1:
                self.progressbar.set_text("Filling table...")
                self.stp_compl.set()
            gtk.gdk.threads_enter()
            self.progressbar.set_fraction(curr+frac)
            gtk.gdk.threads_leave()
        print datetime.datetime.now()-tm

    def show_logs(self, params):
        self.stop_evt.clear()
        self.stp_compl.clear()
        self.cur_view = self.logframe.get_current_view
        self.cur_model = self.logframe.get_current_loglist
        flogs = self.serversw1.model.prepare_files_for_parse()
        evlogs = [[s[1], s[0]] for s in self.serversw2.model.get_active_servers()]
        if flogs or evlogs:
            self.cur_model.clear()
            self.logframe.get_current_logs_store.rows_set.clear()
            self.cur_model.set_default_sort_func(lambda *args: -1)
            self.cur_model.set_sort_column_id(-1, gtk.SORT_ASCENDING)
            self.LOGS_FILTER['date'] = self.date_filter.get_active() and self.date_filter.get_dates or (datetime.datetime.min, datetime.datetime.max)
            self.LOGS_FILTER['types'] = self.ev_filter.get_active() and self.ev_filter.get_event_types or []
            if net_time.time_error_flag:
                net_time.show_time_warning(self.root)
            self.LOGS_FILTER['content'] = ("","")#self.content_filter.get_active() and self.content_filter.get_cont or ("","")
            self.LOGS_FILTER['last'] = 0 #self.quantity_filter.get_active() and self.quantity_filter.get_quant or 0
            n_flogs=file_preparator(flogs,self.LOGS_FILTER)
            fl_count = len(n_flogs)+len(evlogs)+1
            frac = 1.0/(fl_count)
            p1=Process(target=queue_filler, args=(evlogs, self.evt_queue,))
            p1.start()
            p2=Process(target=queue_filler, args=(n_flogs, self.proc_queue,))
            p2.start()
            pr3 = threading.Thread(target=self.progress, args=(self.compl_queue, frac, fl_count))
            pr3.start()
            pr4 = LogListFiller(self.list_queue, self.cur_model, self.cur_view, self.stp_compl, self.compl_queue)#, self.fillprogressbar)
            pr4.start()
            self.show_button.set_sensitive(False)



if __name__ == '__main__':
    freeze_support()
    gtk.gdk.threads_init()
    myGUI = GUI_Controller()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
