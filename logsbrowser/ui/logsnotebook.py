import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from logslist import LogsListWindow


class LogsNotebook(gtk.Notebook):
    def __init__(self, tree, btn):
        super(LogsNotebook, self).__init__()
        self.filters = {}
        self.tree = tree
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
        self.labels = []
        self.counter = 1
        ll=self.add_new_page()
        #self.tree.save_state(ll)
        self.set_current_page(0)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.set_scrollable(True)
        self.show()
        act_box.show()
        self.set_action_widget(act_box, gtk.PACK_END)
        self.connect("switch_page", self.change_source_tree)
        self.sens = [add_btn, btn]

    def set_sens(self, sens):
        for b in self.btns:
            b.set_sensitive(sens)
        for l in self.labels:
            l.set_sensitive(sens)
        page_num = 0
        page = self.get_nth_page(page_num)
        while page:
            for w in page.sens_list:
                w.set_sensitive(sens)
            page_num += 1
            page = self.get_nth_page(page_num)
        for s in self.sens:
            s.set_sensitive(sens)

    def change_source_tree(self, ntb, page, page_num, *args):
        ncurpage = self.get_current_page()
        if ncurpage >= 0:
            cur_page = self.get_nth_page(ncurpage)
            self.tree.save_state(cur_page)
        new_page = self.get_nth_page(page_num)
        self.tree.load_state(new_page)
        self.tree.save_state(new_page)

    def change_page_name(self, widget, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.page = self.get_nth_page(self.get_current_page())
            self.mem_tab = self.get_tab_label(self.page)
            txt = self.mem_tab.get_children()[0].get_children()[0].get_text()
            self.entry = gtk.Entry()
            self.entry.set_has_frame(False)
            self.entry.set_width_chars(12)
            self.entry.set_text(txt)
            self.entry.connect("focus-out-event", self.new_page_name, txt)
            self.set_tab_label(self.page, self.entry)
            self.entry.grab_focus()

    def new_page_name(self, *args):
        old_name = args[-1]
        name = self.entry.get_text().replace(" ","_")
        self.mem_tab.get_children()[0].get_children()[0].\
                           set_text(name)
        filter_ = self.filters[old_name]
        self.filters[name] = filter_
        del self.filters[old_name]
        self.page.set_name(name)
        self.mem_tab.show_all()
        self.set_tab_label(self.page, tab_label=self.mem_tab)
        self.notify_filters()

    def add_new_page(self):
        tab_lab = gtk.HBox()
        name = "Page_%s" % self.counter
        label = gtk.Label(name)
        e = gtk.EventBox()
        e.add(label)
        e.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        e.connect("button-press-event", self.change_page_name)
        e.set_visible_window(False)
        self.labels.append(e)
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
        l_list = LogsListWindow(self)
        l_list.set_name(name)
        l_list.show()
        tab_lab.show()
        num = self.append_page(l_list, tab_lab)
        self.show_all()
        self.counter += 1
        self.filters[name] = l_list.get_filter()
        self.notify_filters()
        return l_list

    def add_new(self, *args):
        self.add_new_page()
        self.set_current_page(len(self.get_children()) - 1)

    def full_pages_menu(self):
        menu = gtk.Menu()
        page_num = 0
        page = self.get_nth_page(page_num)
        while page:
            try:
                page_name = self.get_tab_label(page).get_children()[0].\
                            get_children()[0].get_text()
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
        popup.popup(None, None, None, 1, 0)

    def switch_to(self, copy_to_page, log_list):
        self.set_current_page(self.page_num(log_list))

    @property
    def get_current_loglist(self):
        logsw = self.get_nth_page(self.get_current_page())
        return logsw.log_list.model

    @property
    def get_current_view(self):
        logsw = self.get_nth_page(self.get_current_page())
        return logsw.log_list.view

    @property
    def get_current_logs_store(self):
        logsw = self.get_nth_page(self.get_current_page())
        return logsw.log_list

    def get_logs_list_window(self):
        return self.get_nth_page(self.get_current_page())

    def notify_filters(self):
        for page, filter_ in self.filters.iteritems():
            filter_.update_filters(self.filters)

    def close_tab(self, args):
        child = self.btns.index(args)
        page = self.get_nth_page(child)
        tab = self.get_tab_label(page)
        txt = tab.get_children()[0].get_children()[0].get_text()
        self.tree.free_state(page)
        self.btns.pop(child)
        self.labels.pop(child)
        self.filters.pop(txt)
        page.log_list.clear()
        self.remove_page(child)
        if len(self.get_children()) == 0:
            self.counter = 1
            self.add_new_page()
        self.notify_filters()
