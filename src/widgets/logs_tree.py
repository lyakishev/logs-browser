import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango
import os
from parse import parse_filename
from itertools import groupby
import datetime
import re
import ConfigParser
from config_editor import ConfigEditor
import sys



class ServersModel(object):
    def __init__(self):
        self.conf_dir = os.sep.join(os.path.dirname(__file__)\
                                      .split(os.sep)[:-1] +\
                                      ["config"])
        self.treestore = gtk.TreeStore(gobject.TYPE_STRING,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_BOOLEAN,
                                       gobject.TYPE_STRING)

        self.model_filter = self.treestore.filter_new()

    def fill_model(self):
        pass

    def get_model(self):
        """ Returns the model """
        if self.model_filter:
            return self.model_filter
        else:
            return None

    def get_active_servers(self):
        log_for_process = []

        def treewalk(iters):
            if self.treestore.get_value(iters, 3) == 'f' \
                and self.treestore.get_value(iters, 2):
                cur_log = [self.treestore.get_value(iters, 0)]
                parent = self.treestore.iter_parent(iters)
                while parent:
                    if self.treestore.get_value(parent, 3) == 'n':
                        break
                    cur_log.append(self.treestore.get_value(parent, 0))
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

    def get_active_check_paths(self):
        pathslist = []

        def treewalk(iters):
            if self.treestore.get_value(iters, 3) == 'f' \
                and self.treestore.get_value(iters, 2):
                pathslist.append(self.treestore.get_string_from_iter(iters))
                return
            it = self.treestore.iter_children(iters)
            while it:
                treewalk(it)
                it = self.treestore.iter_next(it)

        root = self.treestore.iter_children(None)
        while root:
            treewalk(root)
            root = self.treestore.iter_next(root)
        return pathslist

    def set_active_from_paths(self, pathslist):
        def treewalk(iters):
            self.treestore.set_value(iters, 2, 0)
            if self.treestore.get_value(iters, 3) == 'f':
                path = self.treestore.get_string_from_iter(iters)
                if path in pathslist:
                    self.treestore.set_value(iters, 2, 1)
                return
            it = self.treestore.iter_children(iters)
            while it:
                treewalk(it)
                it = self.treestore.iter_next(it)
        root = self.treestore.iter_children(None)
        while root:
            treewalk(root)
            root = self.treestore.iter_next(root)


class EventServersModel(ServersModel):
    """ The model class holds the information we want to display """
    def __init__(self):
        super(EventServersModel, self).__init__()
        self.file = os.path.join(self.conf_dir, "evlogs.cfg")
        try:
            f = open(self.file)
        except IOError:
            self.file = os.path.join("config", "evlogs.cfg")
        else:
            f.close()
        self.read_from_file(True)

    def read_from_file(self, fict):
        self.treestore.clear()
        config = ConfigParser.RawConfigParser()
        config.read(self.file)
        for section in config.sections():
            parent = self.treestore.append(None, (section,
                                                  gtk.STOCK_NETWORK,
                                                  None, 'n'))
            for item in config.items(section):
                child = self.treestore.append(parent, (item[0],
                                                       gtk.STOCK_DIRECTORY,
                                                       None, 'd'))
                for value in item[1].split(","):
                    self.treestore.append(child, (value.strip(),
                                                  gtk.STOCK_FILE,
                                                  None, 'f'))


