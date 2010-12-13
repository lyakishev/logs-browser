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

    def parse_like_entry(self):
        strng = self.like_entry.get_text()
            def parse(token):
                if token in ["AND", "OR", "NOT"]:
                    return t.lower()
                elif token in [")","("]:
                    return token
                elif not token:
                    return token
                else:
                    return "'"+t.strip()+"'"+" in l['msg']"
        if_expr = ' '.join([parse(t) for t in re.split("(AND|OR|NOT|\)|\()",\
            strng)])
        return if_expr

    def get_cont(self):
        return (self.parse_like_entry(),self.notlike_entry.get_text())

