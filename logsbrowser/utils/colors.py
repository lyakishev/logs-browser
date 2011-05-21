import gtk

class ColorError(Exception): pass

def check_color(color_value):
    try:
        gtk.gdk.color_parse(color_value)
    except ValueError:
        return False
    else:
        return True

def c_to_string(color_value):
    color = gtk.gdk.color_parse(color_value)
    return color.to_string()
    

