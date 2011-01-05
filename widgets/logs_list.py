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

    def highlight(self, col_str):
        if col_str:
            colors = col_str[::2]
            for color, pattern in zip(colors, [c.strip() for c in col_str[1::2]]):
                if pattern:
                    try:
                        exp = re.compile(pattern)
                    except re.error:
                        return
                    else:
                        for row in self.list_store:
                            if row[6] not in colors or row[6] == color:
                                row[6] = "#FFFFFF"
                            if exp.search(row[5]):
                                row[6] = color
                else:
                    for row in self.list_store:
                        if row[6] == color:
                            row[6] = "#FFFFFF"
        else:
            for row in self.list_store:
                row[6] = "#FFFFFF"
            

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
        self.logs_view= DisplayLogsModel(self.logs_store.get_model())
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.logs_window.add_with_viewport(self.logs_view.view)
        self.exp = gtk.Expander("Filter")
        self.filter_logs = ColorParser(self.logs_store, self.logs_view)
        self.exp.add(self.filter_logs)
        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(self.exp, False, False, 2)





