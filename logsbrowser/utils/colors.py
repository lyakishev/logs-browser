import gtk

class ColorError(Exception): pass

def check_color(color_value):
    try:
        gtk.gdk.color_parse(color_value)
    except ValueError:
        return False
    else:
        return True

