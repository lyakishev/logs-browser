import gtk


class Toolbar(gtk.Toolbar):
    def __init__(self, *args, **kw):
        gtk.Toolbar.__init__(self, *args, **kw)
        self.pos = 0

    def next_pos(self):
        pos = self.pos
        self.pos += 1
        return pos

    def append_button(self, icon, callback, label=""):
        btn = gtk.ToolButton(icon)
        btn.connect("clicked", callback)
        if label:
            btn.set_is_important(True)
            btn.set_label(label)
        self.insert(btn, self.next_pos())
        return btn

    def append_togglebutton(self, icon, callback, label=""):
        btn = gtk.ToggleToolButton(icon)
        btn.connect("toggled", callback)
        if label:
            btn.set_is_important(True)
            btn.set_label(label)
        self.insert(btn, self.next_pos())
        return btn

    def append_item(self, item):
        toolitem = gtk.ToolItem()
        toolitem.add(item)
        self.insert(toolitem, self.next_pos())
        return toolitem

    def append_sep(self):
        sep = gtk.SeparatorToolItem()
        self.insert(sep, self.next_pos())

