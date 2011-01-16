import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import datetime
from log_window import SeveralLogsWindow

from widgets.logs_list import LogListWindow


class LogsNotebook(gtk.Notebook):
    def __init__(self):
        super(LogsNotebook, self).__init__()
        act_box = gtk.HBox()
        add_btn = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
        image.show()
        add_btn.add(image)
        add_btn.show()
        add_btn.connect("clicked", self.add_new)
        act_box.pack_start(add_btn)
        pages_btn = gtk.Button()
        image_pages = gtk.Image()
        image_pages.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        image_pages.show()
        pages_btn.add(image_pages)
        pages_btn.show()
        pages_btn.connect("clicked", self.show_all_pages_menu)
        act_box.pack_start(pages_btn)
        self.btns = []
        self.counter = 1
        self.add_new_page()
        self.set_current_page(0)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.set_scrollable(True)
        self.show()
        act_box.show()
        self.set_action_widget(act_box, gtk.PACK_END)

    def change_page_name(self, widget, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.page = self.get_nth_page(self.get_current_page())
            self.mem_tab=self.get_tab_label(self.page)
            txt = self.mem_tab.get_children()[0].get_children()[0].get_text()
            self.entry = gtk.Entry()
            self.entry.set_has_frame(False)
            self.entry.set_width_chars(12)
            self.entry.set_text(txt)
            self.entry.connect("focus-out-event", self.new_page_name)
            self.set_tab_label(self.page, self.entry)
            self.entry.grab_focus()

    def new_page_name(self, *args):
        self.mem_tab.get_children()[0].get_children()[0].set_text(self.entry.get_text())
        self.mem_tab.show_all()
        self.set_tab_label(self.page, tab_label=self.mem_tab)

    def add_new_page(self):
        tab_lab = gtk.HBox()
        label = gtk.Label("Page "+str(self.counter))
        e = gtk.EventBox()
        e.add(label)
        e.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        e.connect("button-press-event", self.change_page_name)
        tab_button = gtk.Button()
        tab_button.connect("clicked", self.close_tab)
        tab_button.set_relief(gtk.RELIEF_NONE)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        tab_button.add(image)
        self.btns.append(tab_button)
        tab_lab.pack_start(e, True, True)
        tab_lab.pack_start(tab_button, False, False)
        tab_lab.show_all()
        l_list = LogListWindow()
        l_list.get_view.connect("button-press-event", self.show_menu)
        l_list.show()
        tab_lab.show()
        num = self.append_page(l_list, tab_lab)
        self.show_all()
        self.counter+=1
        return num

    def add_new(self, *args):
        self.add_new_page()
        self.set_current_page(len(self.get_children())-1)
        
    def pages_menu(self):
        menu = gtk.Menu()
        page_num = 0
        page = self.get_nth_page(page_num)
        while page:
            try:
                page_name = self.get_tab_label(page).get_children()[0].get_children()[0].get_text()
            except AttributeError:
                break
            if page_num != self.get_current_page():
                menu_item = gtk.MenuItem(page_name)
                menu_item.connect("activate", self.copy_to_page, page)
                menu.append(menu_item)
            page_num += 1
            page = self.get_nth_page(page_num)
        sep = gtk.SeparatorMenuItem()
        menu_item = gtk.MenuItem("New page")
        menu_item.connect("activate", self.copy_to_new_page)
        menu.append(sep)
        menu.append(menu_item)
        menu.show_all()
        return menu

    def full_pages_menu(self):
        menu = gtk.Menu()
        page_num = 0
        page = self.get_nth_page(page_num)
        while page:
            try:
                page_name = self.get_tab_label(page).get_children()[0].get_children()[0].get_text()
            except AttributeError:
                break
            menu_item = gtk.MenuItem(page_name)
            menu_item.connect("activate", self.switch_to, page)
            menu.append(menu_item)
            page_num += 1
            page = self.get_nth_page(page_num)
        menu.show_all()
        return menu

    def show_all_pages_menu(self, *args):
        popup = self.full_pages_menu()
        popup.popup(None,None,None,1,0)

    def switch_to(self, copy_to_page, log_list):
        self.set_current_page(self.page_num(log_list))

    def copy_to_new_page(self, *args):
        ntab = len(self.get_children())
        #self.counter+=1
        new_pagenum = self.add_new_page()
        new_page = self.get_nth_page(new_pagenum)
        self.copy_to_page(None, new_page)
        
    def show_menu(self, treeview, event):
        if event.button == 3:
         # Figure out which item they right clicked on
            path = treeview.get_path_at_pos(int(event.x),int(event.y))
             # Get the selection
            selection = treeview.get_selection()
             # Get the selected path(s)
            model, rows, = selection.get_selected_rows()
         # If they didnt right click on a currently selected row, change the selection
            if path[0] not in rows:
                selection.unselect_all()
                selection.select_path(path[0])
            popup = gtk.Menu()
            cp = gtk.MenuItem("Copy to")
            cp.set_submenu(self.pages_menu())
            popup.append(cp)
            popup.show_all()
            popup.popup( None, None, None, event.button, event.time)
        menu.show_all()
        return menu
    
    def copy_to_page(self, menuitem, log_list):
        view = self.get_current_view
        selection = view.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        val = model.get_value
        n = len(model[0])
        to_view = log_list.get_view
        to_model = to_view.get_model()
        to_model.set_default_sort_func(lambda *args: -1)
        to_model.set_sort_column_id(-1, gtk.SORT_ASCENDING)
        to_set = log_list.logs_store.set_of_rows()
        to_view.freeze_child_notify()
        to_view.set_model(None)
        for path in pathlist:
            iter = model.get_iter(path)
            copy = [val(iter,v) for v in xrange(n)]
            copy[6]="#FFFFFF"
            copy =tuple(copy)
            if copy not in to_set:
                to_model.insert_after(None, copy)
                to_set.add(copy)
        to_model.set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        to_view.set_model(to_model)
        to_view.thaw_child_notify()

    def show_menu(self, treeview, event):
        if event.button == 3:
         # Figure out which item they right clicked on
            path = treeview.get_path_at_pos(int(event.x),int(event.y))
             # Get the selection
            selection = treeview.get_selection()
             # Get the selected path(s)
            model, rows, = selection.get_selected_rows()
         # If they didnt right click on a currently selected row, change the selection
            if path[0] not in rows:
                selection.unselect_all()
                selection.select_path(path[0])
            popup = gtk.Menu()
            cp = gtk.MenuItem("Copy to")
            cp.set_submenu(self.pages_menu())
            aio = gtk.MenuItem("In one")
            aio.connect("activate", self.show_all_in_one)
            popup.append(aio)
            popup.append(cp)
            popup.show_all()
            popup.popup( None, None, None, event.button, event.time)
            return True

    def show_all_in_one(self, *args):
        view = self.get_current_view
        selection = view.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        logs_w = SeveralLogsWindow(model, view, model.get_iter(pathlist[0]),selection)
        

    @property
    def get_current_loglist(self):
        logsw=self.get_nth_page(self.get_current_page())
        return logsw.logs_store.list_store

    @property
    def get_current_view(self):
        logsw=self.get_nth_page(self.get_current_page())
        return logsw.logs_view.view

    @property
    def get_current_logs_store(self):
        logsw=self.get_nth_page(self.get_current_page())
        return logsw.logs_store
        

    def close_tab(self, args):
        self.set_current_page(0)
        child = self.btns.index(args)
        self.btns.pop(child)
        self.remove_page(child)
        if len(self.get_children())==0:
            self.counter = 1
            self.add_new_page()


        



