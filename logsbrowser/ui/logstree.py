import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango
import os
import ConfigParser
from configeditor import ConfigEditor
import sys
from source.worker import dir_walker, join_path, pathes
import cStringIO
import config
import time #DEBUG
from itertools import count


class ServersModel(object):

    def __init__(self):
        self.treestore = gtk.TreeStore(gobject.TYPE_STRING,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_BOOLEAN,
                                       gobject.TYPE_STRING)

        self.model_filter = self.treestore.filter_new()

    def get_model(self):
        """ Returns the model """
        if self.model_filter:
            return self.model_filter
        else:
            return None

    def get_active_servers(self):
        log_for_process = []
        getv = self.treestore.get_value

        def treewalk(iters):
            if getv(iters, 3) == 'f' and getv(iters, 2):
                cur_log = [getv(iters, 0)]
                parent = self.treestore.iter_parent(iters)
                while parent:
                    if getv(parent, 3) == 'n':
                        break
                    cur_log.append(getv(parent, 0))
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
        getv = self.treestore.get_value

        def treewalk(iters):
            if getv(iters, 3) == 'f' and getv(iters, 2):
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

    def add_root(self, name, filled=True):
        return self.treestore.append(None, [name,
                                            (gtk.STOCK_CONNECT if filled
                                            else gtk.STOCK_DISCONNECT),
                                            None, 'n'])

    def add_dir(self, name, parent):
        return self.treestore.append(parent, [name,
                                            gtk.STOCK_DIRECTORY,
                                            None, 'd'])

    def add_file(self, name, parent):
        return self.treestore.append(parent, [name,
                                            gtk.STOCK_FILE,
                                            None, 'f'])

class EventServersModel(ServersModel):
    def __init__(self):
        self.file = config.ELOGS_CFG
        super(EventServersModel, self).__init__()

    def read_config(self):
        self.treestore.clear()
        config_ = ConfigParser.RawConfigParser()
        self.file = config.FLOGS_CFG
        config_.read(config.ELOGS_CFG)
        for section in config_.sections():
            parent = self.add_root(section)
            for dir_, files_ in config_.items(section):
                child = self.add_dir(dir_, parent)
                for value in files_.split(","):
                    self.add_file(value, child)


