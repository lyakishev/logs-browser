import gtk

class PanedBox(gtk.VBox):
    def __init__(self, show_all_func, pos=500):
        gtk.VBox.__init__(self)
        self.paned = gtk.VPaned()
        self.pos = pos
        self.top_widget = None
        self.bottom_widget = None
        self.show_all = show_all_func

    def pack_start(self, *args, **kw):
        gtk.VBox.pack_start(self, *args, **kw)
        self.top_widget = args[0]

    def paned_pack(self, widget):
        self.bottom_widget = widget

    def box_to_paned(self):
        self.remove(self.top_widget)
        self.paned.pack1(self.top_widget, True, False)
        self.paned.pack2(self.bottom_widget, False, False)
        self.paned.set_position(self.pos)
        self.pack_end(self.paned)

    def paned_to_box(self):
        self.paned.remove(self.top_widget)
        self.paned.remove(self.bottom_widget)
        self.remove(self.paned)
        self.pack_end(self.top_widget)

    def change_box(self, paned):
        if paned:
            self.box_to_paned()
        else:
            self.paned_to_box()
        self.show_all()
