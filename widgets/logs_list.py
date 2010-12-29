#! -*- coding: utf8 -*-
import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from widgets.log_window import LogWindow
import re
from data_mining import *
import rpdb2

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


    def highlight(self, pattern):
        for row in self.list_store:
            if pattern:
                if eval(self.parse_like(pattern, "row[5].lower()")):
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
        self.hl_log = gtk.Entry()
        self.hl_log.set_width_chars(20)

        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(self.hl_log, False, False)
        self.hl_log.connect("changed", self.highlight)

        self.test_button = gtk.Button("Clusters")
        self.test_button.connect("clicked", self.test_clusters)
        self.box.pack_start(self.test_button, False, False)

    def highlight(self, params):
        self.logs_store.highlight(params.get_text())
        self.logs_view.repaint()

    def test_clusters(self, args):
        apcount = {}
        wordcounts = {}
        for row in self.logs_store.get_model():
            wc = getwordcounts(row)
            wordcounts[row] = wc
            for word, count in wc.iteritems():
                apcount.setdefault(word,0)
                if count>1:
                    apcount[word]+=1
        wordlist=[]
        #rpdb2.start_embedded_debugger('123')
        for w,bc in apcount.iteritems():
            frac=float(bc)/len([r for r in self.logs_store.get_model()])
            if 0.1 < frac < 0.5:
                wordlist.append(w)

        all_words = []
        rows=[]
        for row, wd in wordcounts.iteritems():
            rows.append(row)
            all_words.append([wd.get(word,0) for word in wordlist])

        clust = hcluster(all_words)
        printclust(clust)



