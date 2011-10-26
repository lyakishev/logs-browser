import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango
import re
import config
import pango
import db
#from utils.profiler import profile


class Filter():

    operators = db.functions.operators
   
    def __init__(self, plain, loglist):
        self.loglist = loglist
        self.plain = plain
        self.query_model = gtk.ListStore(str,  #up
                                         str,  #down
                                         str,  #color
                                         str,  #column
                                         str, #NOT
                                         str,  #operator
                                         str,  #clause
                                         str)  #color

        self.operator_model = gtk.ListStore(str)
        self.field_model = gtk.ListStore(str)

        for c in ["---", "log", "logname", "type", "computer", "source", "event",
                  "date", "$time", "lid"]:
            self.field_model.append([c])

        for c in self.operators.keys():
            self.operator_model.append([c])

        self.fields = {}
        self.fields['UP'] = 0
        self.fields['DOWN'] = 1
        self.fields['COLOR'] = 2
        self.fields['HCOLORV'] = 7
        self.fields['NOT'] = 4
        self.fields['OPERATOR'] = 5
        self.fields['FIELD'] = 3
        self.fields['WHERE'] = 6

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

        not_renderer = gtk.CellRendererText()
        not_renderer.set_property("editable", False)
        not_renderer.set_property('xalign', 1.0)
        font = pango.FontDescription('italic')
        not_renderer.set_property('font-desc', font)
        self.not_column = gtk.TreeViewColumn("no", not_renderer,
                                                text=self.fields['NOT'])

        operator_renderer = gtk.CellRendererCombo()
        operator_renderer.set_property("model", self.operator_model)
        operator_renderer.set_property('text-column', 0)
        operator_renderer.set_property('editable', True)
        operator_renderer.set_property('has-entry', True)
        font = pango.FontDescription('italic')
        operator_renderer.set_property('font-desc', font)
        operator_renderer.connect("changed", self.change_func, self.fields['OPERATOR'])
        operator_column = gtk.TreeViewColumn("operator", operator_renderer,
                                                    text=self.fields['OPERATOR'])
        
        where_renderer = gtk.CellRendererText()
        where_renderer.set_property('editable',True)
        where_renderer.connect("edited", self.change_value,
                                         self.fields['WHERE'])
        where_renderer.connect("editing-started", self.set_cell_entry_signal,
                                                  self.fields['WHERE'])
        self.where_column = gtk.TreeViewColumn("clause", where_renderer,
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
        self.view.append_column(self.not_column)
        self.view.append_column(operator_column)
        self.view.append_column(self.where_column)
        self.view.append_column(hidden_color)

        self.view.set_property("enable-grid-lines", True)
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
            if path:
                if path[1] == self.not_column:
                    row = view.get_model()[path[0]]
                    operator = row[self.fields['OPERATOR']]
                    if operator == ">":
                        view.get_model()[path[0]][self.fields['OPERATOR']] = '<'
                    elif operator == "<":
                        view.get_model()[path[0]][self.fields['OPERATOR']] = '>'
                    try:
                        no = self.operators[operator]
                    except KeyError:
                        return
                    val = row[self.fields['NOT']]
                    if val == no:
                        row[self.fields['NOT']] = ' '
                    else:
                        row[self.fields['NOT']] = no
                    return
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
            if path:
                if path[1] == self.color_column:
                    view.get_model()[path[0]][self.fields['HCOLORV']] = '#fff'

    def change_func(self, combo, path, iter_, col):
        new_value = combo.get_property("model").get_value(iter_,0)
        if col == self.fields['FIELD']:
            if new_value == '---':
                self.query_model[path][self.fields['OPERATOR']] = '---'
                self.query_model[path][self.fields['NOT']] = ' '
            else:
                if hasattr(self, 'default_operator'):
                    new_operator = self.default_operator(new_value)
                    if new_operator:
                        self.query_model[path][self.fields['OPERATOR']] = new_operator
                        self.query_model[path][self.fields['NOT']] = ' '
        if col == self.fields['OPERATOR']:
            self.query_model[path][self.fields['NOT']] = ' '
        self.query_model[path][col] = new_value

    def change_value(self, cell, path, new_text, col):
        self.query_model[path][col] = new_text

    def add_row(self, view):
        selection = view.get_selection()
        (model, iter_) = selection.get_selected()
        try:
            if not model.iter_next(iter_):
                c = len(self.query_model)
                self.query_model[c-1][self.fields['FIELD']] = 'log'
                self.query_model[c-1][self.fields['OPERATOR']] = self.default_operator('log') or '---'
                self.query_model.append([gtk.STOCK_GO_UP, gtk.STOCK_GO_DOWN, '', '', ' ', '', '','#fff'])
        except TypeError:
            pass

    def delete_row(self, view, event):
        if event.keyval == 65535:
            selection = view.get_selection()
            (model, iter_) = selection.get_selected()
            if iter_ is not None and model.iter_next(iter_):
                model.remove(iter_)

    def get_filter_table(self):
        rows = []
        for row in list(self.query_model)[:-1]:
            rows.append((row[self.fields['FIELD']], row[self.fields['HCOLORV']],
                        row[self.fields['WHERE']]))
        return rows

    def set_filter(self, rows):
        self.query_model.clear()
        for row in rows:
            self.query_model.append([gtk.STOCK_GO_UP, gtk.STOCK_GO_DOWN,
                        '',row[0], ' ', self.default_operator(row[0]) or '---', row[2], row[1]])
        self.query_model.append([gtk.STOCK_GO_UP, gtk.STOCK_GO_DOWN, '','', ' ','','', '#fff'])

    def get_filter(self, only_colors):

        ops_funcs = db.functions.operator_functions
        
        fts = self.loglist.fts

        FIELD = self.fields['FIELD']
        WHERE = self.fields['WHERE']
        COLOR = self.fields['HCOLORV']
        OPERATOR = self.fields['OPERATOR']
        NOT = self.fields['NOT']

        def check_clause(field, not_, operator, clause):
            #words = len(clause.split())
            #if words > 1 and clause.count("'")>1:
            #    return clause
            #else:
            if operator in ops_funcs:
                if not_ == self.operators[operator]:
                    return ("%s(%s, '%s')" % (ops_funcs[operator][1], field, clause))
                else:
                    return ("%s(%s, '%s')" % (ops_funcs[operator][0], field, clause))
            else:
                return ("%s %s%s '%s'" % (field, not_+(' ' if not_ != '!' else '') ,operator, clause))
                #if fts:
                #    return ("%s '%s'" % (not_ ,operator, clause))
                #else:
                #    return ("%s '%s'" % (not_ ,operator, clause))

        fields = []
        clauses = []
        only_color_fields = []
        for r in self.query_model:
            if r[FIELD] and r[WHERE]:
                if r[FIELD] == '---':
                    form = '(%s)' % r[WHERE]
                else:
                    form = '%s' % check_clause(r[FIELD], r[NOT], r[OPERATOR], r[WHERE])
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

        self.only_colors = gtk.CheckButton('only colors')
        self.only_colors.set_active(False)
        self.only_colors.show()


        self.plain = Plain()
        plain_query_label = gtk.Label("Query")

        self.query = Filter(self.plain, loglist)
        scroll_query.add(self.query.view)
        
        query_label = gtk.Label("Filter")

        self.append_page(scroll_query, query_label)
        self.append_page(self.plain, plain_query_label)

        self.sens_list = [self.plain, self.query.view]
        self.set_action_widget(self.only_colors, gtk.PACK_END)
        self.show_all()
        self.set_current_page(0)

    def get_only_colors(self):
        return self.only_colors.get_active()

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


class FromCombo(gtk.ComboBox):
    def __init__(self):
        super(FromCombo, self).__init__()
        self.names = []
        self.model = gtk.ListStore(str)
        self.set_model(self.model)
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.show_all()

    def update(self, operation, names, current):
        if operation == 'add':
            self.add(names, current)
        elif operation == 'rename':
            self.rename(names, current)
        elif operation == 'delete':
            self.delete(names, current)

    def get_active_name(self):
        iter_ = self.get_active_iter()
        if not iter_:
            return None
        return self.model.get_value(iter_, 0)

    def set_active_name(self, name):
        iter_ = self.model.get_iter_first()
        while iter_:
            if self.model.get_value(iter_, 0) == name:
                self.set_active_iter(iter_)
                return
            iter_ = self.model.iter_next(iter_)


    def add(self, names, current):
        for new_page in [n for n in names if n not in self.names]:
            self.model.append([new_page])
        if not self.get_active_name():
            self.set_active_name(current)
        self.names = names[:]

    def rename(self, names, current):
        try:
            old_page = [n for n in self.names if n not in names][0]
        except IndexError:
            return
        new_page = [n for n in names if n not in self.names][0]
        self.model.append([new_page])
        if old_page == self.get_active_name():
            self.set_active_name(new_page)
        self.model.remove(self.get_iter_by_text(old_page))
        self.names = names[:]

    def delete(self, names, current):
        deleted_page = [n for n in self.names if n not in names][0]
        if deleted_page == self.get_active_name():
            self.set_active_name(current)
        self.model.remove(self.get_iter_by_text(deleted_page))
        self.names = names[:]
    
    def get_iter_by_text(self, name):
        iter_ = self.model.get_iter_first()
        while iter_:
            if self.model.get_value(iter_, 0) == name:
                return iter_
            iter_ = self.model.iter_next(iter_)

class QueryLoader(gtk.VBox):
    def __init__(self, query_constructor, qmanager, notify_func):
        gtk.VBox.__init__(self)
        self.current = None
        self.froms = []
        self.notify_all = notify_func
        self.query_constructor = query_constructor
        self.query_constructor.query.default_operator = qmanager.default_operator
        self.tools = gtk.HBox()
        self.queries_combo = gtk.HBox()
        self.filters_label = gtk.Label()
        self.filters_label.set_markup('<b>Filter</b>')
        self.filters = gtk.combo_box_new_text()
        self.queries_label = gtk.Label()
        self.queries_label.set_markup('<b>Query</b>')
        self.queries = gtk.combo_box_new_text()
        self.query_manager = qmanager
        self.queries.connect("changed", self.set_query)
        self.filters.connect("changed", self.set_filter)
        self.update_queries_combo()
        self.update_filters_combo()
        self.filters.connect("notify::popup-shown", self._update_fcombo)

        advanced_btn = gtk.ToggleButton()
        advanced_btn.set_relief(gtk.RELIEF_NONE)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_SMALL_TOOLBAR)
        advanced_btn.add(image)
        advanced_btn.connect('toggled', self.show_advanced)

        self.froms_combo = FromCombo()
        self.from_ = gtk.Label()
        self.from_.set_markup("<b>From</b>")
        self.froms_box = gtk.HBox()
        self.froms_box.pack_start(self.from_, False, False, 5)
        self.froms_box.pack_start(self.froms_combo, False, False)

        self.add_lid = gtk.CheckButton('auto__lid')
        self.add_lid.set_active(True)

        self.advanced_box = gtk.HButtonBox()
        self.advanced_box.set_layout(gtk.BUTTONBOX_EDGE)
        self.advanced_box.pack_start(self.froms_box)
        self.advanced_box.pack_start(self.add_lid)

        self.queries_combo.pack_start(self.filters_label, False, False, 5)
        self.queries_combo.pack_start(self.filters, False, True)
        self.queries_combo.pack_start(self.queries_label, False, False, 5)
        self.queries_combo.pack_start(self.queries, True, True)
        self.queries_combo.pack_start(advanced_btn, False, False)
        self.tools.pack_start(self.queries_combo)
        self.pack_start(self.tools, False, False)
        self.pack_start(self.query_constructor, True, True)
        self.show_all()

    def get_from(self):
        return self.froms_combo.get_active_name()

    def show_advanced(self, btn):
        if btn.get_active():
            self.pack_start(self.advanced_box, False, False, 1)
        else:
            self.remove(self.advanced_box)
        self.show_all()

    def update_queries_combo(self, set_def=True):
        for n,q in enumerate(self.query_manager.queries):
            self.queries.append_text(q)
            if q == self.query_manager.default_query and set_def:
                self.queries.set_active(n)

    def update_filters_combo(self, set_def=True):
        filters = [t[0] for t in self.filters.get_model()]
        for n,q in enumerate(self.query_manager.filters):
            if q not in filters:
                self.filters.append_text(q)
                if q == self.query_manager.default_filter and set_def:
                    self.filters.set_active(n)
            else:
                filters.remove(q)
        if filters:
            model = self.filters.get_model()
            next_ = model.get_iter_first()
            while next_:
                if model.get_value(next_, 0) in filters:
                    model.remove(next_)
                next_ = model.iter_next(next_)

    def _update_fcombo(self, combo, popup):
        if combo.get_property('popup-shown'):
            self.current = self.query_constructor.query.get_filter_table()
            self.update_filters_combo(False)
            self.filters.prepend_text("###Current###")
            self.filters.set_active(0)

    def update_combos(self, filters, operation):
        self.query_manager.get_filters_from_pages([(k,v.query_constructor.query.get_filter_table())
                                                    for k,v in filters.items()
                                                        if v != self])

        if operation == 'rename' or not self.current:
            self.current = [n for n,f in filters.iteritems() if f==self][0]

        if operation:
            self.froms_combo.update(operation, filters.keys(), self.current)

    def set_query(self, *args):
        query = self.queries.get_active_text().decode('utf8')
        self.query_constructor.set_query(self.query_manager.queries[query].strip())

    def set_filter(self, *args):
        self.notify_all(None)
        try:
            query = self.filters.get_active_text().decode('utf8')
            if query == "###Current###":
                self.query_constructor.set_filter(self.current)
            else:
                self.query_constructor.set_filter(self.query_manager.filters[query])
        except AttributeError:
            self.filters.set_active(0)

    def get_query(self):
        return self.query_constructor.get_sql(self.get_only_colors())
        
    def get_auto_lid(self):
        return self.add_lid.get_active()

    def get_only_colors(self):
        return self.query_constructor.get_only_colors()
