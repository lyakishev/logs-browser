#!/usr/bin/env python
# vim: ts=4:sw=4:tw=78:nowrap
""" Demonstration using editable and activatable CellRenderers """
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import datetime
from net_time import GetTrueTime
from logworker import *
from widgets.date_time import DateFilter
from widgets.logs_tree import FileServersTree, EvlogsServersTree
from widgets.logs_notebook import LogsNotebook
import sys
from widgets.status_icon import StatusIcon
if sys.platform == 'win32':
    from evlogworker import *
    from widgets.evt_type import EventTypeFilter
import profiler


class GUI_Controller:
    """ The GUI class is the controller for application """
    def __init__(self):
        # setup the main window
        self.root = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.root.set_title("Log Viewer")
        self.root.connect("destroy", self.destroy_cb)
        self.root.set_default_size(1200, 800)

        self.date_filter = DateFilter()

        options_frame = gtk.Frame("Options")
        self.index_t = gtk.CheckButton("Full-text index (enables MATCH operator)")
        self.index_t.set_active(False)
        options_frame.add(self.index_t)

        self.status = StatusIcon(self.date_filter, self.root)

        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.show_button = gtk.Button("Show")
        self.show_button.connect("clicked", self.show_logs)
        stop_all_btn = gtk.Button('Stop')
        stop_all_btn.connect('clicked', self.stop_all)
        break_btn = gtk.Button('Break')
        break_btn.connect('clicked', self.break_all)

        main_box = gtk.HPaned()
        control_box = gtk.VBox()
        self.file_servers_tree = FileServersTree()
        self.file_servers_tree.show()
        self.logs_notebook = LogsNotebook(self.file_servers_tree)

        log_ntb = gtk.Notebook()
        file_label = gtk.Label("Filelogs")
        file_label.show()
        log_ntb.append_page(self.file_servers_tree, file_label)
        log_ntb.show_all()

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

        button_box.pack_start(self.show_button)
        button_box.pack_start(stop_all_btn)
        button_box.pack_start(break_btn)
        control_box.pack_start(log_ntb, True, True)
        control_box.pack_start(self.date_filter, False, False)
        control_box.pack_start(options_frame, False, False)
        control_box.pack_start(button_box, False, False, 5)
        control_box.pack_start(self.progressbar, False, False)
        main_box.pack1(control_box, False, False)
        main_box.pack2(self.logs_notebook, True, False)
        self.root.add(main_box)

        if sys.platform == 'win32':
            evt_label = gtk.Label("Eventlogs")
            evt_label.show()
            self.evlogs_servers_tree = EvlogsServersTree()
            self.evlogs_servers_tree.show()
            log_ntb.append_page(self.evlogs_servers_tree, evt_label)

        self.root.show_all()

    def stop_all(self, *args):
        self.stop = True

    def break_all(self, *args):
        self.break_ = True

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        self.status.statusicon.set_visible(False)
        gtk.main_quit()
        return

    def show_logs(self, *args):
        dt = datetime.datetime.now()
        self.show_button.set_sensitive(False)
        self.stop = False
        self.break_ = False
        flogs = self.file_servers_tree.model.prepare_files_for_parse()
        try:
            evlogs = [[s[1], s[0]] for s in\
                        self.evlogs_servers_tree.model.get_active_servers()]
        except AttributeError:
            evlogs = []
        if flogs or evlogs:
            loglist = self.logs_notebook.get_current_logs_store
            try:
                loglist.clear()
            except:
                pass
            dates = self.date_filter.get_active() and\
                                       self.date_filter.get_dates or\
                                       (datetime.datetime.min,
                                        datetime.datetime.max)
            #if GetTrueTime.time_error_flag:
            #    GetTrueTime.show_time_warning(self.root)
            flogs_pathes = file_preparator(flogs)
            count_logs = len(flogs_pathes) + len(evlogs) + 1
            frac = 1.0 / (count_logs)
            loglist.set_hash([evlogs,flogs,dates,datetime.datetime.now()])
            loglist.create_new_table(self.index_t.get_active())
            count = 0
            for path, log in flogs_pathes:
                self.progressbar.set_text(log)
                loglist.insert_many(filelogworker(dates,path,log))
                loglist.db_conn.commit()
                count += 1
                self.progressbar.set_fraction(frac*count)
                if self.stop or self.break_:
                    break
                while gtk.events_pending():
                    gtk.main_iteration()
            for server, logtype in evlogs:
                self.progressbar.set_text(logtype)
                if self.stop or self.break_:
                    break
                loglist.insert_many(evlogworker(dates,server,logtype))
                loglist.db_conn.commit()
                count += 1
                self.progressbar.set_fraction(frac*count)
                while gtk.events_pending():
                    gtk.main_iteration()
            if self.break_:
                loglist.clear()
                self.progressbar.set_fraction(0.0)
                self.progressbar.set_text("")
            else:
                self.progressbar.set_text("Filling table...")
                loglist.execute("""select date, log_name, type,
                                    rows(rowid) as rows_for_log_window
                                    from this group by
                                   date, type order by date desc""")
                self.progressbar.set_fraction(1.0)
                self.progressbar.set_text("Complete")
        self.show_button.set_sensitive(True)
        print datetime.datetime.now() - dt
        

if __name__ == '__main__':
    myGUI = GUI_Controller()
    gtk.main()
