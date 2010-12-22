import pygtk
pygtk.require("2.0")
import gtk, gobject, gio

class LogWindow:
    def __init__(self, txt):
        self.popup = gtk.Window()
        self.popup.set_title("Log")
        self.popup.set_default_size(640,480)
        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.popup_frame = gtk.Frame("Log")
        self.log_text = gtk.TextView()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_WORD)
        self.log_text.get_buffer().set_text(txt.replace("><",">\n<"))
        self.popup_frame.add(self.scr)
        self.scr.add(self.log_text)
        self.popup.add(self.popup_frame)
        self.popup.show_all()
