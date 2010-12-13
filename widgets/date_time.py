import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import datetime

class DateTimeWidget(gtk.Table):
    def __init__(self):
        super(DateTimeWidget,self).__init__(2, 3, False)
        self.hours_adj = gtk.Adjustment(value=0, lower=0, upper=23, step_incr=1)
        self.minute_adj = gtk.Adjustment(value=0, lower=0, upper=59, step_incr=1)
        self.second_adj = gtk.Adjustment(value=0, lower=0, upper=59, step_incr=1)
        self.year_entry = gtk.Entry(10)
        self.year_entry.set_width_chars(10)
        self.hours_spin = gtk.SpinButton(adjustment=self.hours_adj)
        self.hours_spin.set_width_chars(2)
        self.minutes_spin = gtk.SpinButton(adjustment=self.minute_adj)
        self.minutes_spin.set_width_chars(2)
        self.seconds_spin = gtk.SpinButton(adjustment=self.second_adj)
        self.seconds_spin.set_width_chars(2)
        self.now_btn = gtk.Button("Now")
        self.now_btn.connect("clicked", self.set_now)
        self.attach(self.hours_spin, 0,1,0,1, xoptions=0, yoptions=0)
        self.attach(self.minutes_spin, 1,2,0,1, xoptions=0, yoptions=0)
        self.attach(self.seconds_spin, 2,3,0,1, xoptions=0, yoptions=0)
        self.attach(self.year_entry, 0,2,1,2, xoptions=0, yoptions=0)
        self.attach(self.now_btn, 2,3,1,2, xoptions=0, yoptions=0)
        self.set_now()

    def set_now(self, *args):
        now = datetime.datetime.now()
        self.hours_spin.set_value(now.hour)
        self.minutes_spin.set_value(now.minute)
        self.seconds_spin.set_value(now.second)
        self.year_entry.set_text(now.strftime("%d.%m.%Y"))

    def get_datetime(self):
            dt_date = datetime.datetime.strptime(self.year_entry.get_text(),
                                                    '%d.%m.%Y')
            return datetime.datetime(
                dt_date.year, dt_date.month, dt_date.day,
                self.hours_spin.get_value_as_int(),
                self.minutes_spin.get_value_as_int(),
                self.seconds_spin.get_value_as_int()
            )

    def set_sens(self, sens):
        for child in [self.hours_spin, \
                      self.minutes_spin, \
                      self.seconds_spin, \
                      self.year_entry, \
                      self.now_btn]:
            child.set_sensitive(sens)

class FromToFilter(gtk.HBox):
    def __init__(self):
        super(FromToFilter, self).__init__()
        self.from_radio = gtk.RadioButton(label="From")
        self.to_check = gtk.CheckButton("To")
        self.to_check.set_active(False)
        self.from_date = DateTimeWidget()
        self.to_date = DateTimeWidget()
        self.pack_start(self.from_radio, False, False)
        self.pack_start(self.from_date, False, False)
        self.pack_start(self.to_check, False, False)
        self.pack_start(self.to_date, False, False)
        self.to_check.connect("toggled", self.to_date_sens)
        self.to_date_sens()

    def to_date_sens(self, *args):
        if self.to_check.get_active():
            self.to_date.set_sens(True)
        else:
            self.to_date.set_sens(False)

