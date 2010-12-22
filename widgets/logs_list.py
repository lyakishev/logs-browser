import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from widgets.log_window import LogWindow
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

    def highlight(self, pattern):
        for row in self.list_store:
            if pattern:
                if pattern in row[5]:
                    row[6] = "#FF0000"
                else:
                    row[6] = "#FFFFFF"
            else:
                row[6]="#FFFFFF"

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



class LogListWindow(gtk.Frame):
    def __init__(self):
        super(LogListWindow, self).__init__()
        self.logs_store = LogsModel()
        self.logs_store.get_model().set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        self.logs_view= DisplayLogsModel(self.logs_store.get_model())
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.logs_window.add_with_viewport(self.logs_view.view)
        self.hl_log = gtk.Entry()
        self.hl_log.set_width_chars(20)

        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(self.hl_log, False, False)
        self.hl_log.connect("changed", self.highlight)

    def highlight(self, params):
        self.logs_store.highlight(params.get_text())
        self.logs_view.repaint()





