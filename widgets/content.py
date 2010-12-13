import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from common_filter import CommonFilter

class ContentFilter(CommonFilter):
    def __init__(self):
        super(ContentFilter, self).__init__("Contains")
        self.like_entry = gtk.Entry()
        self.notlike_entry = gtk.Entry()
        self.like_label = gtk.Label('Like')
        self.notlike_label = gtk.Label('Not like')
        self.content_table = gtk.Table(2,2,False)
        self.content_table.attach(self.like_label,0,1,0,1, xoptions=0, yoptions=0)
        self.content_table.attach(self.notlike_label,0,1,1,2, xoptions=0, yoptions=0)
        self.content_table.attach(self.like_entry,1,2,0,1)
        self.content_table.attach(self.notlike_entry,1,2,1,2)
        self.add(content_table)
