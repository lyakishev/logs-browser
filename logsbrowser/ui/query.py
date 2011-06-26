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
        self.query_model = gtk.ListStore(str,  #up
                                         str,  #down
                                         str,  #column
                                         str,  #color
                                         str,  #color
                                         str)  #value        

        self.field_model = gtk.ListStore(str)

        for c in ["---", "log", "logname", "type", "computer", "source", "event",
                  "date", "$time", "lid"]:
            self.field_model.append([c])

        self.fields = {}
        self.fields['UP'] = 0
        self.fields['DOWN'] = 1
        self.fields['COLOR'] = 2
        self.fields['HCOLORV'] = 5
        self.fields['FIELD'] = 3
        self.fields['WHERE'] = 4

        up_renderer = gtk.CellRendererPixbuf()
        down_renderer = gtk.CellRendererPixbuf()
        self.up_column = gtk.TreeViewColumn("", up_renderer,
                stock_id=self.fields['UP'])
        self.down_column = gtk.TreeViewColumn("", down_renderer,
                stock_id=self.fields['DOWN'])

        color_renderer = gtk.CellRendererText()
        color_renderer.set_property("editable", False)
        self.color_column = gtk.TreeViewColumn("color", color_renderer,
                                                text=self.fields['COLOR'],
                                                cell_background=self.fields['HCOLORV'])

        field_renderer = gtk.CellRendererCombo()
        field_renderer.set_property("model", self.field_model)
        field_renderer.set_property('text-column', 0)
        field_renderer.set_property('editable', True)
        field_renderer.set_property('has-entry', True)
        field_renderer.connect("changed", self.change_func, self.fields['FIELD'])
        field_column = gtk.TreeViewColumn("column", field_renderer,
                                                    text=self.fields['FIELD'])

        
        where_renderer = gtk.CellRendererText()
        where_renderer.set_property('editable',True)
        where_renderer.connect("edited", self.change_value,
                                         self.fields['WHERE'])
        where_renderer.connect("editing-started", self.set_cell_entry_signal,
                                                  self.fields['WHERE'])
        self.where_column = gtk.TreeViewColumn("where", where_renderer,
                                                text=self.fields['WHERE'])
        
        hidden_colorr = gtk.CellRendererText()
        hidden_colorr.set_property('editable',True)
        hidden_color = gtk.TreeViewColumn("value", hidden_colorr,
                                                text=self.fields['HCOLORV'])
        hidden_color.set_visible(False)

        self.view = gtk.TreeView()
        self.view.append_column(self.up_column)
        self.view.append_column(self.down_column)
        self.view.append_column(self.color_column)
        self.view.append_column(field_column)
        self.view.append_column(self.where_column)
        self.view.append_column(hidden_color)

        #self.view.set_property("enable-grid-lines", True)
        self.view.set_model(self.query_model)
        self.view.connect("cursor-changed", self.add_row)
        self.view.connect("key-press-event", self.delete_row)
        self.view.connect("button-press-event", self.activate_cell)

    def unselect(self):
        path, focus_column = self.view.get_cursor()
        if path:
            self.view.get_selection().unselect_path(path)

    def focus_out(self, entry, event, path, col):
        iter_ = self.query_model.get_iter_from_string(path)
        self.query_model.set_value(iter_, col, entry.get_text())

    def set_cell_entry_signal(self, cell, entry, num, col):
        entry.connect("focus-out-event", self.focus_out, num, col)

    def activate_cell(self, view, event):
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            if path[1] == self.color_column:
                colordlg = gtk.ColorSelectionDialog("Select color")
                colorsel = colordlg.colorsel
                colorsel.set_has_palette(True)
                response = colordlg.run()
                if response == gtk.RESPONSE_OK:
                    col = colorsel.get_current_color()
                    view.get_model()[path[0]][self.fields['HCOLORV']]=col
                colordlg.destroy()
            view.set_cursor(path[0], focus_column = path[1], start_editing=True)
            if path[1] == self.up_column:
                self.loglist.up_color(view.get_model()[path[0]][self.fields['HCOLORV']])
            elif path[1] == self.down_column:
                self.loglist.down_color(view.get_model()[path[0]][self.fields['HCOLORV']])
        elif event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            if path[1] == self.color_column:
                view.get_model()[path[0]][self.fields['HCOLORV']] = '#fff'

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
                self.query_model[c-1][self.fields['FIELD']] = 'log'
                self.query_model.append([gtk.STOCK_GO_UP, gtk.STOCK_GO_DOWN, '', '', '','#fff'])
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
            self.query_model.append([gtk.STOCK_GO_UP, gtk.STOCK_GO_DOWN,'',row[0], row[2], row[1]])
        self.query_model.append([gtk.STOCK_GO_UP, gtk.STOCK_GO_DOWN, '','', '', '#fff'])

    def get_filter(self, only_colors):
        
        fts = self.loglist.fts

        FIELD = self.fields['FIELD']
        WHERE = self.fields['WHERE']
        COLOR = self.fields['HCOLORV']

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
        only_color_fields = []
        for r in self.query_model:
            if r[FIELD] and r[WHERE]:
                if r[FIELD] == '---':
                    form = '(%s)' % r[WHERE]
                else:
                    form = '%s %s' % (r[FIELD], check_clause(r[WHERE]))
                if r[COLOR] == '#fff':
                    if not only_colors:
                        clauses.append(form)
                else:
                    fields.append('{%s as %s}' % (form, r[COLOR]))
                    if only_colors:
                        only_color_fields.append(form)

        if clauses or fields or only_color_fields:
            fields.append('*')
            sql = "(select %s from $table " % ','.join(fields)
            if clauses:
                sql += 'where %s' % ' AND '.join(clauses)
            elif only_color_fields:
                sql += 'where %s' % ' OR '.join(only_color_fields)
            sql += ')'
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

    def get_filter(self, only_colors):
        return self.query.get_filter(only_colors)

    def get_sql(self, only_colors):
        return (self.get_query(), self.get_filter(only_colors))


class QueryLoader(gtk.VBox):
    def __init__(self, query_constructor, qmanager):
        gtk.VBox.__init__(self)
        self.query_constructor = query_constructor
        self.tools = gtk.HBox()
        self.add_lid = gtk.CheckButton('auto__lid')
        self.add_lid.set_active(True)
        self.queries_combo = gtk.HBox()
        self.filters_label = gtk.Label()
        self.filters_label.set_markup('<b>Filter</b>')
        self.only_colors = gtk.CheckButton('only colors')
        self.only_colors.set_active(False)
        self.filters = gtk.combo_box_new_text()
        self.filters.connect("changed", self.set_filter)
        self.queries_label = gtk.Label()
        self.queries_label.set_markup('<b>Query</b>')
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
        self.queries_combo.pack_start(self.only_colors, False, False)
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

    def get_query(self):
        return self.query_constructor.get_sql(self.get_only_colors())
        
    def get_auto_lid(self):
        return self.add_lid.get_active()

    def get_only_colors(self):
        return self.only_colors.get_active()

        



       

       
    

