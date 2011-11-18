import gtk

class Button(gtk.Button):
    def __init__(self, stock, size):
        gtk.Button.__init__(self)
        image = gtk.Image()
        image.set_from_stock(stock, size)
        self.add(image)
