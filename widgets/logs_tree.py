class EventServersModel:
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
        self.column0 = gtk.TreeViewColumn("Path", self.renderer, text=0)
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        self.column1 = gtk.TreeViewColumn("Show", self.renderer1 )
        self.column1.add_attribute( self.renderer1, "active", 1)
        self.view.append_column( self.column0 )
        self.view.append_column( self.column1 )
        return self.view

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

class LogsTree(gtk.Frame):
    def __init__(self):
        super(EventLogsTree, self).__init__(label="Logs")

