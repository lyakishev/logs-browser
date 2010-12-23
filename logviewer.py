#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
""" Demonstration using editable and activatable CellRenderers """
import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from servers_log import logs
#from evs import *
import datetime
import threading
from logworker import *
import net_time
from widgets.date_time import DateFilter
from widgets.evt_type import EventTypeFilter
from widgets.content import ContentFilter
from widgets.quantity import QuantityFilter
from widgets.logs_tree import ServersTree
from widgets.logs_list import LogListWindow

class GUI_Controller:
    """ The GUI class is the controller for our application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200,800)
        self.tree_frame = gtk.Frame(label="Event Logs")

        self.filter_frame = gtk.Frame(label="Filter")
        self.filter_box = gtk.VBox()

        self.evt_type_filter = EventTypeFilter(evt_dict, "ERROR")
        self.date_filter = DateFilter()
        self.quantity_filter = QuantityFilter()
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
        self.logframe = LogListWindow()
        self.serversw = ServersTree(logs)
        self.build_interface()
        self.root.show_all()
        self.stop_evt = threading.Event()
        return

    def stop_all(self, *args):
        self.stop_evt.set()

    def build_interface(self):
        self.filter_frame.add(self.filter_box)
        self.filter_box.pack_start(self.evt_type_filter, False, False)
        self.filter_box.pack_start(self.date_filter, False, False)
        self.filter_box.pack_start(self.quantity_filter, False, False)
        self.filter_box.pack_start(self.content_filter, False, False)
        self.button_box.pack_start(self.show_button)
        self.button_box.pack_start(self.stop_all_btn)
        self.control_box.pack_start(self.serversw, True, True)
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
        evlogs = [[s[1], s[0]] for s in self.serversw.model.get_active_servers()]
        if evlogs:
            self.logframe.logs_store.list_store.clear()
            self.progress.set_fraction(0.0)
            self.progress.set_text("Working...")
            evl_count = len(evlogs)
            frac = 1.0/(evl_count)
            fltr = {}
            fltr['types'] = self.evt_type_filter.get_active() and self.evt_type_filter.get_event_types or []
            fltr['date'] = self.date_filter.get_active() and \
                self.date_filter.get_dates or (datetime.datetime.min, \
                datetime.datetime.max)
            if net_time.time_error_flag:
                net_time.show_time_warning(self.root)
            fltr['content'] = self.content_filter.get_active() and self.content_filter.get_cont or ("","")
            fltr['last'] = self.quantity_filter.get_active() and self.quantity_filter.get_quant or 0
            #gtk.gdk.threads_init()
            self.sens_list=[self.evt_type_filter,self.date_filter,
                self.content_filter,self.quantity_filter,self.show_button]
            for sl in self.sens_list:
                    sl.set_sensitive(False)
            for comp, log in evlogs:
            #    gtk.gdk.threads_enter()
                self.worker = LogWorker(comp, log, fltr, self.logframe.logs_store.list_store,
                                            self.progress, frac, self.sens_list,
                                            self.stop_evt)
                self.worker.start()

       # gtk.gdk.threads_leave()


		#self.progress.set_fraction(frac/evl_count)
        #        frac+=1
        #self.progress.set_text("Complete")
        #self.progress.set_fraction(1.0)


#    def run(self):
#        """ run is called to set off the GTK mainloop """
#        gtk.main()
#        return
#

if __name__ == '__main__':
    gtk.gdk.threads_init()
    myGUI = GUI_Controller()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
