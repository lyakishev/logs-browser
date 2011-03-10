import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import pango


class Clause(gtk.HBox):
    def __init__(self):
        super(Clause, self).__init__()
        self.fields = gtk.combo_box_new_text()
        self.fields.append_text('log')
        self.fields.append_text('log_name')
        self.fields.append_text('type')
        self.fields.append_text('source')
        self.fields.append_text('computer')
        self.fields.append_text('date')
        self.not_ = gtk.CheckButton("NOT")
        self.operators = gtk.combo_box_new_text()
        self.operators.append_text("MATCH")
        self.operators.append_text("LIKE")
        self.operators.append_text("=")
        self.operators.append_text("REGEXP")
        self.operators.append_text("GLOB")
        self.operators.append_text("BETWEEN")
        self.value = gtk.Entry()
        self.clear_button = gtk.Button('x')
        self.pack_start(self.fields, False, False)
        self.pack_start(self.not_, False, False)
        self.pack_start(self.operators, False, False)
        self.pack_start(self.value, True, True)
        self.pack_start(self.clear_button, False, False)

class WhereClause(Clause):
    def __init__(self):
        super(WhereClause, self).__init__()
        self.logic = gtk.combo_box_new_text()
        self.logic.append_text("AND")
        self.logic.append_text("OR")
        self.logic.set_active(0)
        self.pack_end(self.logic,False,False)

class ColorClause(Clause):
    def __init__(self, col):
        super(ColorClause, self).__init__()
        self.color = gtk.ColorButton(gtk.gdk.color_parse(col))
        self.pack_end(self.color,False,False)


class WhereClauses(gtk.VBox):
    def __init__(self, q=3):
        super(WhereClauses, self).__init__()
        self.clauses = []
        for n in range(q):
            clause = WhereClause()
            self.pack_start(clause,False,False)
            self.clauses.append(clause)

class CaseAsColorClauses(gtk.VBox):
    def __init__(self, q=3):
        super(CaseAsColorClauses, self).__init__()
        self.clauses = []
        for c,n in zip(['red','yellow','green'],range(q)):
            clause = ColorClause(c)
            self.pack_start(clause,False,False)
            self.clauses.append(clause)

class Plain(gtk.ScrolledWindow):
    def __init__(self):
        super(Plain, self).__init__()
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.txt = gtk.TextView()
        self.add(self.txt)


class Where(gtk.Notebook):
    def __init__(self):
        super(Where, self).__init__()
        simple = WhereClauses()
        plain = Plain()
        simple_label = gtk.Label()
        simple_label.set_markup('<b>WHERE</b>')
        plain_label = gtk.Label()
        plain_label.set_markup("<b>WHERE</b> (text)")

        self.append_page(simple, simple_label)
        self.append_page(plain, plain_label)

class CaseAsColor(gtk.Notebook):
    def __init__(self):
        super(CaseAsColor, self).__init__()
        simple = CaseAsColorClauses()
        plain = Plain()
        simple_label = gtk.Label()
        simple_label.set_markup('<b>CASE (...) AS bgcolor</b>')
        plain_label = gtk.Label()
        plain_label.set_markup("<b>CASE (...) AS bgcolor</b> (text)")

        self.append_page(simple, simple_label)
        self.append_page(plain, plain_label)

class Select(gtk.ScrolledWindow):
    def __init__(self):
        super(Select, self).__init__()
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.model = gtk.ListStore(bool,str,str)
        self.view = gtk.TreeView()
        functions = gtk.combo_box_new_text()
        functions.append_text("count")
        functions.append_text("sum")
        functions.append_text("avg")
        functions.append_text("group_concat")
        functions.append_text("snippet")
        functions.append_text("length")
        functions.append_text("time")
        functions.append_text("")
        show_renderer = gtk.CellRendererToggle()
        show_renderer.set_property('activatable', True)
        func_renderer = gtk.CellRendererCombo()
        #func_renderer.set_property('model',functions)
        field_renderer = gtk.CellRendererText()
        field_renderer.set_property("editable", False)
        show_column = gtk.TreeViewColumn("",show_renderer)
        show_label = gtk.Label()
        show_label.set_markup("<b>SELECT</b>")
        show_label.show()
        show_column.set_widget(show_label)
        show_column.add_attribute(show_renderer, "active", 0)
        func_column = gtk.TreeViewColumn("func",func_renderer,
                                         text=1)
        field_column = gtk.TreeViewColumn("field",field_renderer,
                                         text=2)
        self.view.append_column(show_column)
        self.view.append_column(func_column)
        self.view.append_column(field_column)
        self.model.append([True, 'time', 'date'])
        self.model.append([True, '', 'log_name'])
        self.model.append([True, '', 'type'])
        self.model.append([False, '', 'computer'])
        self.model.append([False, '', 'source'])
        self.model.append([False, '', 'log'])
        self.model.append([False, '', '*'])
        self.model.append([False, '', 'this'])
        self.view.set_model(self.model)
        self.add(self.view)

class GroupBy(gtk.ScrolledWindow):
    def __init__(self):
        super(GroupBy, self).__init__()
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.model = gtk.ListStore(bool,str)
        self.view = gtk.TreeView()
        functions = gtk.combo_box_new_text()
        show_renderer = gtk.CellRendererToggle()
        show_renderer.set_property('activatable', True)
        field_renderer = gtk.CellRendererText()
        field_renderer.set_property("editable", False)
        show_label = gtk.Label()
        show_label.set_markup("<b>GROUP BY</b>")
        show_label.show()
        show_column = gtk.TreeViewColumn("",show_renderer)
        show_column.set_widget(show_label)
        show_column.add_attribute(show_renderer, "active", 0)
        field_column = gtk.TreeViewColumn("field",field_renderer,
                                         text=1)
        self.view.append_column(show_column)
        self.view.append_column(field_column)
        self.model.append([True, 'date'])
        self.model.append([False, 'log_name'])
        self.model.append([True, 'type'])
        self.model.append([False, 'computer'])
        self.model.append([False, 'source'])
        self.view.set_model(self.model)
        self.add(self.view)

class Query(gtk.Notebook):
    def __init__(self):
        super(Query, self).__init__()
        select = Select()
        where = Where()
        groupby = GroupBy()
        color = CaseAsColor()

        table = gtk.Table(2,2,False)

        table.attach(select,0,1,0,1,xoptions=0,yoptions=gtk.FILL|gtk.EXPAND)
        table.attach(where,1,2,0,1,xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL|gtk.EXPAND)
        table.attach(groupby,0,1,1,2,xoptions=gtk.FILL,yoptions=gtk.FILL|gtk.EXPAND)
        table.attach(color,1,2,1,2,xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL|gtk.EXPAND)
        
        query_label = gtk.Label("Query")

        self.append_page(table, query_label)

        plain = Plain()
        plain_query_label = gtk.Label("Plain Query")

        self.append_page(plain, plain_query_label)
        self.show_all()
    



       

       
    

