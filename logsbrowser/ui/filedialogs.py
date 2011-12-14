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
            self._zip = ZipFile(self.path, 'w', ZIP_DEFLATED)
        return self._zip

    def setup_actions(self, path):
        self.path = os.path.join(path, self.get_value())
        ToggleEntryWidget.setup_actions(self)

    def actions(self, *args):
        fullpath, name = args[:2]
        self.zip_.write(fullpath, name)
        os.remove(fullpath)

    def teardown(self):
        self.zip_.close()

class SizeBox(ToggleEntryWidget):
    def __init__(self):
        super(SizeBox, self).__init__("Archive file if size larger than", "4", 4)
        mb = gtk.Label("MB")
        self.hide_part.pack_start(mb, False, False, 2)
        mb.show()
        self.size = None

    def setup_actions(self):
        self.size = int(self.get_value())
        ToggleEntryWidget.setup_actions(self)

    def actions(self, *args):
        path = args[0]
        if os.path.getsize(path) > self.size*1024*1024:
             z = ZipFile("%s.zip" % path, 'w', ZIP_DEFLATED)
             z.write(path, os.path.basename(path))
             z.close()
             os.remove(path)

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
        
def gtk_main_iteration():
    while gtk.events_pending():
        gtk.main_iteration()

def save_files_to_dir_dialog(name_action, sens):
    fchooser = gtk.FileChooserDialog("Save logs...", None,
        gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL,
        gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
    zipsizebox = ZipSizeBox()
    fchooser.set_extra_widget(zipsizebox)
    response = fchooser.run()
    if response == gtk.RESPONSE_OK:
        path = fchooser.get_filename()
        zipsizebox.sizebox.setup_actions()
        zipsizebox.zipbox.setup_actions(path)
        fchooser.destroy()
        sens(False)
        for name, action in name_action.iteritems():
            gtk_main_iteration()
            fullpath = os.path.join(path, name)
            with open(fullpath, 'w') as f:
                f.writelines(action())
            zipsizebox.sizebox.do_actions(fullpath)
            zipsizebox.sizebox.teardown_actions()
            gtk_main_iteration()
            zipsizebox.zipbox.do_actions(fullpath, name)
        zipsizebox.zipbox.teardown_actions()
        sens(True)
    else:
        fchooser.destroy()

def save_file_dialog(name_action, sens):
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
        sizebox.setup_actions()
        fchooser.destroy()
        sens(False)
        with open(path.decode('utf8'), 'w') as f:
            f.writelines(text_action())
        sizebox.do_actions(path)
        sizebox.teardown_actions()
        sens(True)
    else:
        fchooser.destroy()

if __name__ == "__main__":
    w = gtk.Window()
    w.add(ZipBox())
    w.show()
    gtk.main()

