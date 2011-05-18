import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango
import re
import config


class Filter():
    def __init__(self, plain, loglist):
        self.loglist = loglist
        self.plain = plain
        self.query_model = gtk.ListStore(str,  #column
                                         str,  #color
                                         str,  #color
                                         str)  #value        

        self.field_model = gtk.ListStore(str)

        for c in ["---", "log", "logname", "type", "computer", "source", "event",
                  "date", "time", "lid"]:
            self.field_model.append([c])

        field_renderer = gtk.CellRendererCombo()
        field_renderer.set_property("model", self.field_model)
        field_renderer.set_property('text-column', 0)
        field_renderer.set_property('editable', True)
        field_renderer.set_property('has-entry', True)
        field_renderer.connect("changed", self.change_func, 0)
        field_column = gtk.TreeViewColumn("column", field_renderer, text=0)

        color_renderer = gtk.CellRendererText()
        color_renderer.set_property("editable", False)
        self.color_column = gtk.TreeViewColumn("color", color_renderer,
                                                text=1, cell_background=3)
        
        where_renderer = gtk.CellRendererText()
        where_renderer.set_property('editable',True)
        where_renderer.connect("edited", self.change_value, 2)
        where_renderer.connect("editing-started", self.set_cell_entry_signal)
        self.where_column = gtk.TreeViewColumn("where", where_renderer,
                                                text=2)
        
        hidden_colorr = gtk.CellRendererText()
        hidden_colorr.set_property('editable',True)
        hidden_color = gtk.TreeViewColumn("value", hidden_colorr,
                                                text=3)
        hidden_color.set_visible(False)

        self.view = gtk.TreeView()
        self.view.append_column(field_column)
        self.view.append_column(self.color_column)
        self.view.append_column(self.where_column)
        self.view.append_column(hidden_color)

        #self.view.set_property("enable-grid-lines", True)
        self.view.set_model(self.query_model)
        self.view.connect("cursor-changed", self.add_row)
        self.view.connect("key-press-event", self.delete_row)
        self.view.connect("button-press-event", self.activate_cell)
        self.entry_path = None

    def unselect(self):
        path, focus_column = self.view.get_cursor()
        if path:
            self.view.get_selection().unselect_path(path)

    def focus_out(self, *args):
        if self.entry_path:
            self.query_model[self.entry_path][2] = self.cell_entry_text
            self.cell_entry_text = ""

    def set_cell_entry_signal(self, cell, entry, num):
        self.cell_entry_text = entry.get_text()
        entry.connect("changed", self.save_cell_text)
        entry.connect("focus-out-event", self.focus_out)

    def save_cell_text(self, entry):
        self.cell_entry_text = entry.get_text()

    def activate_cell(self, view, event):
        old_path, old_col = view.get_cursor()
        if old_path:
            try:
                if self.cell_entry_text:
                    self.query_model[old_path][2] = self.cell_entry_text
            except AttributeError:
                pass
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            if path[1] == self.color_column:
                colordlg = gtk.ColorSelectionDialog("Select color")
                colorsel = colordlg.colorsel
                colorsel.set_has_palette(True)
                response = colordlg.run()
                if response == gtk.RESPONSE_OK:
                    col = colorsel.get_current_color()
                    view.get_model()[path[0]][3]=col
                colordlg.destroy()
            view.set_cursor(path[0], focus_column = path[1], start_editing=True)
            if path[1] == self.where_column:
                self.entry_path = path[0]
        elif event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            if path[1] == self.color_column:
                view.get_model()[path[0]][3] = '#fff'
            if path[1] == self.where_column:
                self.entry_path = path[0]
            

    def change_func(self, combo, path, iter_, col):
        self.query_model[path][col] = combo.get_property("model").get_value(iter_,0)

    def change_value(self, cell, path, new_text, col):
        self.query_model[path][col] = new_text

    def add_row(self, view):
        selection = view.get_selection()
        (model, iter_) = selection.get_selected()
        try:
            if not model.iter_next(iter_):
                c = len(self.query_model)
                self.query_model[c-1][0] = 'log'
                self.query_model.append(['', '', '','#fff'])
        except TypeError:
            pass

    def delete_row(self, view, event):
        if event.keyval == 65535:
            selection = view.get_selection()
            (model, iter_) = selection.get_selected()
            if iter_ is not None and model.iter_next(iter_):
                model.remove(iter_)

    def set_filter(self, rows):
        self.query_model.clear()
        for row in rows:
            self.query_model.append([row[0],'', row[2], row[1]])
        self.query_model.append(['','', '', '#fff'])

    def get_filter(self):
        
        fts = self.loglist.fts

        def check_clause(clause):
            words = len(clause.split())
            if words > 1 and clause.count("'")>1:
                return clause
            else:
                if fts:
                    return ("%s '%s'" %
                            (config.DEFAULT_WHERE_OPERATOR_FTS.upper(),
                                        clause))
                else:
                    return "%s '%s'" % (config.DEFAULT_WHERE_OPERATOR.upper(),
                                        clause)
        fields = []
        clauses = []
        for r in self.query_model:
            if r[0] and r[2]:
                if r[0] == '---':
                    form = '%s' % r[2]
                else:
                    form = '%s %s' % (r[0], check_clause(r[2]))
                if r[3] == '#fff':
                    clauses.append(form)
                else:
                    fields.append('{%s as %s}' % (form, r[3]))

        if clauses or fields:
            fields.append('*')
            sql = "(select %s from $table %s)" % (','.join(fields),
                        ('where %s' % ' AND '.join(clauses)) if clauses else '')
        else:
            sql = '$table'
        return sql

