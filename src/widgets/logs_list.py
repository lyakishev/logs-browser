# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from widgets.log_window import LogWindow
from widgets.color_parser import ColorParser, SQLExecuter
from widgets.label_text import LabelText
import re
import pickle
import hashlib
import sqlite3

def strip(t):
    return t.strip()

def regexp(t, pattern):
    return True if re.compile(pattern).search(t) else False

def utf_decode(t):
    try:
        txt = t.decode('utf-8').encode('utf-8')
    except UnicodeDecodeError:
        txt = t.decode('cp1251').encode('utf-8')
    return txt
    

class LogList:
    db_conn = sqlite3.connect("", check_same_thread = False,
                      detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    db_conn.text_factory = sqlite3.OptimizedUnicode
    db_conn.row_factory = sqlite3.Row
    db_conn.create_function("strip", 1, strip)
    db_conn.create_function("regexp", 2, regexp)
    #TODO# db_conn.create_function("pretty_xml", 1, pretty_xml)
    db_conn.text_factory = utf_decode

    def __init__(self):
        self.hash_value = ""
        self.view = gtk.TreeView()
        self.view.connect('row-activated', self.show_log)
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.model = None
        self.columns = []
        self.cur = self.db_conn.cursor()
        self.cur.execute("PRAGMA synchronous=OFF;")


    def create_new_table(self):
        sql = """create virtual table %s using fts4(date text, computer text, log text,
                 type text, source text, msg text, 
                 color text);""" % self.hash_value
        self.cur.execute(sql)
        self.db_conn.commit()

    def insert(self, log):
        self.cur.execute("insert into %s values (?,?,?,?,?,?,?);" % self.hash_value,
                         log)

    def execute(self, sql):
        self.view.freeze_child_notify()
        self.view.set_model(None)
        self.cur.execute(sql.replace("this", self.hash_value))
        rows = self.cur.fetchall()
        headers = rows[0].keys()
        self.set_new_list_store(headers)
        self.build_view(headers)
        sib = None
        for row in rows:
            sib = self.model.insert_after(sib, tuple(row))
        if 'date' in headers:
            self.model.set_sort_column_id(headers.index('date'), gtk.SORT_DESCENDING)
        self.view.set_model(self.model)
        self.view.thaw_child_notify()

    def set_new_list_store(self, cols):
        args = [gobject.TYPE_STRING for i in cols]
        self.model = gtk.ListStore(*args)

    def build_view(self, args):
        for col in self.columns:
            self.view.remove_column(col)
        self.columns = []
        for number, header in enumerate(args):
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', False)
            renderer.props.wrap_width = 640
            renderer.props.wrap_mode = gtk.WRAP_WORD
            col = gtk.TreeViewColumn(header, renderer,
                                text=number)
            self.columns.append(col)
            col.set_sort_column_id(number)
            col.set_resizable(True)
            self.view.append_column(col)
        self.view.connect('row-activated', self.show_log)
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    def set_hash(self, params):
        pick = pickle.dumps(params)
        hash_v = hashlib.md5(pick).hexdigest()
        self.hash_value = "".join(["_",hash_v])

    def clear(self):
        if self.model:
            self.model.clear()
        if self.hash_value:
            self.cur.execute("drop table %s;" % self.hash_value)
            self.db_conn.commit()
        
    def show_log(self):
        pass
        
        
        

#class LogsModel:
#    """ The model class holds the information we want to display """
#    def __init__(self):
#        """ Sets up and populates our gtk.TreeStore """
#        """!!!Rewrite to recursive!!!!"""
#        self.args = (gobject.TYPE_STRING,
#                     gobject.TYPE_STRING,
#                     gobject.TYPE_STRING,
#                     gobject.TYPE_STRING,
#                     gobject.TYPE_STRING,
#                     gobject.TYPE_STRING,
#                     gobject.TYPE_STRING,
#                     gobject.TYPE_BOOLEAN)
#        self.list_store = gtk.ListStore(*self.args)
#        self.rows_set = set()
#        # places the global people data into the list
#        # we form a simple tree.
#
#    def get_model(self):
#        """ Returns the model """
#        if self.list_store:
#            return self.list_store
#        else:
#            return None
#
#    def parse_like(self, pattern, text):
#        def parse(token):
#            if token.strip() in ["AND", "OR", "NOT", "AND (",
#                                 ") AND", "OR (", ") OR", "NOT ("]:
#                return t.lower()
#            elif not token:
#                return token
#            else:
#                lparen = token.count("(")
#                rparen = token.count(")")
#                if lparen == rparen:
#                    return 're.compile("%s", re.U).search(%s)' % (token, text)
#                elif lparen == rparen - 1:
#                    return 're.compile("%s", re.U).search(%s))' % (token, text)
#                elif rparen == lparen - 1:
#                    return '(re.compile("%s", re.U).search(%s)' % (token, text)
#
#        toks = "( AND \(| OR \(| NOT \(|\) AND |\) OR | AND | OR |NOT )"
#        if_expr = ''.join([parse(t) for t in re.split(toks, pattern)])
#        return if_expr
#
#    def highlight(self, col_str):
#        if col_str:
#            colors = col_str[::2]
#            for color, pattern in zip(colors,
#                                      [c.strip() for c in col_str[1::2]]):
#                if pattern:
#                    exp = self.parse_like(pattern, "msg")
#                    for row in self.list_store:
#                        if row[6] not in colors or row[6] == color:
#                            row[6] = "#FFFFFF"
#                            row[7] = False
#                        try:
#                            msg = row[5].decode('utf-8').encode('utf-8')
#                        except UnicodeDecodeError:
#                            msg = row[5].decode('cp1251').encode('utf-8')
#                        if eval(exp):
#                            row[6] = color
#                            row[7] = True
#                else:
#                    for row in self.list_store:
#                        if row[6] == color:
#                            row[6] = "#FFFFFF"
#                            row[7] = False
#        else:
#            for row in self.list_store:
#                row[6] = "#FFFFFF"
#                row[7] = False
#
#    def count_mean(self):
#        sum_ = 0
#        count_ = 0
#        for row in self.list_store:
#            count_ += 1
#            sum_ += len(row[5])
#        return sum_ / float(count_)
#
#    def set_of_rows(self):
#        if not self.rows_set:
#            n = len(self.args)
#            iter = self.list_store.get_iter_first()
#            val = self.list_store.get_value
#            while iter:
#                row_v = [val(iter, v) for v in xrange(n)]
#                self.rows_set.add(tuple(row_v))
#        return self.rows_set
#
#
#class DisplayLogsModel:
#    """ Displays the Info_Model model in a view """
#    def __init__(self, model):
#        """ Form a view for the Tree Model """
#        self.view = gtk.TreeView(model)
#        # setup the text cell renderer and allows these
#        # cells to be edited.
#
#        # Connect column0 of the display with column 0 in our list model
#        # The renderer will then display whatever is in column 0 of
#        # our model .
#        self.renderers = []
#        self.columns = []
#        for r, header in enumerate(['Date', 'Computer', 'Log', 'Type',\
#            'Source', 'Message', 'bgcolor', 'show']):
#            self.renderers.append(gtk.CellRendererText())
#            self.renderers[r].set_property('editable', False)
#            self.columns.append(gtk.TreeViewColumn(header, self.renderers[r],
#                                text=r))
#        # The columns active state is attached to the second column
#        # in the model.  So when the model says True then the button
#        # will show as active e.g on.
#        for cid, col in enumerate(self.columns):
#            self.view.append_column(col)
#            ctitle = col.get_title()
#            if ctitle == "Message" or ctitle == "bgcolor" or ctitle == "show":
#                col.set_visible(False)
#            else:
#                col.set_sort_column_id(cid)
#                col.set_resizable(True)
#        self.view.connect('row-activated', self.show_log)
#        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
#
#    def repaint(self):
#        for n, (col, ren) in enumerate(zip(self.columns, self.renderers)):
#            col.set_attributes(ren, cell_background=6, text=n)
#
#    def show_log(self, path, column, params):
#        selection = path.get_selection()
#        selection.set_mode(gtk.SELECTION_SINGLE)
#        (model, iter) = selection.get_selected()
#        LogWindow(model, self.view, iter, selection)
#        selection.set_mode(gtk.SELECTION_MULTIPLE)
#        return
#

class LogListWindow(gtk.Frame):
    def __init__(self):
        super(LogListWindow, self).__init__()
        self.log_list = LogList()
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.logs_window.add(self.log_list.view)
        exp = gtk.Expander("Filter")
        exp.connect("activate", self.text_grab_focus)
        self.filter_logs = SQLExecuter(self.log_list.model, self.log_list.view,
                            self.log_list)
        #label_text = LabelText()
        exp.add(self.filter_logs)
        box = gtk.VBox()
        self.add(box)
        #box.pack_start(label_text, False, False)
        box.pack_start(self.logs_window, True, True)
        box.pack_start(exp, False, False, 2)
        self.show_all()

    def text_grab_focus(self, *args):
        self.filter_logs.text.grab_focus()

    @property
    def get_view(self):
        return self.log_list.view
