import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
try:
    from mouse_click import DetectClick
except:
    pass
from multiprocessing import Value
from net_time import GetTrueTime


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
        self.active = True

    def change_mode(self, *args):
        now = GetTrueTime()
        if self.record:
            self.statusicon.set_from_stock(gtk.STOCK_YES)
            self.date_filter.fromto_option.to_date.set_date(now)
            self.record = 0
        else:
            self.statusicon.set_from_stock(gtk.STOCK_NO)
            if self.active:
                ct = Value('d', 0.0)
                p = DetectClick(ct)
                p.start()
                p.join()
                self.date_filter.fromto_option.from_date.set_date(ct.value)
            else:
                self.date_filter.fromto_option.from_date.set_date(now)
            self.record = 1

    def hide_main_window(self, *args):
        self.window.hide()

    def show_main_window(self, *args):
        self.window.show()

    def change_time_mode(self, check):
        if not check.active:
            self.active = False
        else:
            self.active = True
        print self.active

    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()
        time_mode = gtk.CheckMenuItem("First-click mode")
        time_mode.set_active(self.active)
        time_mode.connect('toggled', self.change_time_mode)
        menu.append(time_mode)
        menu.show_all()
        menu.show_all()
        menu.popup(None, None, gtk.status_icon_position_menu,
                   button, time, self.statusicon)
