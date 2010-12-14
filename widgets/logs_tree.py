class ServersModel:
    def __init__(self):
        self.treestore = gtk.TreeStore( gobject.TYPE_STRING,
                                         gobject.TYPE_BOOLEAN )
    def get_model(self):
        """ Returns the model """
        if self.treestore:
            return self.treestore
        else:

    def get_active_servers(self):
        """Make it recursive!!!"""
        logs_for_process = []
        stands = self.treestore.iter_children(None)
        while stands:
            servers = self.treestore.iter_children(stands)
            while servers:
                logs = self.treestore.iter_children(servers)
                while logs:
                    if self.treestore.get_value(logs, 1) == True:
                        logs_for_process.append(
                            [
                                self.treestore.get_value(servers,0),
                                self.treestore.get_value(logs, 0)
                            ]
                        )
                    logs = self.treestore.iter_next(logs)
                servers = self.treestore.iter_next(servers)
            stands = self.treestore.iter_next(stands)
        return logs_for_process


class EventServersModel(ServersModel):
    """ The model class holds the information we want to display """
    def __init__(self, logs):
        super(EventServersModel, self).__init__()
        """ Sets up and populates our gtk.TreeStore """
        """!!!Rewrite to recursive!!!!"""
        # places the global people data into the list
        # we form a simple tree.
        for item in sorted(logs.keys()):
            parent = self.tree_store.append( None, (item, None) )
            for subitem in sorted(logs[item].keys()):
                child = self.tree_store.append( parent, (subitem,None) )
                for subsubitem in logs[item][subitem]:
                    self.tree_store.append( child, (subsubitem,None) )

class FileServersModel(ServersModel):
    def __init__(self, logs):
        super(FileServersModel, self).__init__()
        for i in range(1,13):
            parents={}
            #server_name = '%s-%0.2d' % (stand, i)
            server_name = r'\\nag-tc-%0.2d\forislog' % i
            server = treestore.append(None, [server_name, ""])
            for root, dirs, files in os.walk(r'\\%s\forislog' % server_name):
                for subdir in dirs:
                    parents[os.path.join(root, subdir)] = treestore.append(parents.get(root, server), [subdir,""])
            for item in files:
                try:
                    pf = filename.parseString(item)
                    name = pf['logname']+pf['logname2']
                    print name
                    if not fls.get(name, None):
                        treestore.append(parents.get(root, server), [name, item])
                except ParseException:
                    print "---------------------"
                    print item
                    print "---------------------"



#def build_tree(nodes):
#    # create empty tree to fill
#    tree = {}
#
#    # fill in tree starting with roots (those with no parent)
#    build_tree_recursive(tree, None, nodes)
#
#    return tree
#
#def build_tree_recursive(tree, parent, nodes):
#    # find children
#    children  = [n for n in nodes if n.parent == parent]
#
#    # build a subtree for each child
#    for child in children:
#    	# start new subtree
#    	tree[child.name] = {}
#
#    	# call recursively to build a subtree for current node
#    	build_tree_recursive(tree[child.name], child, nodes)


##os.path.getmtime(fname)))
#left_inter = end_date < file_end_date and end_date>file_start_date
#right_inter = start_date>file_start_date and start_date<file_end_date
#if left_inter:
#    parse
#elif right_inter:
#    parse
#elif
#def datetime_intersect():
#    return (t1start <= t2start and t2start <= t1end) or \
#           (t2start <= t1start and t1start <= t2end)



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
