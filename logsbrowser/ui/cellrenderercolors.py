# LogsBrowser is program for find and analyze logs.
# Copyright (C) <2010-2011>  <Lyakishev Andrey (lyakav@gmail.com)>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import gtk
import pango
import cairo
import gobject
from itertools import cycle
import config


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

    def do_get_size(self, widget, cell_area):
        x, y, w, h = gtk.CellRendererText.do_get_size(self, widget, cell_area)
        return (x, y, int(w*pango.SCALE_LARGE) if config.BOLD_SELECTED else w, h)

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
        colors = self.get_property('backgrounds')
        if (colors and (not bool(flags & gtk.CELL_RENDERER_SELECTED) or
                        config.BOLD_SELECTED)):
            cairo_context = window.cairo_create()
            x = background_area.x
            y = background_area.y
            w = background_area.width
            h = background_area.height
            gdk_colors = [gtk.gdk.color_parse(c) for c in colors.split()]
            self.render_rect(cairo_context, x, y, w, h, gdk_colors)
            if (bool(flags & gtk.CELL_RENDERER_SELECTED) and config.BOLD_SELECTED):
                context = widget.get_pango_context()
                layout = pango.Layout(context)
                layout.set_text(self.get_property('text'))
                layout.set_font_description(pango.FontDescription("bold"))
                widget.style.paint_layout(window, gtk.STATE_NORMAL, True,
                                          None, widget, '',
                                          background_area.x, background_area.y+h/4-1,
                                          layout)
                return
        gtk.CellRendererText.do_render(self, window, widget, background_area, cell_area,
                                       expose_area, flags)

    def get_cairo_color(self, color):
        ncolor = color/65535.0
        return ncolor

    def render_rect(self, cr, x, y, w, h, colors):
        icolors = cycle(colors)
        width = config.COLOR_RECT_WIDTH
        y0 = y
        y1 = y+h
        x0 = x
        x1 = x0 + w
        while x0 <= x1:
            c = icolors.next()
            cr.set_source_rgb(*map(lambda x: self.get_cairo_color(x),
                                   [c.red, c.green, c.blue]))
            cr.move_to(x0, y0)
            cr.line_to(x0+width+1, y0)
            cr.line_to(x0, y1)
            if x0 != x:
                cr.line_to(x0-width-1, y1)
            cr.close_path()
            cr.fill()
            cr.stroke()
            x0 = x0+width
        c = icolors.next()
        cr.set_source_rgb(*map(lambda x: self.get_cairo_color(x),
                               [c.red, c.green, c.blue]))
        cr.move_to(x0, y0)
        cr.line_to(x0, y1)
        cr.line_to(x0-width-1, y1)
        cr.close_path()
        cr.fill()
        cr.stroke()


gobject.type_register(CellRendererColors)
