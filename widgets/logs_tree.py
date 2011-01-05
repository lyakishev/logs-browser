import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import os
from parse import parse_filename
import threading
from itertools import groupby
import glob
import datetime

class ServersModel(object):
    def __init__(self):
        self.treestore = gtk.TreeStore( gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_BOOLEAN,
                                         gobject.TYPE_STRING )

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
        self.fill_model()

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
        stands = []

        #stands.append(["nag-tc", ['%s-%0.2d' % ("nag-tc", i) for i in range(1,13)]])
        #stands.append(["msk-func", ['%s-%0.2d' % ("msk-func", i) for i in range(1,13)]])
        #stands.append(["kog-app", ['%s-%0.2d' % ("kog-app", i) for i in range(1,13)]])
        #stands.append(["umc-test-2", ['%s-v%0.4d' % ("msk-app", i) for i in \
        #    range(190, 224) if i not in range(197,203) and i not in range(204,221)]])

        #for stand, servers in stands:
        #    thread = threading.Thread(target=self.fill_model, args=(stand, servers,))
        #    thread.start()

        #threading.Thread(target=self.add_custom_logdir,args=(r"\\msk-app-v0194\c$\FORIS\Messaging Gateway\log",)).start()
        #threading.Thread(target=self.add_custom_logdir,args=(r"\\msk-app-v0194\c$\FORIS\Messaging Gateway\CRMFilter\logs",)).start()
        self.custom_dir = self.treestore.append(None, ["Custom Folders",\
            gtk.STOCK_DIRECTORY, None, 'd'])
        threading.Thread(target=self.add_custom_logdir,args=(r"\\VBOXSVR\sharew7\log",)).start()

    def fill_model(self, stand, servers):
        dt = datetime.datetime.now()
        tsappend = self.treestore.append
        walk = os.walk
        opjoin = os.path.join
        gtk.gdk.threads_enter()
        stiter = tsappend(None, [stand, gtk.STOCK_DIRECTORY, None, 'd'])
        gtk.gdk.threads_leave()
        for server_name in servers:
            parents={}
            gtk.gdk.threads_enter()
            server = tsappend(stiter, ["\\".join([server_name, "forislog"]), gtk.STOCK_DIRECTORY, None, 'd'])
            gtk.gdk.threads_leave()
            for root, dirs, files in walk(r'\\%s\forislog' % server_name):
                true_parent = parents.get(root, server)
                for subdir in dirs:
                    gtk.gdk.threads_enter()
                    parents[opjoin(root, subdir)] = tsappend(true_parent, \
                        [subdir, gtk.STOCK_DIRECTORY,None, 'd'])
                    gtk.gdk.threads_leave()
                fls=[]#{}
                for item in files:
                    name, ext = parse_filename(item)
                    if name and ext in ('txt', 'log'):
                        #if not fls.get(name, None):
                        if name not in fls:
                            gtk.gdk.threads_enter()
                            tsappend(true_parent, [name, gtk.STOCK_FILE, None, 'f'])
                            gtk.gdk.threads_leave()
                            fls.append(name)
        print stand, '  ', datetime.datetime.now() - dt

    def add_custom_logdir(self, path):
        tm = datetime.datetime.now()
        tsappend = self.treestore.append
        opjoin = os.path.join
        gtk.gdk.threads_enter()
        new_parent = self.custom_dir
        gtk.gdk.threads_leave()
        for subdir in [p for p in path.split(os.sep) if p]:
            gtk.gdk.threads_enter()
            new_parent = tsappend(new_parent, [subdir, gtk.STOCK_DIRECTORY, None, 'd'])
            gtk.gdk.threads_leave()

        parents = {}
        for root, dirs, files in os.walk(path):
            true_parent = parents.get(root, new_parent)
            for subdir in dirs:
                gtk.gdk.threads_enter()
                parents[opjoin(root, subdir)] = tsappend(true_parent,\
                    [subdir, gtk.STOCK_DIRECTORY,None, 'd'])
                gtk.gdk.threads_leave()
            fls=[]#{}
            flsapp=fls.append
            for item in files:
                name, ext = parse_filename(item)
                if name and ext in ('txt', 'log'):
                    #if not fls.get(name, None):
                    if name not in fls:
                        gtk.gdk.threads_enter()
                        tsappend(true_parent, [name, gtk.STOCK_FILE, None, 'f'])
                        gtk.gdk.threads_leave()
                        flsapp(name)
        print datetime.datetime.now()-tm





    def prepare_files_for_parse(self):
        srvs = self.get_active_servers()
        new_srvs = []
        for i in srvs:
            new_srvs.append(["\\\\"+"\\".join(reversed(i[1:-1])),
                             i[0]])
        folders = {}

        for k,g in groupby(new_srvs, lambda x: x[0]):
            folders[k]=[fl[1] for fl in list(g)]

        return folders

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
    def __init__( self, model, srvrs ):
        """ Form a view for the Tree Model """
        self.view = gtk.TreeView( model )
        self.srvrs = srvrs
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
        self.column0.pack_start(self.renderer1, False)
        self.column0.pack_start(self.stockrenderer, False)
        self.column0.pack_start(self.renderer, True)
        self.column0.add_attribute(self.renderer1, 'active', 2 )
        self.column0.set_attributes(self.stockrenderer, stock_id=1)
        self.column0.set_attributes(self.renderer, text=0)
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        self.column2 = gtk.TreeViewColumn("Type", self.renderer2 )
        self.column2.set_visible(False)
        self.view.append_column( self.column0 )
        self.view.append_column( self.column2 )
        self.view.connect("button-press-event", self.show_menu)
        self.popup = gtk.Menu()
        self.add = gtk.MenuItem("Add path")
        self.add.connect("activate", self.add_path)
        self.popup.append(self.add)
        self.popup.show_all()

    def add_path(self, *args):
        fchooser = gtk.FileChooserDialog(None, None,
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
        response = fchooser.run()
        if response == gtk.RESPONSE_OK:
            self.srvrs.add_custom_logdir(fchooser.get_filename())
        fchooser.destroy()

    def show_menu(self, treeview, event):
        if event.button == 3:
            #x = int(event.x)
            #y = int(event.y)
            time = event.time
            #pthinfo = treeview.get_path_at_pos(x, y)
            #if pthinfo is not None:
            #    path, col, cellx, celly = pthinfo
            #    treeview.grab_focus()
            #    treeview.set_cursor( path, col, 0)
            #    self.popup.popup( None, None, None, event.button, time)
            #else:
            #    self.popup.popup( None, None, None, event.button, time)
            self.popup.popup( None, None, None, event.button, time)
            return True


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
        self.view = DisplayServersModel(self.model.get_model(), self.model)
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

class FileServersTree(gtk.Frame):
    def __init__(self):
        super(FileServersTree, self).__init__()
        self.model = FileServersModel()
        self.view = DisplayServersModel(self.model.get_model(), self.model)
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
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
