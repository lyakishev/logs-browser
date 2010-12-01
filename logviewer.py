#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
""" Demonstration using editable and activatable CellRenderers """
import pygtk
pygtk.require("2.0")
import gtk, gobject
from servers_log import logs
from evs import *
import datetime
import threading

class GUI_Controller:
    """ The GUI class is the controller for our application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200,800)
        self.tree_frame = gtk.Frame(label="Event Logs")
        self.event_frame = gtk.Frame(label="Event types")
        self.event_box = gtk.VBox()
        self.evt_checkboxes = {}
        for evt in evt_dict.itervalues():
            self.evt_checkboxes[evt]=gtk.CheckButton(label=evt)
            if "ERROR" in evt:
                self.evt_checkboxes[evt].set_active(True)

        self.action_frame = gtk.Frame(label="Actions")
        self.action_box = gtk.VBox()
        self.all_radiobutton = gtk.RadioButton(None, "All")
        self.date_radiobutton = gtk.RadioButton(self.all_radiobutton,
                                                "By Date:")
        now = datetime.datetime.now()
        self.from_hours_adjustment = gtk.Adjustment(value=now.hour, lower=0, upper=23, step_incr=1)
        self.from_minute_adjustment =gtk.Adjustment(value=now.minute, lower=0, upper=59, step_incr=1)
        self.from_second_adjustment = gtk.Adjustment(value=now.second, lower=0, upper=59, step_incr=1)

        self.to_hours_adjustment = gtk.Adjustment(value=now.hour, lower=0, upper=23, step_incr=1)
        self.to_minute_adjustment =gtk.Adjustment(value=now.minute, lower=0, upper=59, step_incr=1)
        self.to_second_adjustment = gtk.Adjustment(value=now.second, lower=0, upper=59, step_incr=1)

        self.fromto_table = gtk.Table(2, 8, False)
        self.from_label = gtk.Label("From")
        self.fromyear_entry = gtk.Entry(10)
        self.fromyear_entry.set_text(now.strftime("%d.%m.%Y"))
        self.fromhours_spin = gtk.SpinButton(adjustment=self.from_hours_adjustment)
        self.fromminutes_spin = gtk.SpinButton(adjustment=self.from_minute_adjustment)
        self.fromseconds_spin = gtk.SpinButton(adjustment=self.from_second_adjustment)
        self.to_label = gtk.Label("To")
        self.toyear_entry = gtk.Entry(10)
        self.toyear_entry.set_text(now.strftime("%d.%m.%Y"))
        self.tohours_spin = gtk.SpinButton(adjustment=self.to_hours_adjustment)
        self.tominutes_spin = gtk.SpinButton(adjustment=self.to_minute_adjustment)
        self.toseconds_spin = gtk.SpinButton(adjustment=self.to_second_adjustment)

        self.last_radiobutton = gtk.RadioButton(self.all_radiobutton, "Last:")
        self.last_adjustment = gtk.Adjustment(value=3, lower=1, upper=100, step_incr=1)
        self.last_spinbutton = gtk.SpinButton(adjustment=self.last_adjustment)
        self.last_box = gtk.HBox()
        self.startstop_radiobutton = gtk.RadioButton(self.all_radiobutton,
                                                    "Stop")
        self.logs_frame = gtk.Frame(label="Logs")
        self.button_box = gtk.HButtonBox()
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
	self.progress_table = gtk.Table(2,2,False)
        self.progress = gtk.ProgressBar()
        self.progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.pulse_progress = gtk.ProgressBar()
        self.pulse_progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
	self.stop_current_btn = gtk.Button('X')
	self.stop_all_btn = gtk.Button('X')
        self.main_box = gtk.HBox()
        self.control_box = gtk.VBox()
        self.eventlogs_window = gtk.ScrolledWindow()
        self.eventlogs_window.set_policy(gtk.POLICY_NEVER,
                                            gtk.POLICY_AUTOMATIC)
        # Get the model and attach it to the view
        self.eventlogs_model = ServersStore.get_model()
        self.eventlogs_view = ServersDisplay.make_view( self.eventlogs_model )
        # Add our view into the main window
        self.eventlogs_window.add_with_viewport(self.eventlogs_view)
        
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.logs_model = LogsStore.get_model()
	self.logs_model.set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        self.logs_view = LogsDisplay.make_view( self.logs_model )
        self.logs_window.add_with_viewport(self.logs_view)

        self.build_interface()
        self.root.show_all()
        return

    def build_interface(self):
        for chb in self.evt_checkboxes.itervalues():
            self.event_box.pack_start(chb, False, False, 1)
        self.fromto_table.attach(self.from_label, 0, 1, 0, 2, xoptions=0,
                                    yoptions=0, xpadding=10)
        self.fromto_table.attach(self.fromyear_entry, 1, 4, 1, 2, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromhours_spin, 1, 2, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromminutes_spin, 2, 3, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromseconds_spin, 3, 4, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.to_label, 4, 5, 0, 2, xoptions=0,
                                    yoptions=0, xpadding=10)
        self.fromto_table.attach(self.toyear_entry, 5, 8, 1, 2, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.tohours_spin, 5, 6, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.tominutes_spin, 6, 7, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.toseconds_spin, 7, 8, 0, 1, xoptions=0,
                                    yoptions=0)


        self.last_box.pack_start(self.last_radiobutton, False, False)
        self.last_box.pack_start(self.last_spinbutton, False, False, 9)

        self.action_box.pack_start(self.all_radiobutton)
        self.action_box.pack_start(self.date_radiobutton)
        self.action_box.pack_start(self.fromto_table)
        self.action_box.pack_start(self.last_box)
        self.action_box.pack_start(self.startstop_radiobutton)
        self.tree_frame.add(self.eventlogs_window)
        self.logs_frame.add(self.logs_window)
        self.event_frame.add(self.event_box)
        self.action_frame.add(self.action_box)
        self.button_box.pack_start(self.show_button)
        self.control_box.pack_start(self.tree_frame, True, True)
        self.control_box.pack_start(self.event_frame, False, False)
        self.control_box.pack_start(self.action_frame, False, False)
        self.control_box.pack_start(self.button_box, False, False, 5)

        #self.control_box.pack_start(self.progress, False, False)

	self.progress_table.attach(self.progress,0,1,0,1)
	self.progress_table.attach(self.stop_all_btn,1,2,0,1,xoptions=0,yoptions=0)
	self.progress_table.attach(self.pulse_progress,0,1,1,2)
	self.progress_table.attach(self.stop_current_btn,1,2,1,2,xoptions=0,yoptions=0)
        self.control_box.pack_start(self.progress_table, False, False)
        
	self.main_box.pack_start(self.control_box, False, False)
        self.main_box.pack_start(self.logs_frame, True, True)
        self.root.add(self.main_box)
    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        gtk.main_quit()
        return

    def show_logs(self, params):
        self.logs_model.clear()
        evlogs = self.get_active_servers()
        types = self.get_event_types()
        evl_count = len(evlogs)
        frac = 1.0
        if self.all_radiobutton.get_active() == True:
            for comp, log in evlogs:
                self.progress.set_text("%s %s" % (comp,log))
                self.logs+=getEventLogsAll(comp, log, types)
                self.progress.set_fraction(frac/evl_count)
                frac+=1
                while gtk.events_pending():
                    gtk.main_iteration(False)
        elif self.date_radiobutton.get_active() == True:
            st_date = datetime.datetime.strptime(self.fromyear_entry.get_text(),
                                                '%d.%m.%Y')
            start_date = datetime.datetime(
                st_date.year, st_date.month, st_date.day,
                self.fromhours_spin.get_value_as_int(),
                self.fromminutes_spin.get_value_as_int(),
                self.fromseconds_spin.get_value_as_int()
            )

            e_date = datetime.datetime.strptime(self.toyear_entry.get_text(),
                                                '%d.%m.%Y')
            end_date = datetime.datetime(
                e_date.year, e_date.month, e_date.day,
                self.tohours_spin.get_value_as_int(),
                self.tominutes_spin.get_value_as_int(),
                self.toseconds_spin.get_value_as_int()
            )
            for comp, log in evlogs:
                self.progress.set_text("%s %s" % (comp,log))
                for l in getEventLogs(comp, log):
		    self.pulse_progress.pulse()
                    while gtk.events_pending():
                    	gtk.main_iteration(False)
                    if l['evt_type'] in types:
                        if l['the_time']<=end_date and l['the_time']>=start_date:   
                            self.logs_model.append((l['the_time'], l['computer'], l['logtype'], l['evt_type'], l['source'], l['msg']))   
                        if l['the_time']<start_date:
                            break
                self.progress.set_fraction(frac/evl_count)
                frac+=1
		self.stop_curr = False
        elif self.last_radiobutton.get_active() == True:
            n = self.last_spinbutton.get_value_as_int()
            for comp, log in evlogs:
		counter = 0
                self.progress.set_text("%s %s" % (comp,log))
                for l in getEventLogs(comp, log):
                    while gtk.events_pending():
                    	gtk.main_iteration(False)
                    if counter<n:
                        if l['evt_type'] in types:
                            self.logs_model.append((l['the_time'], l['computer'], l['logtype'], l['evt_type'], l['source'], l['msg']))   
                            counter+=1
		    else:
			break
		self.progress.set_fraction(frac/evl_count)
                frac+=1
        self.progress.set_text("Complete")
        self.progress.set_fraction(1.0)

    def get_event_types(self):
        types = []
        for t in self.evt_checkboxes:
            if self.evt_checkboxes[t].get_active() == True:
                types.append(t)
        return types

    def get_active_servers(self):
        logs_for_process = []
        stands = self.eventlogs_model.iter_children(None)
        while stands:
            servers = self.eventlogs_model.iter_children(stands)
            while servers:
                logs = self.eventlogs_model.iter_children(servers)
                while logs:
                    if self.eventlogs_model.get_value(logs, 1) == True:
                        logs_for_process.append(
                            [
                                self.eventlogs_model.get_value(servers,0),
                                self.eventlogs_model.get_value(logs, 0)
                            ]
                        )
                    logs = self.eventlogs_model.iter_next(logs)
                servers = self.eventlogs_model.iter_next(servers)
            stands = self.eventlogs_model.iter_next(stands)
        return logs_for_process

    def run(self):
        """ run is called to set off the GTK mainloop """
        gtk.main()
        return  

class ServersModel:
    """ The model class holds the information we want to display """
    def __init__(self):
        """ Sets up and populates our gtk.TreeStore """
        """!!!Rewrite to recursive!!!!"""
        self.tree_store = gtk.TreeStore( gobject.TYPE_STRING,
                                         gobject.TYPE_BOOLEAN )
        # places the global people data into the list
        # we form a simple tree.
        for item in sorted(logs.keys()):
            parent = self.tree_store.append( None, (item, None) )
            for subitem in sorted(logs[item].keys()):
                child = self.tree_store.append( parent, (subitem,None) )
                for subsubitem in logs[item][subitem]:
                    self.tree_store.append( child, (subsubitem,None) )
        return
    def get_model(self):
        """ Returns the model """
        if self.tree_store:
            return self.tree_store
        else:
            return None

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
                                         gobject.TYPE_STRING )
        # places the global people data into the list
        # we form a simple tree.
    def get_model(self):
        """ Returns the model """
        if self.list_store:
            return self.list_store
        else:
            return None

class DisplayServersModel:
    """ Displays the Info_Model model in a view """
    def make_view( self, model ):
        """ Form a view for the Tree Model """
        self.view = gtk.TreeView( model )
        # setup the text cell renderer and allows these
        # cells to be edited.
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property( 'editable', False )
        #self.renderer.connect( 'edited', self.col0_edited_cb, model )

        # The toggle cellrenderer is setup and we allow it to be
        # changed (toggled) by the user.
        self.renderer1 = gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect( 'toggled', self.col1_toggled_cb, model )
		
        # Connect column0 of the display with column 0 in our list model
        # The renderer will then display whatever is in column 0 of
        # our model .
        self.column0 = gtk.TreeViewColumn("Server", self.renderer, text=0)
		
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        self.column1 = gtk.TreeViewColumn("Show", self.renderer1 )
        self.column1.add_attribute( self.renderer1, "active", 1)
        self.view.append_column( self.column0 )
        self.view.append_column( self.column1 )
        return self.view
    #def col0_edited_cb( self, cell, path, new_text, model ):
    #    """
    #    Called when a text cell is edited.  It puts the new text
    #    in the model so that it is displayed properly.
    #    """
    #    print "Change '%s' to '%s'" % (model[path][0], new_text)
    #    model[path][0] = new_text
    #    return
    def col1_toggled_cb( self, cell, path, model ):
        """
        Sets the toggled state on the toggle button to true or false.

	!!!Rewrite to recursive!!!!
        """
        state = model[path][1] = not model[path][1]
        for child in model[path].iterchildren():
            child[1] = state
            for subchild in child.iterchildren():
                subchild[1] = state
        return

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
        for r, header in enumerate(['Date','Computer', 'Log', 'Type', 'Source', 'Message']):
            self.renderers.append(gtk.CellRendererText())
            self.renderers[r].set_property( 'editable', False )
            self.columns.append(gtk.TreeViewColumn(header, self.renderers[r],
                                text=r))
		
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        for col in self.columns:
            self.view.append_column( col )
            if col.get_title() == "Message":
                col.set_visible(False)
        self.view.connect( 'row-activated', self.show_log)

        return self.view
    #def col0_edited_cb( self, cell, path, new_text, model ):
    #    """
    #    Called when a text cell is edited.  It puts the new text
    #    in the model so that it is displayed properly.
    #    """
    #    print "Change '%s' to '%s'" % (model[path][0], new_text)
    #    model[path][0] = new_text
    #    return
    def show_log( self, path, column, params):
        selection = path.get_selection()
        (model, iter) = selection.get_selected()
        popup = gtk.Window()
        popup.set_title("Log")
        popup.set_default_size(640,480)
        popup_frame = gtk.Frame("Log")
        log_text = gtk.TextView()
        log_text.set_wrap_mode(gtk.WRAP_WORD)
        log_text.get_buffer().set_text("%s\n%s\n%s\n%s\n%s\n\n\n%s" % (
            model.get_value(iter, 0),
            model.get_value(iter, 1),
            model.get_value(iter, 2),
            model.get_value(iter, 3),
            model.get_value(iter, 4),
            model.get_value(iter, 5).decode("string-escape")))
        popup_frame.add(log_text)
        popup.add(popup_frame)
        popup.show_all()
        selection = path.get_selection()
        (model, iter) = selection.get_selected()
        print model.get_value(iter, 0)
        return

#class LogWorker(threading.Thread):
#    stopthread = threading.Event()
#
#    def __init__(self, params):
#        super(LogWorker,self).__init__(self)
#        self.params = params
#
#    def run(self):
#        pass
#        #for 
#        #   if ( self.stopthread.isSet() ):
#        #       self.stopthread.clear()
#        #       break   
#        #   progress
#        #   getlogs
#        #self.stopthread.clear()
#        #
#    
            
    


if __name__ == '__main__':
    ServersStore = ServersModel()
    LogsStore = LogsModel()
    ServersDisplay = DisplayServersModel()
    LogsDisplay = DisplayLogsModel()
    myGUI = GUI_Controller()
    myGUI.run()
