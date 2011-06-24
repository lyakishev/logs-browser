import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango
import os
from configeditor import ConfigEditor
import sys
from source.worker import dir_walker, join_path, pathes, clear_source_formats
import config
from itertools import count
from utils.xmlmanagers import SourceManager, SelectManager


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

    def do_actions(self, action, iter_):
        getv = self.treestore.get_value
        name = getv(iter_, 0)
        type_ = getv(iter_, 3)
        path_ = self.get_path(iter_)
        return action(type_, path_, name, self.select_action(iter_),
                                          self.unselect_action(iter_))

    def get_path(self, node):
        getv = self.treestore.get_value
        path = []
        path.append(getv(node, 0))
        parent = self.treestore.iter_parent(node)
        while parent:
            path.append(getv(parent, 0))
            parent = self.treestore.iter_parent(parent)
        path.reverse()
        return os.sep.join(path)

    def select_recursively(self, iter_, val):
        getv = self.treestore.get_value
        setv = self.treestore.set_value
        def walk(it):
            setv(it, 2, val)
            it_ = self.treestore.iter_children(it)
            while it_:
                walk(it_)
                it_ = self.treestore.iter_next(it_)

        if getv(iter_, 3) in ("d", "n"):
            walk(iter_)
        else:
            setv(iter_, 2, val)

    def select_action(self, iter_):
        def select():
            self.select_recursively(iter_, 1)
        return select

    def unselect_action(self, iter_):
        def unselect():
            self.select_recursively(iter_, 0)
        return unselect


    def select_rows(self, action):
        def treewalk(iter_):
            self.do_actions(action, iter_)
            it = self.treestore.iter_children(iter_)
            while it:
                treewalk(it)
                it = self.treestore.iter_next(it)
        root = self.treestore.iter_children(None)
        while root:
            treewalk(root)
            root = self.treestore.iter_next(root)

    def set_from_copy(self, copy_treestore):
        self._copy(copy_treestore, self)

    def copy(self):
        copy_treestore = ServersModel()
        self._copy(self.treestore, copy_treestore)
        return copy_treestore.treestore

    def _copy(self, treestore, copytreestore):
        getv = treestore.get_value
        copy_treestore = copytreestore

        def treewalk(iter_, parent):
            val = getv(iter_, 3)
            name = getv(iter_, 0)
            if val == 'n':
                filled = True if getv(iter_, 1) == gtk.STOCK_CONNECT else False
                parent_copy = copy_treestore.add_root(name, filled)
            elif val == 'd':
                parent_copy = copy_treestore.add_dir(name, parent)
            elif val == 'f':
                parent_copy = copy_treestore.add_file(name, parent)
            it = treestore.iter_children(iter_)
            while it:
                treewalk(it, parent_copy)
                it = treestore.iter_next(it)
        root = treestore.iter_children(None)
        while root:
            treewalk(root, None)
            root = treestore.iter_next(root)

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
        super(EventServersModel, self).__init__()

    def fill(self, sources):
        self.treestore.clear()
        for k, v in sources.iteritems():
            child = self.add_dir(k, None)
            for l in v:
                self.add_file(l, child)


