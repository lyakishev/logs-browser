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
from widgets.date_time import DateFilter
from widgets.evt_type import EventTypeFilter
from widgets.content import ContentFilter
from widgets.quantity import QuantityFilter
from widgets.log_window import LogWindow
from widgets.logs_tree import EventServersModel, FileServersModel, DisplayServersModel

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
        self.eventlogs_window = gtk.ScrolledWindow()
        self.eventlogs_window.set_policy(gtk.POLICY_NEVER,
                                            gtk.POLICY_AUTOMATIC)
        self.eventlogs_model = ServersStore.get_model()
        self.eventlogs_view = ServersDisplay.make_view( self.eventlogs_model )
        self.eventlogs_window.add_with_viewport(self.eventlogs_view)
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.logs_model = LogsStore.get_model()
        self.logs_model.set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        self.logs_view = LogsDisplay.make_view( self.logs_model )
        self.logs_window.add_with_viewport(self.logs_view)
        self.ntb = gtk.Notebook()
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
        self.tree_frame.add(self.eventlogs_window)
        self.logs_frame.add(self.logs_window)
        self.button_box.pack_start(self.show_button)
        self.button_box.pack_start(self.stop_all_btn)
        self.control_box.pack_start(self.tree_frame, True, True)
        self.control_box.pack_start(self.filter_frame, False, False)
        self.control_box.pack_start(self.button_box, False, False, 5)
        self.control_box.pack_start(self.progress, False, False)
        self.main_box.pack_start(self.control_box, False, False)
        self.main_box.pack_start(self.logs_frame, True, True)
        self.ev_label = gtk.Label("EventLogs")
        self.file_label = gtk.Label("FileLogs")
        self.ntb.append_page(self.main_box, tab_label=self.ev_label)
        #self.ntb.append_page(self.file_main_box, tab_label=self.file_label)
        self.root.add(self.ntb)

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        gtk.main_quit()
        return

    def show_logs(self, params):
        self.stop_evt.clear()
        evlogs = ServersStore.get_active_servers()
        if evlogs:
            self.logs_model.clear()
            self.progress.set_fraction(0.0)
            self.progress.set_text("Working...")
            evl_count = len(evlogs)
            frac = 1.0/(evl_count)
            fltr = {}
            fltr['types'] = self.evt_type_filter.get_active() and self.evt_type_filter.get_event_types or []
            fltr['date'] = self.date_filter.get_active() and self.date_filter.get_dates or ()
            fltr['content'] = self.content_filter.get_active() and self.content_filter.get_cont or ("","")
            fltr['last'] = self.quantity_filter.get_active() and self.quantity_filter.get_quant or 0
            #gtk.gdk.threads_init()
            self.sens_list=[self.evt_type_filter,self.date_filter,
                self.content_filter,self.quantity_filter,self.show_button]
            for sl in self.sens_list:
                    sl.set_sensitive(False)
            for comp, log in evlogs:
            #    gtk.gdk.threads_enter()
                self.worker = LogWorker(comp, log, fltr, self.logs_model,
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

class LogsModel:
    """ The model class holds the information we want to display """
    def __init__(self):
        """ Sets up and populates our gtk.TreeStore """
        """!!!Rewrite to recursive!!!!"""
        self.list_store = gtk.ListStore( gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_STRING )
        # places the global people data into the list
        # we form a simple tree.
    def get_model(self):
        """ Returns the model """
        if self.list_store:
            return self.list_store
        else:
            return None

    def highlight(self, pattern):
        for row in self.list_store:
            if pattern in row[5]:
                row[6] = "#FF0000"
            else:
                row[6] = "#FFFFFF"
        

class DisplayLogsModel:
    """ Displays the Info_Model model in a view """
    def make_view( self, model ):
        """ Form a view for the Tree Model """
        self.view = gtk.TreeView( model )
        # setup the text cell renderer and allows these
        # cells to be edited.

        # Connect column0 of the display with column 0 in our list model
        # The renderer will then display whatever is in column 0 of
        # our model .
        self.renderers = []
        self.columns = []
        for r, header in enumerate(['Date','Computer', 'Log', 'Type',\
            'Source', 'Message', 'bgcolor']):
            self.renderers.append(gtk.CellRendererText())
            self.renderers[r].set_property( 'editable', False )
            self.columns.append(gtk.TreeViewColumn(header, self.renderers[r],
                                text=r))
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        for cid, col in enumerate(self.columns):
            self.view.append_column( col )
            if col.get_title() == "Message" or col.get_title() == "bgcolor":
                col.set_visible(False)
            else:
                col.set_sort_column_id(cid)
        self.view.connect( 'row-activated', self.show_log)

        return self.view
    
    def repaint(self):
        for col, ren in zip(self.columns, self.renderers):
            col.set_attributrs(ren, cell_background=6)
        
            


    def show_log( self, path, column, params):
        import pdb
        pdb.set_trace()
        print type(self)
        print type(path)
        print type(column)
        print type(params)
        selection = path.get_selection()
        print type(selection)
        (model, iter) = selection.get_selected()
        msg = model.get_value(iter, 5).decode("string-escape")
        msg = re.sub(r"u[\"'](.+?)[\"']", lambda m: m.group(1), msg, flags=re.DOTALL)
        msg = re.sub(r"\\u\w{4}", lambda m: m.group(0).decode("unicode-escape"), msg)
        txt = "%s\n%s\n%s\n%s\n%s\n\n\n%s" % (
            model.get_value(iter, 0),
            model.get_value(iter, 1),
            model.get_value(iter, 2),
            model.get_value(iter, 3),
            model.get_value(iter, 4),
            msg)
        log_w = LogWindow(txt)
        return

if __name__ == '__main__':
    gtk.gdk.threads_init()
    ServersStore = EventServersModel(logs)
    LogsStore = LogsModel()
    ServersDisplay = DisplayServersModel()
    LogsDisplay = DisplayLogsModel()
    myGUI = GUI_Controller()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    #myGUI.run()
