import pygtk
pygtk.require("2.0")
import gtk, gobject, gio

from widgets.logs_list import LogListWindow


class LogsNotebook(gtk.Notebook):
    def __init__(self):
        super(LogsNotebook, self).__init__()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
        fiction = gtk.Label()
        self.btns = []
        self.append_page(fiction, image)
        self.counter = 1
        self.add_new_page(0, str(self.counter))
        self.set_current_page(0)
        self.connect("switch_page", self.add_and_switch_to_new)
        self.show()

    def add_new_page(self, pos, text):
        tab_lab = gtk.HBox()
        label = gtk.Label(text)
        tab_button = gtk.Button()
        tab_button.connect("clicked", self.close_tab)
        tab_button.set_relief(gtk.RELIEF_NONE)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        tab_button.add(image)
        self.btns.append(tab_button)
        tab_lab.pack_start(label, True, True)
        tab_lab.pack_start(tab_button, False, False)
        tab_lab.show_all()
        l_list = LogListWindow()
        l_list.show()
        tab_lab.show()
        self.insert_page(l_list, tab_lab, pos)
        self.show_all()

    def add_and_switch_to_new(self, ntb, page, page_num, *args):
        ntab = len(self.get_children())
        if ntab == page_num+1:
            self.counter += 1
            self.add_new_page(page_num, str(self.counter))
            self.stop_emission('switch-page')
            self.set_current_page(page_num)

    @property
    def get_current_loglist(self):
        logsw=self.get_nth_page(self.get_current_page())
        return logsw.logs_store.list_store

    @property
    def get_current_view(self):
        logsw=self.get_nth_page(self.get_current_page())
        return logsw.logs_view.view
        

    def close_tab(self, args):
        self.set_current_page(0)
        child = self.btns.index(args)
        self.btns.pop(child)
        self.remove_page(child)

        