class FileServersModel(ServersModel):
    def __init__(self):
        super(FileServersModel, self).__init__()
        self.file = os.path.join(self.conf_dir, "logs.cfg")
        try:
            self.read_from_file(True)
        except IOError:
            self.file = os.path.join("config", "logs.cfg")
            self.read_from_file(True)

    def read_from_file(self, re_all):
        if re_all:
            self.parents = {}
            self.files = []
            self.config = {}
            self.treestore.clear()
        root_re = re.compile("^\[.+?\]$")
        with open(self.file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    #print line
                    if not line.startswith("#"):
                        if line == "[]":
                            root = None
                            c_root = line
                            if not self.config.get(c_root):
                                self.config[c_root] = set()
                        elif root_re.search(line):
                            root = self.add_root(line[1:-1])
                            c_root = line
                            if not self.config.get(c_root):
                                self.config[c_root] = set()
                        else:
                            if line not in self.config[c_root]:
                                self.add_parents(line, root)
                                self.add_logdir(line, root)
                                self.config[c_root].add(line)
        #self.remove_empty_dirs()

    def add_root(self, name):
        if name:
            for root in self.treestore:
                if name == root[0]:
                    return root.iter
            return self.treestore.append(None, [name,
                                                gtk.STOCK_NETWORK,
                                                None, 'n'])

    def remove_empty_dirs(self):
        def walker(it):
            files = 0
            dirs = 0
            chit = self.treestore.iter_children(it)
            while chit:
                n_chit = self.treestore.iter_next(chit)
                if self.treestore.get_value(chit, 3) == 'd':
                    dirs += 1
                    walker(chit)
                else:
                    files += 1
                chit = n_chit
            if not files and not dirs:
                par = self.treestore.iter_parent(it)
                if self.treestore.get_value(it, 3) != 'n':
                    self.treestore.remove(it)
                    if par:
                        walker(par)

        it = self.treestore.iter_children(None)
        while it:
            walker(it)
            it = self.treestore.iter_next(it)

    def add_parents(self, path, parent):
        try:
            parent_str = self.treestore.get_value(parent, 0)
        except TypeError:
            parent_str = ""
        tsappend = self.treestore.append
        parts = path.split(os.sep)
        if path.startswith(r"\\"):
            parts = parts[2:]
            parts[0] = r"\\" + parts[0]
        elif path.startswith("/"):
            parts = parts[1:]
            parts[0] = "/" + parts[0]
        for n, p in enumerate(parts):
            if p:
                new_node_path = "|".join([parent_str,
                                          os.sep.join(parts[:(n + 1)])])
                if not self.parents.get(new_node_path):
                    prev_parent = self.parents.get("|".join([parent_str,
                                                 os.sep.join(parts[:n])]),
                                                 parent)
                    self.parents[new_node_path] = tsappend(prev_parent,
                                        [p, gtk.STOCK_DIRECTORY, None, 'd'])

    def add_logdir(self, path, parent):
        try:
            parent_str = self.treestore.get_value(parent, 0)
        except TypeError:
            parent_str = ""
        true_parent = self.parents.get("|".join([parent_str, path]), parent)
        self.walk(path, true_parent, parent_str)

    def walk(self, path, parent, pstr):
        fls = []
        try:
            for f in os.listdir(path):
                fullf = os.path.join(path, f)
                fext = os.path.splitext(f)[1]
                node_name = "|".join([pstr, fullf])
                true_parent = self.parents.get("|".join([pstr, fullf]), parent)
                if fext:
                    if node_name not in self.files:
                        self.files.append(node_name)
                        name, ext = parse_filename(f)
                        if ext in ('txt', 'log'):
                            if not name:
                                name = "undefined"
                            if name not in fls:
                                self.treestore.append(true_parent,
                                        [name, gtk.STOCK_FILE, None, 'f'])
                                fls.append(name)
                else:
                    node = self.parents.get(node_name)
                    if not node:
                        node = self.treestore.append(true_parent, \
                                [f, gtk.STOCK_DIRECTORY, None, 'd'])
                        self.parents[node_name] = node
                    self.walk(fullf, node, pstr)
        except:
            pass

    def prepare_files_for_parse(self):
        srvs = self.get_active_servers()
        new_srvs = []
        for i in srvs:
            new_srvs.append([os.sep.join(reversed(i[1:])), i[0]])

        folders = {}

        for k, g in groupby(new_srvs, lambda x: x[0]):
            folders[k] = [fl[1] for fl in list(g)]

        return folders


class DisplayServersModel:
    """ Displays the Info_Model model in a view """
    def __init__(self, model, srvrs):
        """ Form a view for the Tree Model """
        self.view = gtk.TreeView(model)
        self.srvrs = srvrs
        # setup the text cell renderer and allows these
        # cells to be edited.
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('editable', False)
        self.stockrenderer = gtk.CellRendererPixbuf()
        #self.renderer.connect( 'edited', self.col0_edited_cb, model )

        # The toggle cellrenderer is setup and we allow it to be
        # changed (toggled) by the user.
        self.renderer1 = gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect('toggled', self.col1_toggled_cb, model)
        self.renderer2 = gtk.CellRendererText()
        # Connect column0 of the display with column 0 in our list model
        # The renderer will then display whatever is in column 0 of
        # our model .
        self.column0 = gtk.TreeViewColumn("Path")
        self.column0.pack_start(self.renderer1, False)
        self.column0.pack_start(self.stockrenderer, False)
        self.column0.pack_start(self.renderer, True)
        self.column0.add_attribute(self.renderer1, 'active', 2)
        self.column0.set_attributes(self.stockrenderer, stock_id=1)
        self.column0.set_attributes(self.renderer, text=0)
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        self.column2 = gtk.TreeViewColumn("Type", self.renderer2)
        self.column2.set_visible(False)
        self.view.append_column(self.column0)
        self.view.append_column(self.column2)
        self.view.connect("button-press-event", self.show_menu)
        self.popup = gtk.Menu()
        self.reload = gtk.MenuItem("Reload All")
        self.load = gtk.MenuItem("Load New")
        self.reload.connect("activate", self.reload_all)
        self.load.connect("activate", self.load_new)
        self.edit = gtk.MenuItem("Edit config")
        self.edit.connect("activate", self.show_config_editor)
        self.popup.append(self.reload)
        self.popup.append(self.load)
        self.popup.append(self.edit)
        self.popup.show_all()

    def show_config_editor(self, *args):
        ConfigEditor(self.srvrs.file)

    def reload_all(self, *args):
        self.srvrs.read_from_file(True)

    def load_new(self, *args):
        self.srvrs.read_from_file(False)

    def show_menu(self, treeview, event):
        if event.button == 3:
            time = event.time
            self.popup.popup(None, None, None, event.button, time)

    def col1_toggled_cb(self, cell, path, model):
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
    def __init__(self):
        super(ServersTree, self).__init__()
        self.view = DisplayServersModel(self.model.get_model(), self.model)
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.logs_window.add(self.view.view)
        self.hide_log = gtk.Entry()
        self.hide_log.set_text("Search...")
        self.hide_log.modify_text(gtk.STATE_NORMAL,
                            gtk.gdk.color_parse("#929292"))
        self.hide_log.modify_font(pango.FontDescription("italic"))
        entry_box = gtk.HBox()
        clear_btn = gtk.Button()
        clear = gtk.Image()
        clear.set_from_stock(gtk.STOCK_CLEAR,gtk.ICON_SIZE_MENU)
        clear_btn.add(clear)
        clear_btn.connect("clicked", self.clear_entry)
        entry_box.pack_start(self.hide_log, True,True)
        entry_box.pack_start(clear_btn,False,False)

        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(entry_box, False, False)
        self.hide_log.connect("changed", self.on_advanced_entry_changed)
        self.hide_log.connect("focus-in-event", self.on_hide_log_focus_in)
        self.hide_log.connect("focus-out-event", self.on_hide_log_focus_out)
        self.ft = False
        self.model.get_model().set_visible_func(self.visible_func)
        self.filter_text = ""
        self.show_all()

    def clear_entry(self, *args):
        self.on_hide_log_focus_in()
        self.filter_text = ""
        self.on_hide_log_focus_out()
    
    def set_text(self, entry):
        self.on_hide_log_focus_in()
        self.hide_log.set_text(entry[0])
        self.filter_text = entry[0]
        self.ft = entry[1]
        self.on_hide_log_focus_out()

    def on_hide_log_focus_in(self, *args):
        self.ft = True
        self.hide_log.set_text(self.filter_text)
        self.hide_log.modify_text(gtk.STATE_NORMAL,
                            gtk.gdk.color_parse("black"))
        self.hide_log.modify_font(pango.FontDescription("normal"))

    def on_hide_log_focus_out(self, *args):
        if not self.filter_text:
            self.ft = False
            self.hide_log.set_text("Search...")
            self.filter_text = ""
            self.hide_log.modify_text(gtk.STATE_NORMAL,
                                gtk.gdk.color_parse("#929292"))
            self.hide_log.modify_font(pango.FontDescription("italic"))

    def on_advanced_entry_changed(self, widget):
        self.filter_text = widget.get_text()
        self.model.get_model().refilter()
        if not self.filter_text or not self.ft:
            self.view.view.collapse_all()
        else:
            self.ft = True
            self.view.view.expand_all()

    def visible_func(self, model, treeiter):
        if self.ft:
            search_string = self.filter_text.lower()
            for it in tree_model_pre_order(model, treeiter):
                try:
                    if search_string in model[it][0].lower():
                        return True
                except:
                    pass
            return False
        else:
            return True

class EvlogsServersTree(ServersTree):
    def __init__(self):
        self.model = EventServersModel()
        super(EvlogsServersTree, self).__init__()

class FileServersTree(ServersTree):
    def __init__(self):
        self.model = FileServersModel()
        super(FileServersTree, self).__init__()


class LogsTrees(gtk.Notebook):
    def __init__(self):
        super(LogsTrees, self).__init__()
        self.file_servers_tree = FileServersTree()
        file_label = gtk.Label("Filelogs")
        file_label.show()
        self.append_page(self.file_servers_tree, file_label)
        self.evlogs_servers_tree = None
        if sys.platform == 'win32':
            evt_label = gtk.Label("Eventlogs")
            evt_label.show()
            self.evlogs_servers_tree = EvlogsServersTree()
            self.evlogs_servers_tree.show()
            self.append_page(self.evlogs_servers_tree, evt_label)

        self.state_ = {}

    def load_state(self, page):
        ftree = self.file_servers_tree
        etree = self.evlogs_servers_tree
        state = self.state_.get(page)
        if state:
            fpathslist, fentry, epathslist, eentry = state
        else:
            fpathslist, fentry, epathslist, eentry = ([],("",False),
                                                      [],("",False))
        ftree.model.set_active_from_paths(fpathslist)
        ftree.set_text(fentry)
        if etree:
            etree.model.set_active_from_paths(epathslist)
            etree.set_text(eentry)
        

    def save_state(self, page):
        ftree = self.file_servers_tree
        fpathslist = ftree.model.get_active_check_paths()
        fentry = ftree.filter_text, ftree.ft
        etree = self.evlogs_servers_tree
        if etree:
            epathslist = etree.model.get_active_check_paths()
            eentry = etree.filter_text, ftree.ft
        else:
            epathslist = []
            eentry = ()
        self.state_[page] = (fpathslist, fentry, epathslist, eentry)

    def free_state(self, page):
        del self.state_[page]


        