class FileServersModel(ServersModel):
    def __init__(self, progress, sens_func, signals):
        self.progress = progress
        self.signals = signals
        self.read_config = sens_func(self._read_config)
        self.file = config.FLOGS_CFG
        super(FileServersModel, self).__init__()

    def _read_config(self, fill):
        self.treestore.clear()
        self.parents = {}
        fake_config = cStringIO.StringIO()
        self.file = config.FLOGS_CFG
        with open(config.FLOGS_CFG, 'r') as f:
            fake_config.writelines((line.strip() + " = \n" for line in f))
        fake_config.seek(0)
        config_ = ConfigParser.RawConfigParser()
        config_.optionxform = str
        config_.readfp(fake_config)
        frac = 1./len([i for s in config_.sections() for i in config_.items(s)])
        n = count(1)
        try:
            for server in config_.sections():
                parent = self.add_root(server, fill)
                for path, null in config_.items(server):
                    self.progress.set_text("%s: %s" % (server, path))
                    if self.signals['stop'] or self.signals['break']:
                        raise StopIteration
                    self.add_parents(path, parent, server)
                    if fill:
                        self.add_logdir(path, parent, server)
                    self.progress.set_fraction(next(n)*frac)
        except StopIteration:
            pass
        finally:
            self.close_conf(fake_config)
            self.signals['stop'] = False
            self.signals['break'] = False

    def close_conf(self, conf):
        conf.close()
        self.progress.set_text("")
        self.progress.set_fraction(0)
        
    def add_parents(self, path, parent, server):
        parts = [p for p in path.split(os.sep) if p]
        if path.startswith(r"\\"):
            parts[0] = r"\\"+parts[0]
        elif path.startswith(r"/"):
            parts[0] = "/"+parts[0]
        prev_node_path = server
        for n, p in enumerate(parts):
            new_node_path = join_path(server, os.sep.join(parts[:n+1]))
            self.new_dir_node(p, parent, new_node_path, prev_node_path)
            prev_node_path = new_node_path
            while gtk.events_pending():
                gtk.main_iteration()

    def check_break(self):
        if self.signals['break']:
            raise StopIteration

    def new_dir_node(self, f, parent, ext_parent, ext_prev_parent=None):
        while gtk.events_pending():
            gtk.main_iteration()
        self.check_break()
        node = self.parents.get(ext_parent)
        if not node:
            parent_ = self.parents.get(ext_prev_parent, parent)
            node = self.add_dir(f, parent_)
            self.parents[ext_parent] = node
        return node

    def file_callback(self, name, parent, ext_parent):
        while gtk.events_pending():
            gtk.main_iteration()
        self.check_break()
        parent_ = self.parents.get(ext_parent, parent)
        self.add_file(name, parent_)

    def add_logdir(self, path, parent, server):
        parent_ = self.parents.get(join_path(server, path), parent)
        dir_walker(path, self.new_dir_node, self.file_callback, parent_,
                    server)

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

    def show_config_editor(self, *args):
        if not config.EXT_CONFIG_EDITOR:
            ConfigEditor(self.srvrs.file)
        else:
            os.system('%s %s' % (config.EXT_CONFIG_EDITOR, self.srvrs.file))

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

        toolbar = gtk.Toolbar()
        reload_btn = gtk.ToolButton(gtk.STOCK_REFRESH)
        reload_btn.connect("clicked", lambda args: self.model.read_config(True))
        editconf_btn = gtk.ToolButton(gtk.STOCK_EDIT)
        editconf_btn.connect("clicked", lambda args: self.view.show_config_editor())
        search_entry = gtk.ToolItem()
        search_entry.set_expand(True)
        search_entry.add(self.hide_log)
        clear_btn = gtk.ToolButton(gtk.STOCK_CLEAR)
        clear_btn.connect("clicked", self.clear_entry)
        sep = gtk.SeparatorToolItem()

        toolbar.insert(reload_btn, 0)
        toolbar.insert(editconf_btn, 1)
        toolbar.insert(sep, 2)
        toolbar.insert(search_entry, 3)
        toolbar.insert(clear_btn, 4)

        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_MENU)

        self.box = gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.logs_window, True, True)
        self.box.pack_start(toolbar, False, False)
        self.hide_log.connect("changed", self.on_advanced_entry_changed)
        self.hide_log.connect("focus-in-event", self.on_hide_log_focus_in)
        self.hide_log.connect("focus-out-event", self.on_hide_log_focus_out)
        self.ft = False
        self.model.get_model().set_visible_func(self.visible_func)
        self.filter_text = ""
        self.show_all()

    def clear_entry(self, *args):
        self.filter_text = ""
        self.on_hide_log_focus_in()
        if not self.hide_log.is_focus():
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
    def __init__(self, progress, sens_func, signals):
        self.model = FileServersModel(progress, sens_func, signals)
        super(FileServersTree, self).__init__()


class LogsTrees(gtk.Notebook):
    def __init__(self, progress, sens_func, signals):
        super(LogsTrees, self).__init__()
        self.file_servers_tree = FileServersTree(progress, sens_func, signals)
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

    def fill(self, walk):
        self.file_servers_tree.model.read_config(walk)
        if self.evlogs_servers_tree:
            self.evlogs_servers_tree.model.read_config()

    def get_log_sources(self):
        flogs = pathes(self.file_servers_tree.model.get_active_servers())
        if self.evlogs_servers_tree:
            evlogs = ([(s[1], s[0]) for s in
                      self.evlogs_servers_tree.model.get_active_servers()])
        else:
            evlogs = []
        return (flogs, evlogs)

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


        
