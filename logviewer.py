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
from logworker import *

class GUI_Controller:
    """ The GUI class is the controller for our application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200,800)
        self.tree_frame = gtk.Frame(label="Event Logs")
        self.event_box = gtk.VBox()
        self.evt_checkboxes = {}
        for evt in evt_dict.itervalues():
            self.evt_checkboxes[evt]=gtk.CheckButton(label=evt)
            if "ERROR" in evt:
                self.evt_checkboxes[evt].set_active(True)

        self.filter_frame = gtk.Frame(label="Filter")
        self.filter_box = gtk.VBox()
        self.evt_type_frame = gtk.Frame()
        self.evt_type_filter = gtk.CheckButton("Type")


        self.quantity_frame = gtk.Frame()
        self.quantity_filter = gtk.CheckButton("Quantity")
        self.last_label = gtk.Label("Last")
        self.last_adjustment = gtk.Adjustment(value=3, lower=1, upper=100, step_incr=1)
        self.last_spinbutton = gtk.SpinButton(adjustment=self.last_adjustment)
        self.last_box = gtk.HBox()

        self.content_frame = gtk.Frame()
        self.content_filter = gtk.CheckButton("Contains")
        self.like_entry = gtk.Entry()
        self.notlike_entry = gtk.Entry()
        self.like_label = gtk.Label('Like')
        self.notlike_label = gtk.Label('Not like')
        self.content_table = gtk.Table(2,2,False)

        #for fltr in ['evt_type','quantity','date','content']:
        #    getattr(self, '%s_filter' % fltr).connect('toggled', getattr(self,
        #                                              '%s_sens' % fltr))

        self.date_frame = gtk.Frame()
        self.date_filter = gtk.CheckButton("Date")
        self.date_box = gtk.VBox()
        self.date_last_box = gtk.HBox()
        self.last_date_radio = gtk.RadioButton(label='Last')
        self.last_date_adj = gtk.Adjustment(value=1, lower=1, upper=100, step_incr=1)
        self.last_date_spin = gtk.SpinButton(adjustment=self.last_date_adj)
        self.last_date_combo = gtk.combo_box_new_text()
        self.last_date_combo.append_text('seconds')
        self.last_date_combo.append_text('minutes')
        self.last_date_combo.append_text('hours')
        self.last_date_combo.append_text('days')
        self.last_date_combo.set_active(1)
        
        now = datetime.datetime.now()
        self.from_hours_adjustment = gtk.Adjustment(value=now.hour, lower=0, upper=23, step_incr=1)
        self.from_minute_adjustment =gtk.Adjustment(value=now.minute, lower=0, upper=59, step_incr=1)
        self.from_second_adjustment = gtk.Adjustment(value=now.second, lower=0, upper=59, step_incr=1)

        self.to_hours_adjustment = gtk.Adjustment(value=now.hour, lower=0, upper=23, step_incr=1)
        self.to_minute_adjustment =gtk.Adjustment(value=now.minute, lower=0, upper=59, step_incr=1)
        self.to_second_adjustment = gtk.Adjustment(value=now.second, lower=0, upper=59, step_incr=1)

        self.from_label = gtk.RadioButton(self.last_date_radio, label="From")
        self.fromto_table = gtk.Table(2, 8, False)
        self.fromyear_entry = gtk.Entry(10)
        self.fromyear_entry.set_text(now.strftime("%d.%m.%Y"))
        self.fromhours_spin = gtk.SpinButton(adjustment=self.from_hours_adjustment)
        self.fromminutes_spin = gtk.SpinButton(adjustment=self.from_minute_adjustment)
        self.fromseconds_spin = gtk.SpinButton(adjustment=self.from_second_adjustment)
        self.to_label = gtk.CheckButton("To")
        self.to_label.set_active(False)
        self.to_label.connect("toggled", self.to_date_sens)
        self.toyear_entry = gtk.Entry(10)
        self.toyear_entry.set_text(now.strftime("%d.%m.%Y"))
        self.tohours_spin = gtk.SpinButton(adjustment=self.to_hours_adjustment)
        self.tominutes_spin = gtk.SpinButton(adjustment=self.to_minute_adjustment)
        self.toseconds_spin = gtk.SpinButton(adjustment=self.to_second_adjustment)

        self.logs_frame = gtk.Frame(label="Logs")
        self.button_box = gtk.HButtonBox()
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        #self.progress_table = gtk.Table(2,2,False)
        self.progress = gtk.ProgressBar()
        self.progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        #self.pulse_progress = gtk.ProgressBar()
        #self.pulse_progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        #self.stop_current_btn = gtk.Button('X')
        #self.stop_all_btn = gtk.Button('X')
        #self.stop_all_btn.connect('clicked', self.stop_all)
        self.allstop = threading.Event()
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
        self.evt_type_filter.connect('toggled', self.evt_type_sens)
        self.quantity_filter.connect('toggled', self.quantity_sens)
        self.date_filter.connect('toggled', self.date_sens)
        self.content_filter.connect('toggled', self.content_sens)
        self.build_interface()
        self.evt_type_filter.set_active(True)
        self.date_filter.set_active(True)
        self.root.show_all()
        self.evt_type_sens()
        self.quantity_sens()
        self.date_sens()
        self.content_sens()
        self.to_date_sens()
        return

    #def __getattr__(self, name):
    #    if name in ["%s_sens" % i for i in ['evt_type','quantity','date','content']]:
    #        fltr = name.replace("_sens", '')
    #        attr = getattr(self, "%s_filter" % fltr])
    #        frame = getattr(self, "%s_frame" % fltr)
    #        if attr.get_active():
    #            frame.set_sensitive(False)
    #        else:
    #            frame.set_sensitive(True)
                

    def to_date_sens(self, *args): #may do with descriptors
        if self.to_label.get_active():
            self.toyear_entry.set_sensitive(True)
            self.tohours_spin.set_sensitive(True)
            self.tominutes_spin.set_sensitive(True)
            self.toseconds_spin.set_sensitive(True)
        else:
            self.toyear_entry.set_sensitive(False)
            self.tohours_spin.set_sensitive(False)
            self.tominutes_spin.set_sensitive(False)
            self.toseconds_spin.set_sensitive(False)

    def evt_type_sens(self, *args): #may do with descriptors
        if self.evt_type_filter.get_active():
            self.evt_type_frame.children()[0].set_sensitive(True)
        else:
            self.evt_type_frame.children()[0].set_sensitive(False)

    def date_sens(self, *args): #may do with descriptors
        if self.date_filter.get_active():
            self.date_frame.children()[0].set_sensitive(True)
        else:
            self.date_frame.children()[0].set_sensitive(False)

    def content_sens(self, *args): #may do with descriptors
        if self.content_filter.get_active():
            self.content_frame.children()[0].set_sensitive(True)
        else:
            self.content_frame.children()[0].set_sensitive(False)

    def quantity_sens(self, *args): #may do with descriptors
        if self.quantity_filter.get_active():
            self.quantity_frame.children()[0].set_sensitive(True)
        else:
            self.quantity_frame.children()[0].set_sensitive(False)

    #def stop_all(self, *args):
    #    self.allstop.set()

    def build_interface(self):
        self.filter_frame.add(self.filter_box)
        self.evt_type_frame.set_label_widget(self.evt_type_filter)
        self.evt_type_frame.add(self.event_box)
        for chb in self.evt_checkboxes.itervalues():
            self.event_box.pack_start(chb, False, False, 1)
        self.filter_box.pack_start(self.evt_type_frame, False, False)
        self.filter_box.pack_start(self.date_frame, False, False)
        self.filter_box.pack_start(self.quantity_frame, False, False)
        self.filter_box.pack_start(self.content_frame, False, False)

        #self.date_frame.set_label_widget(self.date_filter)
        #self.date_frame.add(self.event_box)
        self.quantity_frame.set_label_widget(self.quantity_filter)
        self.quantity_frame.add(self.last_box)
        self.last_box.pack_start(self.last_label, False, False)
        self.last_box.pack_start(self.last_spinbutton, False, False,20)

        self.date_frame.set_label_widget(self.date_filter)
        self.date_frame.add(self.date_box)
        self.date_box.pack_start(self.date_last_box, False, False)
        self.date_box.pack_start(self.fromto_table, False, False)
        self.date_last_box.pack_start(self.last_date_radio, False, False)
        self.date_last_box.pack_start(self.last_date_spin, False, False)
        self.date_last_box.pack_start(self.last_date_combo, False, False)

        self.content_frame.set_label_widget(self.content_filter)
        self.content_frame.add(self.content_table)
        self.content_table.attach(self.like_label,0,1,0,1, xoptions=0, yoptions=0)
        self.content_table.attach(self.notlike_label,0,1,1,2, xoptions=0, yoptions=0)
        self.content_table.attach(self.like_entry,1,2,0,1)
        self.content_table.attach(self.notlike_entry,1,2,1,2)


        self.fromto_table.attach(self.from_label, 0, 1, 0, 2, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromyear_entry, 1, 4, 1, 2, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromhours_spin, 1, 2, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromminutes_spin, 2, 3, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.fromseconds_spin, 3, 4, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.to_label, 4, 5, 0, 2, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.toyear_entry, 5, 8, 1, 2, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.tohours_spin, 5, 6, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.tominutes_spin, 6, 7, 0, 1, xoptions=0,
                                    yoptions=0)
        self.fromto_table.attach(self.toseconds_spin, 7, 8, 0, 1, xoptions=0,
                                    yoptions=0)



        self.tree_frame.add(self.eventlogs_window)
        self.logs_frame.add(self.logs_window)
        #self.action_frame.add(self.action_box)
        self.button_box.pack_start(self.show_button)
        self.control_box.pack_start(self.tree_frame, True, True)
        self.control_box.pack_start(self.filter_frame, False, False)
        #self.control_box.pack_start(self.event_frame, False, False)
        #self.control_box.pack_start(self.action_frame, False, False)
        self.control_box.pack_start(self.button_box, False, False, 5)
        #self.control_box.pack_start(self.progress, False, False)
        #self.progress_table.attach(self.progress,0,1,0,1)
        #self.progress_table.attach(self.stop_all_btn,1,2,0,1,xoptions=0,yoptions=0)
        #self.progress_table.attach(self.pulse_progress,0,1,1,2)
        #self.progress_table.attach(self.stop_current_btn,1,2,1,2,xoptions=0,yoptions=0)
        self.control_box.pack_start(self.progress, False, False)
        #self.control_box.pack_start(self.progress_table, False, False)
        self.main_box.pack_start(self.control_box, False, False)
        self.main_box.pack_start(self.logs_frame, True, True)
        self.root.add(self.main_box)

    def parse_like_entry(self):
        strng = self.like_entry.get_text()
        
        def parse(token):
            if token in ["AND", "OR", "NOT"]:
                return t.lower()
            elif token in [")","("]:
                return token
            elif not token:
                return token
            else:
                return "'"+t.strip()+"'"+" in l['msg']"
        
        if_expr = ' '.join([parse(t) for t in re.split("(AND|OR|NOT|\)|\()",
            strng)])
        return if_expr

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        gtk.main_quit()
        return

    def get_dates(self):
        '''Define start_date and end_date'''
        if self.last_date_radio.get_active():
            end_date = datetime.datetime.now()
            dateunit = [1.*24*60*60,1.*24*60,1.*24,1.]
            active = self.last_date_combo.get_active()
            delta = self.last_date_spin.get_value()/dateunit[active]
            start_date = end_date-datetime.timedelta(delta)
        elif self.from_label.get_active():
            st_date = datetime.datetime.strptime(self.fromyear_entry.get_text(),
                                                    '%d.%m.%Y')
            start_date = datetime.datetime(
                st_date.year, st_date.month, st_date.day,
                self.fromhours_spin.get_value_as_int(),
                self.fromminutes_spin.get_value_as_int(),
                self.fromseconds_spin.get_value_as_int()
            )
            if self.to_label.get_active():
                e_date = datetime.datetime.strptime(self.toyear_entry.get_text(),
                                                    '%d.%m.%Y')
                end_date = datetime.datetime(
                    e_date.year, e_date.month, e_date.day,
                    self.tohours_spin.get_value_as_int(),
                    self.tominutes_spin.get_value_as_int(),
                    self.toseconds_spin.get_value_as_int()
                )
            else:
                end_date = datetime.datetime.now()
        return (start_date, end_date)

    def get_cont(self):
        return (self.parse_like_entry(),self.notlike_entry.get_text())

    def get_quant(self):
        return self.last_spinbutton.get_value()

    def show_logs(self, params):
        self.logs_model.clear()
        self.progress.set_fraction(0.0)
        self.progress.set_text("Working...")
        evlogs = self.get_active_servers()
        evl_count = len(evlogs)
        frac = 1.0/(evl_count)
        fltr = {}
        fltr['types'] = self.evt_type_filter.get_active() and self.get_event_types() or []
        fltr['date'] = self.date_filter.get_active() and self.get_dates() or ()
        fltr['content'] = self.content_filter.get_active() and self.get_cont() or ("","")
        fltr['last'] = self.quantity_filter.get_active() and self.get_quant() or 0
        #gtk.gdk.threads_init()
        self.sens_list=[self.evt_type_frame,self.date_frame,
            self.content_frame,self.quantity_frame,self.show_button]
        for sl in self.sens_list:
                sl.set_sensitive(False)
        for comp, log in evlogs:
        #    gtk.gdk.threads_enter()
            self.worker = LogWorker(comp, log, fltr, self.logs_model,
                                        self.progress, frac, self.sens_list)
            self.worker.start()

       # gtk.gdk.threads_leave()


		#self.progress.set_fraction(frac/evl_count)
        #        frac+=1
        #self.progress.set_text("Complete")
        #self.progress.set_fraction(1.0)

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

#    def run(self):
#        """ run is called to set off the GTK mainloop """
#        gtk.main()
#        return
#
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
        scr = gtk.ScrolledWindow()
        scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        popup_frame = gtk.Frame("Log")
        log_text = gtk.TextView()
        log_text.set_editable(False)
        log_text.set_wrap_mode(gtk.WRAP_WORD)
        msg = model.get_value(iter, 5).decode("string-escape")
        msg = re.sub(r"u[\"'](.+?)[\"']", lambda m: m.group(1), msg, flags=re.DOTALL)
        msg = re.sub(r"\\u\w{4}", lambda m: m.group(0).decode("unicode-escape"), msg)
        log_text.get_buffer().set_text("%s\n%s\n%s\n%s\n%s\n\n\n%s" % (
            model.get_value(iter, 0),
            model.get_value(iter, 1),
            model.get_value(iter, 2),
            model.get_value(iter, 3),
            model.get_value(iter, 4),
            msg))
        popup_frame.add(scr)
        scr.add(log_text)
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
    gtk.gdk.threads_init()
    ServersStore = ServersModel()
    LogsStore = LogsModel()
    ServersDisplay = DisplayServersModel()
    LogsDisplay = DisplayLogsModel()
    myGUI = GUI_Controller()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    #myGUI.run()
