import gtk
from zipfile import ZipFile, ZIP_DEFLATED
import os

class ToggleEntryWidget(gtk.HBox):
    def __init__(self, label, default_value, entry_size=-1):
        gtk.HBox.__init__(self)
        self.visible_part = gtk.HBox()
        self.check = gtk.CheckButton(label)
        self.check.connect("toggled", self.show_hide_part)
        self.visible_part.pack_start(self.check, True, True)
        self.hide_part = gtk.HBox()
        self.value_edit = gtk.Entry()
        self.value_edit.set_text(default_value)
        self.value_edit.set_width_chars(entry_size)
        self.hide_part.pack_start(self.value_edit, False, False)
        self.pack_start(self.visible_part, False, False)
        self.pack_start(self.hide_part, True, True, 3)
        self.show_all()
        self.hide_part.hide()

    def show_hide_part(self, toggle):
        if toggle.get_active():
            self.hide_part.show()
        else:
            self.hide_part.hide()

    def get_value(self):
        return self.value_edit.get_text()

    def get_active(self):
        return self.check.get_active()

    def setup_actions(self):
        if self.get_active():
            self.do_actions = self.actions
            self.teardown_actions = self.teardown
        else:
            self.do_actions = lambda *args: None
            self.teardown_actions = lambda *args: None

    def actions(self, *args):
        pass

    def teardown(self):
        pass

class ZipBox(ToggleEntryWidget):
    def __init__(self):
        super(ZipBox, self).__init__("Save to zip archive", "logs.zip")
        self._zip = None


    @property
    def zip_(self):
        if not self._zip:
            self._zip = ZipFile(self.path, 'a', ZIP_DEFLATED)
        return self._zip

    def setup_actions(self, path, undo_list):
        self.path = os.path.join(path, self.get_value())
        ToggleEntryWidget.setup_actions(self)
        self.undo_list = undo_list

    def actions(self, *args):
        fullpath, name = args[:2]
        self.zip_.write(fullpath, name)
        os.remove(fullpath)
        self.undo_list.remove(fullpath)
        self.undo_list.add(self.path)

    def teardown(self):
        self.zip_.close()

    def undo(self):
        pass


class SizeBox(ToggleEntryWidget):
    def __init__(self):
        super(SizeBox, self).__init__("Archive file if size larger than", "4", 4)
        mb = gtk.Label("MB")
        self.hide_part.pack_start(mb, False, False, 2)
        mb.show()
        self.size = None

    def setup_actions(self, undo_list):
        self.size = int(self.get_value())
        ToggleEntryWidget.setup_actions(self)
        self.undo_list = undo_list


    def actions(self, *args):
        path = args[0]
        if os.path.getsize(path) > self.size*1024*1024:
             zpath = "%s.zip" % path
             z = ZipFile(zpath, 'w', ZIP_DEFLATED)
             z.write(path, os.path.basename(path))
             z.close()
             os.remove(path)
             self.undo_list.remove(path)
             self.undo_list.add(zpath)

    def undo(self):
        pass

class ZipSizeBox(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.zipbox = ZipBox()
        self.sizebox = SizeBox()
        self.sizebox.check.set_label("Archive files if size larger than")
        self.zipbox.check.connect('toggled', self.show_size_box)
        self.pack_start(self.zipbox)
        self.pack_start(self.sizebox)

    def show_size_box(self, toggle):
        if toggle.get_active():
            self.sizebox.set_sensitive(False)
            self.sizebox.check.set_active(False)
        else:
            self.sizebox.set_sensitive(True)

    def undo(self):
        pass
        
def gtk_main_iteration():
    while gtk.events_pending():
        gtk.main_iteration()

def save_files_to_dir_dialog(name_action, sens, progress):
    fchooser = gtk.FileChooserDialog("Save logs...", None,
        gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL,
        gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
    zipsizebox = ZipSizeBox()
    fchooser.set_extra_widget(zipsizebox)
    response = fchooser.run()
    if response == gtk.RESPONSE_OK:
        path = fchooser.get_filename()
        undo_files = set()
        zipsizebox.sizebox.setup_actions(undo_files)
        zipsizebox.zipbox.setup_actions(path, undo_files)
        fchooser.destroy()
        sens(False)
        try:
            progress.begin(len(name_action))
            for name, action in name_action.iteritems():
                try:
                    progress.set_text("Saving %s" % name)
                    fullpath = os.path.join(path, name)
                    f = open(fullpath, 'w')
                    try:
                        progress.execute(f.writelines, [f.close, lambda: os.remove(fullpath)],
                                                    "Saving %s" % name, action())
                    finally:
                        f.close()
                    undo_files.add(fullpath)
                    progress.execute(zipsizebox.sizebox.do_actions,
                                    [zipsizebox.sizebox.undo], "Zipping %s" % name, fullpath)
                    progress.execute(zipsizebox.sizebox.teardown_actions,
                                            [lambda: None], "")
                    progress.execute(zipsizebox.zipbox.do_actions,
                                        [zipsizebox.zipbox.undo], "Zipping %s" % name,
                                        fullpath, name)
                    progress.add_frac()
                except progress.StopException:
                    break
        except progress.BreakException:
            zipsizebox.zipbox.teardown_actions()
            for path in undo_files:
                os.remove(path)
        finally:
            zipsizebox.zipbox.teardown_actions()
            progress.end()
        sens(True)
    else:
        fchooser.destroy()

def save_file_dialog(name_action, sens, progress):
    name, text_action = name_action.items()[0]
    fchooser = gtk.FileChooserDialog("Save logs...", None,
        gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL,
        gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
    fchooser.set_current_name(name)
    sizebox = SizeBox()
    fchooser.set_extra_widget(sizebox)
    response = fchooser.run()
    if response == gtk.RESPONSE_OK:
        path = fchooser.get_filename()
        undo_files = set()
        sizebox.setup_actions(undo_files)
        fchooser.destroy()
        sens(False)
        try:
            progress.begin(0)
            progress.set_text("Saving %s" % name)
            path = path.decode('utf8')
            f = open(path, 'w')
            try:
                progress.execute(f.writelines, [f.close, lambda: os.remove(path)],
                                      "Saving %s" % name, text_action())
            finally:
                f.close()
            undo_files.add(path)
            progress.execute(sizebox.do_actions, [sizebox.undo], "Zipping %s" % name, path)
            progress.execute(sizebox.teardown_actions, [lambda: None], "")
        except (progress.BreakException, progress.StopException):
            pass
        finally:
            progress.end()
        sens(True)
    else:
        fchooser.destroy()

if __name__ == "__main__":
    w = gtk.Window()
    w.add(ZipBox())
    w.show()
    gtk.main()

