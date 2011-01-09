import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import os
from parse import parse_filename
import threading
from itertools import groupby
import glob
import datetime
from widgets.dialog import Dialog
import re

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
                    if self.treestore.get_value(parent,3) == 'n':
                        break
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
        self.parents = {}
        self.files = []
        self.config = {}
        self.read_from_file("logs.cfg")

    def read_from_file(self, path):
        root_re = re.compile("^\[.+?\]$")
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    if not line.startswith("#"):
                        if line == "[]":
                            root = None
                            c_root = line
                            self.config[c_root] = []
                        elif root_re.search(line):
                            root = self.add_root(line[1:-1])
                            c_root = line
                            self.config[c_root] = []
                        else:
                            self.add_parents(line, root)
                            self.add_logdir(line, root)
                            self.config[c_root].append(line)
                    else:
                        if line == "#[]" or root_re.search(line[1:]):
                            c_root = line
                            self.config[c_root] = []
                        else:
                            self.config[c_root].append(line)
                        
                        
    def write_config(self, path):
        with open(path, "w") as f:
            for k, v in self.config.iteritems():
                f.write(k+"\n")
                for line in v:
                    f.write(line+"\n")
            

    def add_root(self, name):
        if name:
            for root in self.treestore:
                if name == root[0]:
                    return
            return self.treestore.append(None, [name, gtk.STOCK_NETWORK, None, 'n'])

    def remove_empty_dirs(self):
        def walker(row):
            files = 0
            dirs = 0
            for i in row.iterchildren():
                if i[3] == 'd':
                    dirs += 1
                    walker(i)
                else:
                    files += 1
            if not files and not dirs:
                par = row.parent
                if row[3] != 'n':
                    self.treestore.remove(row.iter)
                    if par:
                        walker(par)
        for i in self.treestore:
            walker(i)


    def add_parents(self, path, parent):
        opjoin = os.path.join
        try:
            parent_str = self.treestore.get_value(parent,0)
        except TypeError:
            parent_str = ""
        tsappend = self.treestore.append
        parts = path.split(os.sep)
        if path.startswith(r"\\"):
            parts = [r"\\"+parts[2]]+parts[3:]
        elif path.startswith("/"):
            parts = ["/"+parts[1]]+parts[2:]
        for n, p in enumerate(parts):
            if p:
                new_node_path = "|".join([parent_str, os.sep.join(parts[:n+1])])
                if not self.parents.get(new_node_path, None):
                    prev_parent = self.parents.get("|".join([parent_str, os.sep.join(parts[:n])]), parent)
                    #gtk.gdk.threads_enter()
                    self.parents[new_node_path] = tsappend(prev_parent, [p, gtk.STOCK_DIRECTORY, None, 'd'])
                    #gtk.gdk.threads_leave()

    def add_logdir(self, path, parent):
        walk = os.walk
        opjoin = os.path.join
        try:
            parent_str = self.treestore.get_value(parent, 0)
        except TypeError:
            parent_str = ""
        tsappend = self.treestore.append
        for root, dirs, files in walk(path):
            true_parent = self.parents.get("|".join([parent_str, root]), parent)
            for subdir in dirs:
                #gtk.gdk.threads_enter()
                node = self.parents.get("|".join([parent_str, opjoin(root, subdir)]), None)
                if not node:
                    self.parents["|".join([parent_str, opjoin(root, subdir)])] = tsappend(true_parent, \
                        [subdir, gtk.STOCK_DIRECTORY,None, 'd'])
                #gtk.gdk.threads_leave()
            fls=[]
            for item in files:
                fullf = opjoin(root, item)
                if "|".join([parent_str, fullf]) not in self.files:
                    self.files.append("|".join([parent_str, fullf]))
                    name, ext = parse_filename(item)
                    if ext in ('txt', 'log'):
                        if not name:
                            name = "undefined"
                        if name not in fls:
                            #gtk.gdk.threads_enter()
                            tsappend(true_parent, [name, gtk.STOCK_FILE, None, 'f'])
                            #gtk.gdk.threads_leave()
                            fls.append(name)

    def prepare_files_for_parse(self):
        srvs = self.get_active_servers()
        new_srvs = []
        for i in srvs:
            new_srvs.append([os.sep.join(reversed(i[1:])), i[0]])

        folders = {}

        for k,g in groupby(new_srvs, lambda x: x[0]):
            folders[k]=[fl[1] for fl in list(g)]

        return folders

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
        self.short_popup = gtk.Menu()
        self.sh_add_path = gtk.MenuItem("Add path")
        self.sh_save = gtk.MenuItem("Save")
        self.add_path = gtk.MenuItem("Add path")
        self.add_root = gtk.MenuItem("Add root")
        self.save = gtk.MenuItem("Save")
        self.sh_add_path.connect("activate", self.f_add_path)
        self.add_path.connect("activate", self.f_add_path)
        self.add_root.connect("activate", self.f_add_root)
        self.save.connect("activate", self.save_config)
        self.sh_save.connect("activate", self.save_config)
        self.popup.append(self.add_root)
        self.popup.append(self.add_path)
        self.popup.append(self.save)
        self.short_popup.append(self.sh_add_path)
        self.short_popup.append(self.sh_save)
        self.popup.show_all()
        self.short_popup.show_all()

    def save_config(self, *args):
        self.srvrs.write_config("logs.cfg")

    def f_add_root(self, *args):
        dialog = Dialog()
        dialog.run()
        txt = dialog.get_text()
        dialog.destroy()
        self.srvrs.add_root(txt)

    def f_add_path(self, *args):
        fchooser = gtk.FileChooserDialog(None, None,
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
        response = fchooser.run()
        if response == gtk.RESPONSE_OK:
            path = fchooser.get_filename()
            fchooser.destroy()
            add_parents=threading.Thread(target=self.srvrs.add_parents, args=(path, self.root))
            add_parents.start()
            add_parents.join()
            add_logdir=threading.Thread(target=self.srvrs.add_logdir, args=(path, self.root))
            add_logdir.start()
            add_logdir.join()
            remove_empty_dirs = threading.Thread(target=self.srvrs.remove_empty_dirs)
            remove_empty_dirs.start()
            remove_empty_dirs.join()
            try:
                root = "["+self.srvrs.treestore.get_value(self.root, 0)+"]"
            except TypeError:
                root = "[]"
            self.srvrs.config.setdefault(root, [])
            if path not in self.srvrs.config[root]:
                self.srvrs.config[root].append(path)
        else:
            fchooser.destroy()
        
        
    def show_menu(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)
                iter = self.srvrs.treestore.get_iter(path[0])
                self.ch_iter = self.srvrs.treestore.get_iter(path)
                if self.srvrs.treestore.get_value(iter, 3) == 'n':
                    self.root = iter
                else:
                    self.root = None
                self.short_popup.popup( None, None, None, event.button, time)
            else:
                self.root = None
                self.popup.popup( None, None, None, event.button, time)

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
        self.logs_window.add(self.view.view)
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
        self.logs_window.add(self.view.view)
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
