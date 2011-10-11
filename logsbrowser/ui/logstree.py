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
from utils.xmlmanagers import SourceManager, SelectManager
from dialogs import save_dialog
from sourceactionsmanager import SourceActionsManagerUI
from utils.monitor import ConfigMonitor


def os_join(p1, p2):
    return os.sep.join([p1, p2])



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
        action(type_, path_, name, self.select_action(iter_),
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


    def get_active_servers(self):
        log_for_process = []
        getv = self.treestore.get_value

        def treewalk(iters):
            if getv(iters, 3) == 'f' and getv(iters, 2):
                cur_log = [getv(iters, 0)]
                parent = self.treestore.iter_parent(iters)
                while parent:
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

    def get_pathes(self):
        pathes = []
        getv = self.treestore.get_value

        def treewalk(iter_):
            if getv(iter_, 3) == 'f' and getv(iter_, 2):
                pathes.append(self.get_path(iter_))
                return
            it = self.treestore.iter_children(iter_)
            while it:
                treewalk(it)
                it = self.treestore.iter_next(it)

        root = self.treestore.iter_children(None)
        while root:
            treewalk(root)
            root = self.treestore.iter_next(root)
        return pathes
    
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

    def add_root(self, name, path):
        return self.treestore.append(None, [name,
                                            gtk.STOCK_DISCONNECT,
                                            None, 'n'])

    def add_dir(self, name, parent, path):
        return self.treestore.append(parent, [name,
                                            gtk.STOCK_DIRECTORY,
                                            None, 'd'])

    def add_file(self, name, parent):
        return self.treestore.append(parent, [name,
                                            gtk.STOCK_FILE,
                                            None, 'f'])

class EventServersModel(ServersModel):
    def __init__(self, stand, logs):
        super(EventServersModel, self).__init__()
        self.change_model(logs)

    def change_model(self, sources):
        self.treestore.clear()
        for k, v in sources.iteritems():
            child = self.add_dir(k, None, k)
            for l in v:
                self.add_file(l, child)


class FileServersModel(ServersModel):
    def __init__(self, progress, sens_func, signals, stand, logs):
        self.progress = progress
        self.signals = signals
        self.fill_tree = sens_func(self.fill_tree)
        self.fill_node = sens_func(self.fill_node)
        self.change_model = sens_func(self.change_model)
        self.stand = stand
        self.dirs = []
        super(FileServersModel, self).__init__()
        self.change_model(logs)

    def check_break(self):
        if self.signals['break']:
            raise StopIteration

    def change_model(self, dirs):
        dirs_for_del = [d for d in self.dirs if d not in dirs]
        new_dirs = [d for d in dirs if d not in self.dirs]
        self.remove_dirs(dirs_for_del)
        for dir_ in new_dirs:
            self.add_nodes(dir_)
        self.dirs = dirs

    def add_nodes(self, path, conn=False):
        parts = self.split_path(path)
        root, dirs = parts[0], parts[1:]
        parent = self.new_root_node(root, conn)
        for n, node_name in enumerate(dirs):
            node_path = os.sep.join(parts[:n + 2])
            parent = self.new_dir_node(node_name, parent, node_path, conn)
            while gtk.events_pending():
                gtk.main_iteration()

    def split_path(self, path):
        parts = [p for p in path.split(os.sep) if p]
        if path.startswith(r"\\"):
            parts[0] = r"\\" + parts[0]
        elif path.startswith(r"/"):
            parts[0] = "/" + parts[0]
        return parts

    def pathes_from_path(self, path):
        parts = self.split_path(path)
        root, dirs = parts[0], parts[1:]
        yield root
        for n, p in enumerate(dirs):
            yield os.sep.join(parts[:n+2])

    def new_root_node(self, node_name, conn):
        while gtk.events_pending():
            gtk.main_iteration()
        node = self.get_iter_by_path(node_name, conn)
        if not node:
            node = self.add_root(node_name, node_name)
        return node

    def new_dir_node(self, node_name, parent, node_path, conn):
        while gtk.events_pending():
            gtk.main_iteration()
        node = self.get_iter_by_path(node_path, conn)
        if not node:
            node = self.add_dir(node_name, parent, node_path)
        return node

    def find_iter_in_childs_by_name(self, iter_, val):
        getv = self.treestore.get_value
        it = self.treestore.iter_children(iter_)
        while it:
            if getv(it, 0) == val:
                return it
            it = self.treestore.iter_next(it)
        return None

    def find_root(self, name, conn):
        getv = self.treestore.get_value
        it = self.treestore.iter_children(None)
        while it:
            if getv(it, 0) == name and getv(it, 1) == (gtk.STOCK_CONNECT if
                                                        conn else gtk.STOCK_DISCONNECT):
                return it
            it = self.treestore.iter_next(it)
            while gtk.events_pending():
                gtk.main_iteration()
        return None

    def get_iter_by_path(self, path, conn=False):
        getv = self.treestore.get_value
        parts = self.split_path(path)
        it = self.find_root(parts[0], conn)
        if it:
            for p in parts[1:]:
                it = self.find_iter_in_childs_by_name(it, p)
                while gtk.events_pending():
                    gtk.main_iteration()
            return it
        else:
            return None

    def remove_dirs(self, dirs):
        iters_for_rm_conn = []
        iters_for_rm_disconn = []
        all_conn = set()
        all_disconn = set()
        for d in self.dirs:
            if self.get_iter_by_path(d, False):
                all_disconn.add(d)
            if self.get_iter_by_path(d, True):
                all_conn.add(d)
        all_disconn = all_disconn.difference(set(dirs))
        all_conn = all_conn.difference(set(dirs))
        all_disconn_set = set()
        all_conn_set = set()
        for dir_ in all_disconn:
            for d in set(self.pathes_from_path(dir_)):
                all_disconn_set.add(d)
        for dir_ in all_conn:
            for d in set(self.pathes_from_path(dir_)):
                all_conn_set.add(d)
        for rm_dir in dirs:
            rm_dir_set = set(self.pathes_from_path(rm_dir))
            if all_conn_set & rm_dir_set:
                for p in rm_dir_set.difference(all_conn_set):
                    iters_for_rm_conn.append(p)
            else:
                for p in rm_dir_set:
                    iters_for_rm_conn.append(p)
            if all_disconn_set & rm_dir_set:
                for p in rm_dir_set.difference(all_disconn_set):
                    iters_for_rm_disconn.append(p)
            else:
                for p in rm_dir_set:
                    iters_for_rm_disconn.append(p)

        for p in iters_for_rm_conn:
            c_iter = self.get_iter_by_path(p, True)
            if c_iter:
                self.treestore.remove(c_iter)

        for p in iters_for_rm_disconn:
            d_iter = self.get_iter_by_path(p, False)
            if d_iter:
                self.treestore.remove(d_iter)

    def remove_childs(self, it):
        child = self.treestore.iter_children(it)
        while child:
            next_ = self.treestore.iter_next(child)
            self.treestore.remove(child)
            child = next_

    def fill_tree(self):
        clear_source_formats(self.stand)
        self.treestore.clear()
        frac = 1. / len(self.dirs)
        for n, dir_ in enumerate(self.dirs):
            self.progress.set_text("%s" % dir_)
            self.add_nodes(dir_)
            if not (self.signals['stop'] or self.signals['break']):
                self.connect(dir_)
                try:
                    self.fill_dir(dir_)
                except StopIteration:
                    continue
            self.progress.set_fraction(frac * (n + 1))
        self.progress.set_fraction(0)
        self.progress.set_text("")
        self.signals['stop'] = False
        self.signals['break'] = False

    def connect(self, dir_):
        root = self.split_path(dir_)[0]
        it_connect = self.find_root(root, True)
        it_disconnect = self.find_root(root, False)
        if it_disconnect:
            if it_connect:
                self.add_nodes(dir_, True)
                self.treestore.remove(it_disconnect)
            else:
                self.treestore.set_value(it_disconnect, 1, gtk.STOCK_CONNECT)

    def iter_to_os_path(self, it):
        path = []
        while it:
            path.append(self.treestore.get_value(it, 0))
            it = self.treestore.iter_parent(it)
        return os.sep.join(path[::-1])

    def get_root(self, iter_):
        while self.treestore.get_value(iter_, 3) != 'n':
            iter_ = self.treestore.iter_parent(iter_)
        return iter_

    def get_child_pathes(self, iter_):

        def paths(it, acc=[]):
            if not self.treestore.iter_has_child(it) and self.treestore.get_value(it, 3) != 'f':
                yield acc

            it_ = self.treestore.iter_children(it)
            while it_:
                for path in paths(it_, [self.treestore.get_value(it_, 0)]+acc):
                    yield path
                it_ = self.treestore.iter_next(it_)

        for p in paths(iter_):
            yield os.sep.join(p[::-1])

    def clear_node(self, iter_):
        it = self.treestore.iter_children(iter_)
        while it:
            next_ = self.treestore.iter_next(it)
            self.treestore.remove(it)
            it = next_

    def get_dirs_for_update(self, path):
        iter_ = self.treestore.get_iter(path)
        os_path = self.iter_to_os_path(iter_)
        dirs = list(self.get_child_pathes(iter_))
        dirs_set = set()
        for dir_ in dirs:
            full_dir = os_join(os_path, dir_)
            for s_dirs in self.dirs:
                if full_dir.startswith(s_dirs):
                    dirs_set.add(s_dirs)
        return dirs_set


    def fill_node(self, path):
        self.progress.set_fraction(0)
        self.progress.set_text("Fill node...")
        iter_ = self.treestore.get_iter(path)
        if self.treestore.get_value(iter_, 3) != 'f':
            os_path = self.iter_to_os_path(iter_)
            root = self.get_root(iter_)
            need_move = True
            if self.treestore.get_value(root, 1) == gtk.STOCK_DISCONNECT:
                dirs = []
                for dir_ in self.get_child_pathes(iter_):
                    if dir_:
                        dirs.append(os_join(os_path, dir_))
                    else:
                        dirs.append(os_path)
                root_name = self.treestore.get_value(root, 0)
                other_dirs = [d for d in [os_join(root_name, dir_) for dir_ in self.get_child_pathes(root)] if d not in dirs]
                self.clear_node(root)
                pos = self.treestore.iter_next(root)
                if not self.find_root(root_name, True):
                    self.treestore.set_value(root, 1, gtk.STOCK_CONNECT)
                else:
                    self.treestore.remove(root)
                    need_move = False
                for dir_ in dirs:
                    self.add_nodes(dir_, True)
                    self.fill_dir(dir_)
                for dir_ in other_dirs:
                    self.add_nodes(dir_)
                disc_root = self.get_iter_by_path(root_name, False)
                if disc_root:
                    if need_move:
                        root = self.get_iter_by_path(root_name, True)
                        self.treestore.move_after(disc_root, root)
                    else:
                        self.treestore.move_before(disc_root, pos)
            else:
                is_root = (self.treestore.get_value(iter_, 3) == 'n')
                if is_root:
                    dirs = list(self.get_child_pathes(iter_))
                    self.clear_node(iter_)
                    dirs_set = set()
                    for dir_ in dirs:
                        full_dir = os_join(os_path, dir_)
                        for s_dirs in self.dirs:
                            if full_dir.startswith(s_dirs):
                                dirs_set.add(s_dirs)
                    for d in dirs_set:
                        self.add_nodes(d, True)
                        self.fill_dir(d)
                else:
                    dirs_to_update = set()
                    for dir_ in self.dirs:
                        if dir_.startswith(os_path) and self.get_iter_by_path(dir_, True):
                            dirs_to_update.add(dir_)
                    self.clear_node(iter_)
                    if dirs_to_update:
                        for d in dirs_to_update:
                            self.add_nodes(d, True)
                            self.fill_dir(d)
                    else:
                        self.fill_dir(os_path)
        self.progress.set_text("")

    def file_callback(self, name, parent, ext_parent):
        parent_ = self.get_iter_by_path(ext_parent, True) or parent
        self.add_file(name, parent_)
        while gtk.events_pending():
            gtk.main_iteration()
        #self.check_break()

    def fill_dir(self, path):
        parent_ = self.get_iter_by_path(path, True)
        dir_walker(path, self.new_dir_node, self.file_callback, self.stand, parent_)



class DisplayServersModel:
    """ Displays the Info_Model model in a view """
    def __init__(self, visible_func):
        """ Form a view for the Tree Model """
        self.models = {}
        self.stand = None
        self.view = gtk.TreeView(None)
        self.servers_model = None
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('editable', False)
        self.stockrenderer = gtk.CellRendererPixbuf()
        self.renderer1 = gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect('toggled', self.col1_toggled_cb)
        self.renderer2 = gtk.CellRendererText()
        self.column0 = gtk.TreeViewColumn("Path")
        self.column0.pack_start(self.renderer1, False)
        self.column0.pack_start(self.stockrenderer, False)
        self.column0.pack_start(self.renderer, True)
        self.column0.add_attribute(self.renderer1, 'active', 2)
        self.column0.set_attributes(self.stockrenderer, stock_id=1)
        self.column0.set_attributes(self.renderer, text=0)
        self.column2 = gtk.TreeViewColumn("Type", self.renderer2)
        self.column2.set_visible(False)
        self.view.append_column(self.column0)
        self.view.append_column(self.column2)
        self.view.connect("button-press-event", self.tree_actions)

    def col1_toggled_cb(self, cell, path):
        """
        Sets the toggled state on the toggle button to true or false.
        """
        true_model = self.servers_model.treestore
        true_path = self.servers_model.get_model().convert_path_to_child_path(path)
        state = true_model[true_path][2] = not true_model[true_path][2]

        def walk(child):
            for ch in child.iterchildren():
                ch[2] = state
                walk(ch)

        walk(true_model[true_path])
        return

    def tree_actions(self, view, event):
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            if path:
                model = view.get_model()
                true_model = self.servers_model.treestore
                true_path =  self.servers_model.get_model().convert_path_to_child_path(path[0])
                self.servers_model.fill_node(true_path)

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
    def __init__(self, root):
        super(ServersTree, self).__init__()
        self.view = DisplayServersModel(self.visible_func)
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
        cbtn.connect_object("event", self.select_popup, SelectsMenu(self, root))
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
        self.filter_text = ""
        self.show_all()

    def set_tree(self, stand, logs):
        if self.view.servers_model:
            self.view.models[self.view.stand] = self.view.servers_model
        self.view.stand = stand
        model = self.view.models.get(stand)
        if model:
            self.view.servers_model = model
            self.view.servers_model.change_model(logs)
        else:
            self.view.servers_model = self.new_model(stand, logs)
            self.view.servers_model.get_model().set_visible_func(self.visible_func)
        self.view.view.set_model(self.view.servers_model.get_model())
        self.set_text((self.filter_text, self.ft))

    def get_pathes(self):
        return self.view.servers_model.get_pathes()

    def apply_select(self, menuitem, select, manager):
        actions = manager.get_select_actions(select)
        for action in actions:
            self.view.servers_model.select_rows(action)

    def select_popup(self, menu, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            menu.build_submenu()
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
        model = self.view.servers_model
        if model:
            model.get_model().refilter()
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
    def __init__(self, root):
        super(EvlogsServersTree, self).__init__(root)

    def new_model(self, stand, logs):
        return EventServersModel(stand, logs)

class FileServersTree(ServersTree):
    def __init__(self, progress, sens_func, signals, root):
        self.progress = progress
        self.sens_func = sens_func
        self.signals = signals
        super(FileServersTree, self).__init__(root)

    def new_model(self, stand, logs):
        return FileServersModel(self.progress, self.sens_func, self.signals, stand, logs)

    def fill_tree(self):
        self.view.servers_model.fill_tree()



class LogsTrees(gtk.Notebook):
    def __init__(self, progress, sens_func, signals, root):
        super(LogsTrees, self).__init__()
        self.file_servers_tree = FileServersTree(progress, sens_func, signals, root)
        file_label = gtk.Label("Filelogs")
        file_label.show()
        self.append_page(self.file_servers_tree, file_label)
        self.evlogs_servers_tree = None
        if sys.platform == 'win32':
            evt_label = gtk.Label("Eventlogs")
            evt_label.show()
            self.evlogs_servers_tree = EvlogsServersTree(root)
            self.evlogs_servers_tree.show()
            self.append_page(self.evlogs_servers_tree, evt_label)

    def change_stand(self, stand, filelogs, evlogs):
        if self.evlogs_servers_tree:
            self.evlogs_servers_tree.set_tree(stand, evlogs)
        self.file_servers_tree.set_tree(stand, filelogs)

    def fill_trees(self):
        self.file_servers_tree.fill_tree()


class SourceManagerUI(gtk.VBox):
    def __init__(self, progress, sens_func, signals, root):
        gtk.VBox.__init__(self)
        self.state_ = {}

        stand_manager = gtk.Toolbar()
        self.trees = LogsTrees(progress, sens_func, signals, root)
        self.source_manager = SourceManager(config.SOURCES_XML)
        self.config_monitor = ConfigMonitor(config.SOURCES_XML)
        self.config_monitor.register_action(self.config_changed)


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
        self.pack_start(self.trees, True, True)

        self.show_all()

    def config_changed(self, *args):
        stand = self.stand_choice.get_active_text()
        new_model = gtk.ListStore(str)
        self.stand_choice.set_model(None)
        active = None
        for n, st in enumerate(self.source_manager.stands):
            new_model.append([st])
            if st == self.source_manager.default_stand:
                self.default = n
            if st == stand:
                active = n
        self.stand_choice.set_model(new_model)
        self.stand_choice.set_active(active if active is not None else self.default)

    def get_log_sources(self):
        flogs = pathes(self.trees.file_servers_tree.view.servers_model.get_active_servers(),
                        self.trees.file_servers_tree.view.servers_model.stand)
        if self.trees.evlogs_servers_tree:
            evlogs = ([(s[1], s[0], None) for s in
                      self.trees.evlogs_servers_tree.view.servers_model.get_active_servers()])
        else:
            evlogs = []
        return (flogs, evlogs)

    def load_state(self, page):
        ftree = self.trees.file_servers_tree
        etree = self.trees.evlogs_servers_tree
        state = self.state_.get(page)
        if state:
            fpathslist, fentry, epathslist, eentry, stand = state
        else:
            fpathslist, fentry, epathslist, eentry, stand = ([], ("", False),
                                                          [], ("", False),
                                                          self.default)
        self.stand_choice.set_active(stand)
        ftree.view.servers_model.set_active_from_paths(fpathslist)
        ftree.set_text(fentry)
        if etree:
            etree.view.servers_model.set_active_from_paths(epathslist)
            etree.set_text(eentry)


    def save_state(self, page):
        ftree = self.trees.file_servers_tree
        fpathslist = ftree.view.servers_model.get_active_check_paths()
        fentry = ftree.filter_text, ftree.ft
        etree = self.trees.evlogs_servers_tree
        stand = self.stand_choice.get_active()
        if etree:
            epathslist = etree.view.servers_model.get_active_check_paths()
            eentry = etree.filter_text, ftree.ft
        else:
            epathslist = []
            eentry = ()
        self.state_[page] = (fpathslist, fentry, epathslist, eentry, stand)

    def free_state(self, page):
        del self.state_[page]

    def change_stand(self, *args):
        stand = self.stand_choice.get_active_text()
        flogs = self.source_manager.get_filelog_sources(stand)
        elogs = self.source_manager.get_evlog_sources(stand)
        self.trees.change_stand(stand, flogs, elogs)

    def fill(self):
        stand = self.stand_choice.get_active_text()
        self.trees.fill_trees()


    def fill_combo(self):
        for n, stand in enumerate(self.source_manager.stands):
            self.stand_choice.append_text(stand)
            if stand == self.source_manager.default_stand:
                self.stand_choice.set_active(n)
                self.default = n


class SelectsMenu(gtk.Menu):
    def __init__(self, tree, root):
        super(SelectsMenu, self).__init__()
        self.tree = tree
        self.select_manager = SelectManager(config.SELECTS)
        self.show = gtk.MenuItem("Select")
        save = gtk.MenuItem("Save")
        save.connect("activate", self.save)
        edit = gtk.MenuItem("Edit")
        edit.connect("activate", self.show_edit_window, root)
        self.append(self.show)
        self.append(save)
        self.append(edit)
        self.show_all()
        
    def show_edit_window(self, menuitem, root):
        SourceActionsManagerUI(self.select_manager, root)
        
    def build_submenu(self):
        self.show.remove_submenu()
        submenu = gtk.Menu()
        for item in self.select_manager.selects:
            mitem = gtk.MenuItem(item)
            mitem.connect("activate", self.tree.apply_select, item, self.select_manager)
            submenu.append(mitem)
        submenu.show_all()
        self.show.set_submenu(submenu)

    def save(self, *args):
        name = save_dialog()
        if name != 0:
            pathes = self.tree.get_pathes()
            self.select_manager.save_pathes(name, pathes)






