import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from widgets.log_window import LogWindow
from widgets.color_parser import ColorParser
import re

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

    def parse_like(self, text, what):
        def parse(token):
            if token in ["AND", "OR", "NOT"]:
                return t.lower()
            elif token in [")","("]:
                return token
            elif not token:
                return token
            else:
                return "'"+t.strip()+"'"+" in %s" % what
        if_expr = ' '.join([parse(t).lower() for t in re.split("(AND|OR|NOT|\)|\()",\
            text)])
        return if_expr


    def highlight(self, pattern, color):
        for row in self.list_store:
            if row[6] == color:
                row[6] = "#FFFFFF"
            if pattern:
                if eval(self.parse_like(pattern, "row[5].lower()")):
                    row[6] = color
                #else:
                #    if row[6] == color:
                #        row[6] = "#FFFFFF"

class DisplayLogsModel:
    """ Displays the Info_Model model in a view """
    def __init__( self, model ):
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
    
    def repaint(self):
        for n, (col, ren) in enumerate(zip(self.columns, self.renderers)):
            col.set_attributes(ren, cell_background=6, text=n)
        
    def show_log( self, path, column, params):
        selection = path.get_selection()
        (model, iter) = selection.get_selected()
        log_w = LogWindow(model, iter, selection)
        return



class LogListWindow(gtk.Frame):
    def __init__(self):
        super(LogListWindow, self).__init__()
        self.logs_store = LogsModel()
        self.logs_store.get_model().set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        self.logs_view= DisplayLogsModel(self.logs_store.get_model())
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.logs_window.add_with_viewport(self.logs_view.view)
        self.filter_logs = ColorParser()
        #self.hl_log_red = gtk.Entry()
        #self.hl_log_red.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#FF0000"))
        #self.hl_log_green = gtk.Entry()
        #self.hl_log_green.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#00FF00"))
        #self.hl_log_blue = gtk.Entry()
        #self.hl_log_blue.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#0000FF"))
        #self.hl_log_blue.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
        #self.hl_log_yellow = gtk.Entry()
        #self.hl_log_yellow.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#FFFF00"))
        #self.color_button = gtk.Button("Highlight")
        #self.color_button.connect("clicked", self.highlight)

        #self.entry_box=gtk.HBox()
        #self.entry_box.pack_start(self.hl_log_red)
        #self.entry_box.pack_start(self.hl_log_green)
        #self.entry_box.pack_start(self.hl_log_blue)
        #self.entry_box.pack_start(self.hl_log_yellow)
        #self.entry_box.pack_start(self.color_button)

        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(self.filter_logs, False, False, 2)
        #self.hl_log_red.connect("changed", self.highlight, "#FF0000")
        #self.hl_log_green.connect("changed", self.highlight, "#00FF00")
        #self.hl_log_blue.connect("changed", self.highlight, "#0000FF")
        #self.hl_log_yellow.connect("changed", self.highlight, "#FFFF00")

    #def highlight(self, *args):
    #    self.logs_store.highlight(self.hl_log_red.get_text(), "#FF0000")
    #    self.logs_store.highlight(self.hl_log_green.get_text(), "#00FF00")
    #    self.logs_store.highlight(self.hl_log_blue.get_text(), "#0000FF")
    #    self.logs_store.highlight(self.hl_log_yellow.get_text(), "#FFFF00")
    #    self.logs_view.repaint()





