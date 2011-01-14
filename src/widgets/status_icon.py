import pygtk
pygtk.require("2.0")
import gtk, gobject, gio


class StatusIcon:
    def __init__(self, date_filter, window):
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_YES) 
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.connect("activate", self.change_mode)
        self.statusicon.set_tooltip("Log Viewer")
        self.record = 0
        self.date_filter = date_filter
        self.window = window
        self.hide = 0

    def change_mode(self, *args):
        if self.record:
            self.statusicon.set_from_stock(gtk.STOCK_YES)
            self.date_filter.fromto_option.to_date.set_now()
            self.record = 0
        else:
            self.statusicon.set_from_stock(gtk.STOCK_NO)
            self.date_filter.fromto_option.from_date.set_now()
            self.record = 1
       
    def hide_main_window(self, *args):
        self.window.hide()

    def show_main_window(self, *args):
        self.window.show()

    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()
        if self.hide:
            show = gtk.MenuItem("Show")
            show.connect("activate", self.show_main_window)
            menu.append(show)
            self.hide = 0
        else:
            hide = gtk.MenuItem("Hide")
            hide.connect("activate", self.hide_main_window)
            menu.append(hide)
            self.hide = 1
        menu.show_all()
        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)
