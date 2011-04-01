import gtk
import pango
import cairo
import gobject
from itertools import cycle


class CellRendererColors(gtk.CellRendererText):
    __gproperties__ = {
                    'backgrounds': (gobject.TYPE_STRING,
                            'Backgrounds of the cell',
                            'The backgrounds of the cell',
                            '#FFFFFF',
                            gobject.PARAM_READWRITE
                            )
                    }
    def __init__(self):
        self.__gobject_init__()
        gtk.CellRendererText.__init__(self)
        self.bgcolors = ""

    def do_set_property(self, pspec, value):
        if pspec.name == 'backgrounds':
            self.bgcolors = value
        else:
            setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        if pspec.name == 'backgrounds':
            return self.bgcolors
        return getattr(self, pspec.name)

    def do_render(self, window, widget, background_area, cell_area,
                    expose_area, flags):
        cairo_context = window.cairo_create()
        x = background_area.x
        y = background_area.y
        w = background_area.width
        h = background_area.height

        colors = self.get_property('backgrounds')
        if colors and not bool(flags & gtk.CELL_RENDERER_SELECTED):
            gdk_colors = [gtk.gdk.color_parse(c) for c in colors.split()]
            self.render_rect(cairo_context, x, y, w, h, gdk_colors)
            context = widget.get_pango_context()
            layout = pango.Layout(context)
            layout.set_text(self.get_property('text'))
            layout.set_width(cell_area.width * pango.SCALE)
            widget.style.paint_layout(window, gtk.STATE_NORMAL, True,
                                    background_area, widget, 'footext',
                                    background_area.x, background_area.y,
                                    layout)

        else:
            gtk.CellRendererText.do_render(self, window, widget, background_area, cell_area,
                    expose_area, flags)

    def get_cairo_color(self, color):
            ncolor = color/65535.0
            return ncolor


    def render_rect(self, cr, x, y, w, h, colors):
        icolors = cycle(colors)
        width = 20
        y0 = y
        y1 = y+h
        x0 = x
        x1 = x0 + w
        while x0 <= x1:
            c = icolors.next()
            cr.set_source_rgb(*map(lambda x: self.get_cairo_color(x),
                                    [c.red,c.green,c.blue]))
            cr.move_to(x0, y0)
            cr.line_to(x0+width+1, y0)
            cr.line_to(x0, y1)
            if x0 != x:
                cr.line_to(x0-width-1, y1)
            cr.close_path()
            cr.fill()
            cr.stroke()
            x0=x0+width
        c = icolors.next()
        cr.set_source_rgb(*map(lambda x: self.get_cairo_color(x),
                                [c.red,c.green,c.blue]))
        cr.move_to(x0, y0)
        cr.line_to(x0, y1)
        cr.line_to(x0-width-1, y1)
        cr.close_path()
        cr.fill()
        cr.stroke()


gobject.type_register(CellRendererColors)