class FileServersModel(ServersModel):
    def __init__(self, progress, sens_func, signals):
        self.progress = progress
        self.signals = signals
        self.fill = sens_func(self.fill)
        self.dirs = None
        self.stand = None
        self.cache = {}
        super(FileServersModel, self).__init__()

    def fill(self, fill, dirs = None, stand = None):
        self.treestore.clear()
        if fill:
            clear_source_formats(stand)
            self._fill(dirs, stand)
            self.cache[self.stand] = (self.copy(), self.dirs, self.stand)
        else:
            cached_model = self.get_model_from_cache(stand)
            if cached_model:
                self.set_from_copy(cached_model[0])
                self.dirs = cached_model[1]
                self.stand = cached_model[2]
            else:
                self._fill(dirs, stand)
                self.cache[self.stand] = (self.copy(), self.dirs, self.stand)

    def _fill(self, dirs, stand):
        self.parents={}
        fill = True
        if dirs:
            self.dirs = dirs
            fill = False
        if stand:
            self.stand = stand
        frac = 1./len(self.dirs)
        try:
            for n, path in enumerate(self.dirs):
                self.progress.set_text("%s" % path)
                if self.signals['stop'] or self.signals['break']:
                    raise StopIteration
                self.add_parents(path, None, self.stand)
                if fill:
                    self.add_logdir(path, None, self.stand)
                self.progress.set_fraction(frac*(n+1))
        except StopIteration:
            pass
        finally:
            self.signals['stop'] = False
            self.signals['break'] = False
            self.progress.set_text("")
            self.progress.set_fraction(0)

    def get_model_from_cache(self, stand):
        return self.cache.get(stand)

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

        cbtn = gtk.Button()
        cbtn.connect_object("event", self.select_popup, SelectsMenu(self))
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU)
        image.show()
        cbtn.add(image)
        editconf_btn = gtk.ToolItem()
        editconf_btn.add(cbtn)
        search_entry = gtk.ToolItem()
        search_entry.set_expand(True)
        search_entry.add(self.hide_log)
        clear_btn = gtk.ToolButton(gtk.STOCK_CLEAR)
        clear_btn.connect("clicked", self.clear_entry)
        sep = gtk.SeparatorToolItem()

        toolbar.insert(editconf_btn, 0)
        toolbar.insert(sep, 1)
        toolbar.insert(search_entry, 2)
        toolbar.insert(clear_btn, 3)

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

    def apply_select(self, menuitem, select, manager):
        actions = manager.get_select_actions(select)
        for action in actions:
            self.model.select_rows(action)

    def select_popup(self, menu, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            menu.popup(None, None, None, event.button, event.time)
            return True
        return False

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

    def fill_tree(self, filelogs, evlogs, stand):
        if self.evlogs_servers_tree:
            self.evlogs_servers_tree.model.fill(evlogs)
        self.file_servers_tree.model.fill(False, filelogs, stand)

    def fill(self, evlogs):
        self.file_servers_tree.model.fill(True)
        if self.evlogs_servers_tree:
            self.evlogs_servers_tree.model.fill(evlogs)


class SourceManagerUI(gtk.VBox):
    def __init__(self, progress, sens_func, signals):
        gtk.VBox.__init__(self)
        self.state_ = {}

        stand_manager = gtk.Toolbar()
        self.tree = LogsTrees(progress, sens_func, signals)
        self.source_manager = SourceManager(config.SOURCES_XML)


        reload_btn = gtk.ToolButton(gtk.STOCK_REFRESH)
        reload_btn.connect("clicked", lambda args: self.fill())
        stand_choice_item = gtk.ToolItem()
        stand_choice_item.set_expand(True)

        self.stand_choice = gtk.combo_box_new_text()
        self.stand_choice.connect('changed', self.change_stand)
        stand_choice_item.add(self.stand_choice)

        stand_manager.insert(reload_btn, 0)
        stand_manager.insert(stand_choice_item, 1)
        stand_manager.set_style(gtk.TOOLBAR_ICONS)
        stand_manager.set_icon_size(gtk.ICON_SIZE_MENU)

        self.pack_start(stand_manager, False, False)
        self.pack_start(self.tree, True, True)

        self.show_all()

    def fill(self):
        stand = self.stand_choice.get_active_text()
        self.tree.fill(self.source_manager.get_evlog_sources(stand))

    def get_log_sources(self):
        flogs = pathes(self.tree.file_servers_tree.model.get_active_servers(),
                        self.tree.file_servers_tree.model.stand)
        if self.tree.evlogs_servers_tree:
            evlogs = ([(s[1], s[0], None) for s in
                      self.tree.evlogs_servers_tree.model.get_active_servers()])
        else:
            evlogs = []
        return (flogs, evlogs)

    def load_state(self, page):
        ftree = self.tree.file_servers_tree
        etree = self.tree.evlogs_servers_tree
        state = self.state_.get(page)
        if state:
            fpathslist, fentry, epathslist, eentry, stand = state
        else:
            fpathslist, fentry, epathslist, eentry, stand = ([],("",False),
                                                          [],("",False),
                                                          self.default)
        self.stand_choice.set_active(stand)
        ftree.model.set_active_from_paths(fpathslist)
        ftree.set_text(fentry)
        if etree:
            etree.model.set_active_from_paths(epathslist)
            etree.set_text(eentry)


    def save_state(self, page):
        ftree = self.tree.file_servers_tree
        fpathslist = ftree.model.get_active_check_paths()
        fentry = ftree.filter_text, ftree.ft
        etree = self.tree.evlogs_servers_tree
        stand = self.stand_choice.get_active()
        if etree:
            epathslist = etree.model.get_active_check_paths()
            eentry = etree.filter_text, ftree.ft
        else:
            epathslist = []
            eentry = ()
        self.state_[page] = (fpathslist, fentry, epathslist, eentry, stand)

    def free_state(self, page):
        del self.state_[page]

    def change_stand(self, *args):
        stand = self.stand_choice.get_active_text()
        self.tree.fill_tree(self.source_manager.get_filelog_sources(stand),
                            self.source_manager.get_evlog_sources(stand),
                            stand)

    def fill_combo(self):
        for n, stand in enumerate(self.source_manager.stands):
            self.stand_choice.append_text(stand)
            if stand == self.source_manager.default_stand:
                self.stand_choice.set_active(n)
                self.default = n


class SelectsMenu(gtk.Menu):
    def __init__(self, tree):
        super(SelectsMenu, self).__init__()
        self.select_manager = SelectManager(config.SELECTS)
        show = gtk.MenuItem("Select")
        show.set_submenu(self.build_submenu(tree))
        save = gtk.MenuItem("Save")
        new = gtk.MenuItem("New")
        self.append(show)
        self.append(save)
        self.append(new)
        self.show_all()

    def build_submenu(self, tree):
        submenu = gtk.Menu()
        for item in self.select_manager.selects:
            mitem = gtk.MenuItem(item)
            mitem.connect("activate", tree.apply_select, item, self.select_manager)
            submenu.append(mitem)
        submenu.show_all()
        return submenu






