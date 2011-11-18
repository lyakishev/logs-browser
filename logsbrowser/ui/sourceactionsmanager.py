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
import gobject

class SourceActionsManagerUI(object):
    def __init__(self, sourcemanager, root):
        self.source_manager = sourcemanager
        window = gtk.Window()
        window.set_title("Actions Manager")
        window.set_default_size(480, 320)
        window.set_modal(gtk.TRUE)
        window.set_transient_for(root)
        
        box = gtk.HBox()
        self.actions_list = gtk.ListStore(gobject.TYPE_STRING)
        self.actions_view = gtk.TreeView()
        name_renderer = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Name", name_renderer,
                                 text=0)
        name_renderer.set_property('editable', False)
        self.actions_view.append_column(col)
        self.actions_view.set_model(self.actions_list)
        
        for select_name in sourcemanager.selects:
            self.actions_list.append([select_name])
            
        button_box = gtk.VButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_START)
        new_button = gtk.Button("New")
        new_button.connect("clicked", self.new_source_actions)
        edit_button = gtk.Button("Edit")
        edit_button.connect("clicked", self.edit_source_actions)
        delete_button = gtk.Button("Delete")
        delete_button.connect("clicked", self.delete_source_actions)
        
        button_box.pack_start(new_button, False, False, 3)
        button_box.pack_start(edit_button, False, False, 3)
        button_box.pack_start(delete_button, False, False, 3)
        
        scr = gtk.ScrolledWindow()
        scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scr.add(self.actions_view)
        
        box.pack_start(scr, True, True, 5)
        box.pack_start(button_box, False, False, 5)
        
        window.add(box)
        window.show_all()
        
    def new_source_actions(self, button):
        action = ActionsEditor(self.source_manager)
        result = action.run()
        if result == gtk.RESPONSE_OK:
            new_name = action.get_name()
            new_actions = action.get_actions()
            if new_actions and new_name:
                self.source_manager.new_select(new_name, new_actions)
                self.actions_list.append([new_name])
        action.destroy()
    
    def edit_source_actions(self, button):
        name_to_edit, iter_ = self.get_selected_name()
        action = ActionsEditor(self.source_manager, name_to_edit)
        result = action.run()
        if result == gtk.RESPONSE_OK:
            new_name = action.get_name()
            new_actions = action.get_actions()
            if new_actions and new_name:
                self.source_manager.update_actions(name_to_edit, new_name, new_actions)
                self.actions_list.set_value(iter_, 0, new_name)
        action.destroy()
        
    def get_selected_name(self):    
        selection = self.actions_view.get_selection()
        (model, iter_) = selection.get_selected()
        return self.actions_list.get_value(iter_, 0), iter_
        
    
    def delete_source_actions(self, button):
        name_to_delete, iter_ = self.get_selected_name()
        self.source_manager.delete_select(name_to_delete)
        self.actions_list.remove(iter_)
        

class ActionsEditor(gtk.Dialog):
    def __init__(self, source_manager, actions_name=None):
        super(ActionsEditor, self).__init__()
        self.set_title("Actions Editor")
        self.set_default_size(512, 384)
        self.source_manager = source_manager
        self.actions_name = actions_name
        
        title_box = gtk.HBox()
        title_label = gtk.Label("Name: ")
        self.title_entry = gtk.Entry()
        if actions_name:
            self.title_entry.set_text(actions_name)
        title_box.pack_start(title_label, False, False, 3)
        title_box.pack_start(self.title_entry, True, True)
        
        self.add_button("Save", gtk.RESPONSE_OK)
        self.add_button("Cancel", gtk.RESPONSE_CANCEL)
        self.model, self.view = self.build_actions_table(actions_name)
        
        scr = gtk.ScrolledWindow()
        scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scr.add(self.view)
        
        self.vbox.pack_start(title_box, False, False)
        self.vbox.pack_start(scr, True, True)
        self.show_all()
        
    def get_name(self):
        return self.title_entry.get_text()
    
    def get_actions(self):
        actions = []
        for r in self.model:
            if all(r):
                actions.append(dict(zip(self.headers, r)))
        return actions
        
    def change_func(self, combo, path, iter_, col, model):
        model[path][col] = combo.get_property("model").get_value(iter_,0)
        
    def change_value(self, cell, path, new_text, col, model):
        model[path][col] = new_text
        
    def delete_row(self, view, event):
        if event.keyval == 65535:
            selection = view.get_selection()
            (model, iter_) = selection.get_selected()
            if iter_ is not None and model.iter_next(iter_):
                model.remove(iter_) 
                
    def add_row(self, view):
        selection = view.get_selection()
        (model, iter_) = selection.get_selected()
        try:
            if not model.iter_next(iter_):
                model.append(self.source_manager.empty_action())
        except TypeError:
            pass 
        
    def focus_out(self, entry, event, path, col, model):
        iter_ = model.get_iter_from_string(path)
        model.set_value(iter_, col, entry.get_text())
            
    def set_cell_entry_signal(self, cell, entry, num, col, model):
        entry.connect("focus-out-event", self.focus_out, num, col, model)
        
    def activate_cell(self, view, event):
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            view.set_cursor(path[0], focus_column = path[1], start_editing=True)
        
    def build_actions_table(self, actions_name):
        self.headers = self.source_manager.get_attributes()
        cols = [gobject.TYPE_STRING for i in self.headers]
        model = gtk.ListStore(*cols)
        view = gtk.TreeView()
        for number, header in enumerate(self.headers):
            if hasattr(self.source_manager, "%s_map" % header):
                c_model = gtk.ListStore(str)
                for h in getattr(self.source_manager, "%s_map" % header):
                    c_model.append([h])
                renderer = gtk.CellRendererCombo()
                renderer.set_property("model", c_model)
                renderer.set_property('text-column', 0)
                renderer.set_property('editable', True)
                renderer.connect("changed", self.change_func, number, model)
                col = gtk.TreeViewColumn(header, renderer, text=number)
            else:
                renderer = gtk.CellRendererText()
                renderer.set_property('editable', True)
                renderer.connect("editing-started", self.set_cell_entry_signal, number, model)
                renderer.connect("edited", self.change_value, number, model)
                col = gtk.TreeViewColumn(header, renderer, text=number)
            view.append_column(col)
        if actions_name:
            for action in self.source_manager.get_actions(actions_name):
                model.append(action)
        model.append(self.source_manager.empty_action())
        view.set_model(model)
        view.connect("key-press-event", self.delete_row)
        view.connect("cursor-changed", self.add_row)
        view.connect("button-press-event", self.activate_cell)
        return model, view