class Plain(gtk.ScrolledWindow):
    def __init__(self):
        super(Plain, self).__init__()
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.txt = gtk.TextView()
        self.buf = self.txt.get_buffer()
        self.add(self.txt)
        self.sens_list = [self.txt]
        self.show_all()

    def set_text(self, txt):
        self.buf.set_text(txt)

    def set_sql(self, txt):
        self.set_text(txt)

    def get_text(self):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        txt = self.buf.get_text(start, end)
        return txt

    def get_sql(self):
        return self.get_text()


class Query(gtk.Notebook):
    def __init__(self, loglist):
        super(Query, self).__init__()
        scroll_query = gtk.ScrolledWindow()
        scroll_query.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        self.plain = Plain()
        plain_query_label = gtk.Label("Query")

        self.query = Filter(self.plain, loglist)
        scroll_query.add(self.query.view)
        
        query_label = gtk.Label("Filter")

        self.append_page(scroll_query, query_label)
        self.append_page(self.plain, plain_query_label)

        self.sens_list = [self.plain, self.query.view]

        self.show_all()

        self.set_current_page(0)

    def unselect(self):
        self.query.unselect()

    def set_query(self, txt):
        self.plain.set_sql(txt)

    def set_filter(self, rows):
        self.query.set_filter(rows)

    def get_query(self):
        return self.plain.get_text()

    def get_filter(self):
        return self.query.get_filter()

    def get_sql(self):
        return (self.get_query(), self.get_filter())


class QueryLoader(gtk.VBox):
    def __init__(self, query_constructor, qmanager):
        gtk.VBox.__init__(self)
        self.query_constructor = query_constructor
        self.tools = gtk.HBox()
        self.add_lid = gtk.CheckButton('auto__lid')
        self.add_lid.set_active(True)
        self.queries_combo = gtk.HBox()
        self.filters_label = gtk.Label('Filter')
        self.filters = gtk.combo_box_new_text()
        self.filters.connect("changed", self.set_filter)
        self.queries_label = gtk.Label('Query')
        self.queries = gtk.combo_box_new_text()
        self.queries.connect("changed", self.set_query)
        self.query_manager = qmanager
        for n,q in enumerate(self.query_manager.queries):
            self.queries.append_text(q)
            if q == self.query_manager.default_query:
                self.queries.set_active(n)
        for n,q in enumerate(self.query_manager.filters):
            self.filters.append_text(q)
            if q == self.query_manager.default_filter:
                self.filters.set_active(n)
        self.queries_combo.pack_start(self.filters_label, False, False, 5)
        self.queries_combo.pack_start(self.filters, True, True)
        self.queries_combo.pack_start(self.queries_label, False, False, 5)
        self.queries_combo.pack_start(self.queries, True, True)
        self.tools.pack_start(self.queries_combo)
        self.tools.pack_start(self.add_lid, False,False, 10)
        self.pack_start(self.tools, False, False)
        self.pack_start(self.query_constructor)
        self.show_all()

    def set_query(self, *args):
        query = self.queries.get_active_text().decode('utf8')
        self.query_constructor.set_query(self.query_manager.queries[query].strip())

    def set_filter(self, *args):
        query = self.filters.get_active_text().decode('utf8')
        self.query_constructor.set_filter(self.query_manager.filters[query])
        
    def get_auto_lid(self):
        return self.add_lid.get_active()

        



       

       
    

