import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango
import re

class QueryDesigner():
    def __init__(self, plain, loglist):
        self.loglist = loglist
        self.plain = plain
        self.query_model = gtk.ListStore(bool,                #show
                                   str,#column
                                   str,#alias
                                   str,#where criteria
                                   str,                #group by                        
                                   str,#gobject.TYPE_OBJECT, #order by
                                   str,                 #color
                                   str,#color_clause
                                   str
                                   )                 #value        

        self.field_model = gtk.ListStore(str)
        self.order_model = gtk.ListStore(str)
        self.group_model = gtk.ListStore(str)

        for c in ["","group","avg","count","min","max","sum","error","group_concat","rows"]:
            self.group_model.append([c])

        for c in ["time","date","comp","log_name","type",
                  "source","log","snippet","rowid", "this"]:
            self.field_model.append([c])

        for c in ["","DESC","ASC"]:
            self.order_model.append([c])

        select_renderer = gtk.CellRendererToggle()
        select_renderer.set_property('activatable', True)
        select_renderer.connect('toggled', self.col_toggled_cb,
                                self.query_model, 0)
        select_column = gtk.TreeViewColumn("show", select_renderer )
        select_column.add_attribute(select_renderer, "active", 0)

        field_renderer = gtk.CellRendererCombo()
        field_renderer.set_property("model", self.field_model)
        field_renderer.set_property('text-column', 0)
        field_renderer.set_property('editable', True)
        field_renderer.connect("changed", self.change_func, 1)
        field_column = gtk.TreeViewColumn("column", field_renderer, text=1)

        alias_renderer = gtk.CellRendererText()
        alias_renderer.set_property('editable',True)
        alias_renderer.connect("edited", self.change_value, 2)
        alias_column = gtk.TreeViewColumn("as", alias_renderer,
                                                text=2)

        where_renderer = gtk.CellRendererText()
        where_renderer.set_property('editable',True)
        where_renderer.connect("edited", self.change_value, 3)
        where_column = gtk.TreeViewColumn("where", where_renderer,
                                                text=3)

        groupby_renderer = gtk.CellRendererCombo()
        groupby_renderer.set_property("model", self.group_model)
        groupby_renderer.set_property('text-column', 0)
        groupby_renderer.set_property('editable', True)
        groupby_renderer.connect("changed", self.change_func, 4)
        groupby_column = gtk.TreeViewColumn("group by", groupby_renderer, text=4)

        order_renderer = gtk.CellRendererCombo()
        order_renderer.set_property("model", self.order_model)
        order_renderer.set_property('text-column', 0)
        order_renderer.set_property('editable', True)
        order_renderer.connect("changed", self.change_func, 5)
        order_column = gtk.TreeViewColumn("order", order_renderer, text=5)
        
        
        color_renderer = gtk.CellRendererText()
        color_renderer.set_property("editable", False)
        color_column = gtk.TreeViewColumn("color", color_renderer,
                                                text=6, cell_background=8)

        color_case_renderer = gtk.CellRendererText()
        color_case_renderer.set_property('editable',True)
        color_case_renderer.connect("edited", self.change_value, 7)
        color_case_column = gtk.TreeViewColumn("clause", color_case_renderer,
                                                text=7)

        hidden_colorr = gtk.CellRendererText()
        hidden_colorr.set_property('editable',True)
        hidden_color = gtk.TreeViewColumn("value", hidden_colorr,
                                                text=8)
        hidden_color.set_visible(False)

        self.view = gtk.TreeView()
        self.view.append_column(select_column)
        self.view.append_column(field_column)
        self.view.append_column(alias_column)
        self.view.append_column(where_column)
        self.view.append_column(groupby_column)
        self.view.append_column(order_column)
        self.view.append_column(color_column)
        self.view.append_column(color_case_column)
        self.view.append_column(hidden_color)

        self.query_model.append([True, 'date', '','','group','DESC','','','#fff'])
        self.query_model.append([True, 'log_name', '','','group','','','','#fff'])
        self.query_model.append([True, 'type', '','','group','','','','#fff'])
        self.query_model.append([False, '', '','','','','','','#fff'])
        self.plain.set_text(self.get_sql(self.loglist.fts))

        #self.view.set_property("enable-grid-lines", True)
        self.view.set_model(self.query_model)
        self.view.connect("cursor-changed", self.add_row)
        self.view.connect("key-press-event", self.delete_row)
        self.view.connect("row-activated", self.change_color)

    def set_sql(self):
        self.plain.set_text(self.get_sql(self.loglist.fts))

    def col_toggled_cb(self, cell, path, model, col):
        model[path][col] = not model[path][col]
        self.set_sql()

    def change_func(self, combo, path, iter_, col):
        self.query_model[path][col] = combo.get_property("model").get_value(iter_,0)
        self.set_sql()

    def change_value(self, cell, path, new_text, col):
        self.query_model[path][col] = new_text
        self.set_sql()

    def add_row(self, view):
        selection = view.get_selection()
        (model, iter_) = selection.get_selected()
        try:
            if not model.iter_next(iter_):
                self.query_model.append([False, '', '','','','','','','#fff'])
        except TypeError:
            pass

    def delete_row(self, view, event):
        if event.keyval == 65535:
            selection = view.get_selection()
            (model, iter_) = selection.get_selected()
            if iter_ is not None and model.iter_next(iter_):
                model.remove(iter_)
        self.set_sql()

    def change_color(self, view, path, column):
        selection = view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        (model, iter_) = selection.get_selected()
        ncol = None
        for n,c in enumerate(view.get_columns()):
            if c == column:
                ncol = n
        if ncol and ncol == 6:
            colordlg = gtk.ColorSelectionDialog("Select color")
            colorsel = colordlg.colorsel
            colorsel.set_has_palette(True)
            response = colordlg.run()
            if response == gtk.RESPONSE_OK:
                col = colorsel.get_current_color()
                model[path][8]=col
            colordlg.destroy()
        self.set_sql()

    def get_sql(self, fts):

        def check_clause(clause):
            words = len(clause.split())
            if words > 1 and clause.count("'")>1:
                return clause
            else:
                if fts:
                    return "MATCH '%s'" % clause
                else:
                    return "REGEXP '%s'" % clause

        def match(col, clause, color):
            if 'match' in clause.lower():
                return ("rowid",
                        "in (select rowid from $this where %s %s)" % (col,
                                                                    clause),
                        color)
            else:
                return (col, clause, color)

        select = "select "
        for r in self.query_model:
            if r[0]:
                column = r[1].replace("snippet",
                                      "snippet($this)").replace("time",
                                                            "strftime('%H:%M:%S.%f',date)")
                select += "%s%s, " % (("%s(%s)" % (r[4], column)) if (r[4] and r[4]!='group') else column,
                            (" as %s" % r[2]) if r[2] else "")

        from_ = "from $this"

        match_re = re.compile("(?i)match '(.+?)'")
        match_clauses = ""
        nonmatch_clauses = []
        for r in self.query_model:
            if r[3] and r[1]:
                match_ = check_clause(r[3])
                if 'match' in match_.lower():
                    match_clauses+="%s:%s " % (r[1],
                                match_re.search(match_).group(1))
                else:
                    nonmatch_clauses.append("%s %s" % (r[2] or r[1],
                                                 match_))
        match_clauses = "$this MATCH '%s'" % match_clauses[:-1] if match_clauses else ""
        nonmatch_clauses = " AND ".join(nonmatch_clauses)
        where_clauses = ((match_clauses+" AND "+nonmatch_clauses) if match_clauses
                         and nonmatch_clauses else (match_clauses or
                         nonmatch_clauses))
            
        where = ("where " + where_clauses) if where_clauses else ""

        groups = ", ".join([(r[2] or r[1]) for r in self.query_model
                            if r[4] == 'group'])
        groupby = ("group by " + groups) if groups else ""

        orders = ", ".join(["%s %s" % (r[2] or r[1], r[5])
                            for r in self.query_model if r[5]])
        order_by = ("order by "+orders) if orders else ""

        agg = [r[4] for r in self.query_model if r[4]]

        color_fields = [(r[2] or r[1]) for r in self.query_model if r[7]]
        if color_fields:
            color = "'#fff' as bgcolor"
            bgcolor_n = 1
            for r in self.query_model:
                if r[7] and r[1]:

                    bgcol="(case when %s %s then '%s' end)" % match(r[1],
                                                    check_clause(r[7]), r[8])
                    if groups:
                        bgcol = "color_agg(%s)" % bgcol
                    color+=(",\n%s as bgcolor_%d" % (bgcol, bgcolor_n))
                    bgcolor_n+=1
            select += ("\n%s," % color)
        if agg:
            select+="\nrows(rowid) as rows_for_log_window"
        else:
            select+="\nrowid as rows_for_log_window"
        return "\n".join([select,from_,where,groupby,order_by])


class Plain(gtk.ScrolledWindow):
    def __init__(self):
        super(Plain, self).__init__()
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.txt = gtk.TextView()
        self.buf = self.txt.get_buffer()
        self.add(self.txt)

    def set_text(self, txt):
        self.buf.set_text(txt)

    def get_text(self):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        txt = self.buf.get_text(start, end)
        return txt


class Query(gtk.Notebook):
    def __init__(self, loglist):
        super(Query, self).__init__()
        scroll_query = gtk.ScrolledWindow()
        scroll_query.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        
        self.plain = Plain()
        plain_query_label = gtk.Label("Plain Query")

        self.query = QueryDesigner(self.plain, loglist)
        scroll_query.add(self.query.view)
        
        query_label = gtk.Label("Query")

        self.append_page(scroll_query, query_label)
        self.append_page(self.plain, plain_query_label)

        self.sens_list = [self.plain, self.query.view]

        self.show_all()


    def set_sql(self):
        self.query.set_sql()

    def get_sql(self):
        return self.plain.get_text()
        



       

       
    

