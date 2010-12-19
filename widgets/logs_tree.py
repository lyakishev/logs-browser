import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import os
from parse import filename
from pyparsing import ParseException
import threading
from itertools import groupby
import glob

class ServersModel(object):
    def __init__(self):
        self.treestore = gtk.TreeStore( gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_BOOLEAN,
                                         gobject.TYPE_STRING )

        FillThread=threading.Thread(target=self.fill_model)
        FillThread.start()
        self.model_filter = self.treestore.filter_new()

    def fill_model(self):
        pass

    def get_model(self):
        """ Returns the model """
        if self.model_filter:
            return self.model_filter
        else:
            return None

    #def visible_func(self, model, treeiter):
        

    def get_active_servers(self):
        log_for_process = []
        def treewalk(iters):
            if self.treestore.get_value(iters, 3) == 'f' \
                and self.treestore.get_value(iters, 2):
                cur_log = [self.treestore.get_value(iters, 0)]
                parent = self.treestore.iter_parent(iters)
                while parent:
                    cur_log.append(self.treestore.get_value(parent,0))
                    parent = self.treestore.iter_parent(parent)
                log_for_process.append(cur_log)
            it = self.treestore.iter_children(iters)
            while it:
                treewalk(it)
                it = self.treestore.iter_next(it)
        root = self.treestore.iter_children(None)
        while root:
            treewalk(root)
            root = self.treestore.iter_next(root)

        return log_for_process

class EventServersModel(ServersModel):
    """ The model class holds the information we want to display """
    def __init__(self, logs):
        self.logs=logs
        super(EventServersModel, self).__init__()
        """ Sets up and populates our gtk.TreeStore """
        """!!!Rewrite to recursive!!!!"""
        # places the global people data into the list
        # we form a simple tree.

    def fill_model(self):
        for item in sorted(self.logs.keys()):
            parent = self.treestore.append( None, (item, gtk.STOCK_DIRECTORY, None, 'd') )
            for subitem in sorted(self.logs[item].keys()):
                child = self.treestore.append( parent, (subitem, gtk.STOCK_DIRECTORY, None, 'd') )
                for subsubitem in self.logs[item][subitem]:
                    self.treestore.append( child, (subsubitem, gtk.STOCK_FILE, None, 'f') )

class FileServersModel(ServersModel):
    def __init__(self):
        super(FileServersModel, self).__init__()

    def fill_model(self):
        fls={}
        for stand in ("nag-tc", "msk-func", "kog-app"):
            stiter = self.treestore.append(None, [stand, None, 'd'])
            for i in range(1,13):
                parents={}
                server_name = '%s-%0.2d' % (stand, i)
                server = self.treestore.append(stiter, [server_name, gtk.STOCK_DIRECTORY, None, 'd'])
                for root, dirs, files in os.walk(r'\\%s\forislog' % server_name):
                    if not dirs and not (glob.glob(root+r"\*.txt") or glob.glob(root+'\*.log')):
                        continue
                    else:
                        for subdir in dirs:
                            gtk.gdk.threads_enter()
                            parents[os.path.join(root, subdir)] = self.treestore.append(parents.get(root, server), \
                                [subdir, gtk.STOCK_DIRECTORY,None, 'd'])
                            gtk.gdk.threads_leave()
                        for item in files:
                            try:
                                pf = filename.parseString(item)
                                name = pf['logname']+pf['logname2']
                                if not fls.get(name, None):
                                    gtk.gdk.threads_enter()
                                    self.treestore.append(parents.get(root, server), [name, gtk.STOCK_FILE, None, 'f'])
                                    gtk.gdk.threads_leave()
                                    fls[name]=item
                            except:
                                print "---------------------"
                                print item
                                print "---------------------"

    def prepare_files_for_parse(self):
        srvs = self.get_active_servers()
        new_srvs = []
        for i in srvs:
             new_srvs.append(["\\\\"+i[-2]+"\\forislog\\"+"\\".join(reversed(i[1:-2])),
                             i[0]])
        folders = {}

        for k,g in groupby(new_srvs, lambda x: x[0]):
            folders[k]=[fl[1] for fl in list(g)]

        return folders


        #print folders





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



class DisplayServersModel:
    """ Displays the Info_Model model in a view """
    def __init__( self, model ):
        """ Form a view for the Tree Model """
        self.view = gtk.TreeView( model )
        # setup the text cell renderer and allows these
        # cells to be edited.
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property( 'editable', False )
        self.stockrenderer = gtk.CellRendererPixbuf()
        #self.renderer.connect( 'edited', self.col0_edited_cb, model )

        # The toggle cellrenderer is setup and we allow it to be
        # changed (toggled) by the user.
        self.renderer1 = gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect( 'toggled', self.col1_toggled_cb, model )
        self.renderer2 = gtk.CellRendererText()
        # Connect column0 of the display with column 0 in our list model
        # The renderer will then display whatever is in column 0 of
        # our model .
        self.column0 = gtk.TreeViewColumn("Path")
        self.column0.pack_start(self.stockrenderer, False)
        self.column0.pack_start(self.renderer, True)
        self.column0.set_attributes(self.stockrenderer, stock_id=1)
        self.column0.set_attributes(self.renderer, text=0)
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        self.column1 = gtk.TreeViewColumn("Show", self.renderer1 )
        self.column1.add_attribute( self.renderer1, "active", 2)
        self.column2 = gtk.TreeViewColumn("Type", self.renderer2 )
        self.column2.set_visible(False)
        self.view.append_column( self.column0 )
        self.view.append_column( self.column1 )
        self.view.append_column( self.column2 )
        #return self.view

    def col1_toggled_cb( self, cell, path, model ):
        """
        Sets the toggled state on the toggle button to true or false.
        """
        true_model = model.get_model()
        true_path = model.convert_path_to_child_path(path)
        state = true_model[true_path][2] = not true_model[true_path][2]
        def walk(child):
            for ch in child.iterchildren():
                ch[2] = state
                walk(ch)
        walk(true_model[true_path])
        #model.refilter()
        return

def tree_model_iter_children(model, treeiter):
    it = model.iter_children(treeiter)
    while it:
        yield it
        it = model.iter_next(it)

def tree_model_pre_order(model, treeiter):
    yield treeiter
    for childiter in tree_model_iter_children(model, treeiter):
        for it in tree_model_pre_order(model, childiter):
            yield it

class ServersTree(gtk.Frame):
    def __init__(self, logs):
        super(ServersTree, self).__init__()
        self.model = EventServersModel(logs)
        self.view = DisplayServersModel(self.model.get_model())
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.logs_window.add_with_viewport(self.view.view)
        self.hide_log = gtk.Entry()
        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(self.hide_log, False, False)
        self.hide_log.connect("changed", self.on_advanced_entry_changed)
        self.model.get_model().set_visible_func(self.visible_func)


    def on_advanced_entry_changed(self, widget):
        self.model.get_model().refilter()
        if not widget.get_text():
            self.view.view.collapse_all()
        else:
            self.view.view.expand_all()

    def visible_func(self, model, treeiter):
        search_string = self.hide_log.get_text()
        for it in tree_model_pre_order(model, treeiter):
            try:
                if search_string in model[it][0]:
                    return True
            except:
                pass
        return False

        
