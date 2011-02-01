import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import datetime
from common_filter import CommonFilter
from net_time import get_true_time
import datetime

class DateTimeWidget(gtk.Table):
    def __init__(self, d = datetime.timedelta(0)):
        super(DateTimeWidget,self).__init__(2, 3, False)
        self.delta = d
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
        now = get_true_time()
        self.set_date(now)

    def set_date(self, ct):
        dt = datetime.datetime.fromtimestamp(ct) + self.delta
        self.hours_spin.set_value(dt.hour)
        self.minutes_spin.set_value(dt.minute)
        self.seconds_spin.set_value(dt.second)
        self.year_entry.set_text(dt.strftime("%d.%m.%Y"))
        

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

class FromToOption(gtk.HBox):
    def __init__(self):
        super(FromToOption, self).__init__()
        self.from_radio = gtk.RadioButton(label="From")
        self.to_check = gtk.CheckButton("To")
        self.to_check.set_active(True)
        self.from_date = DateTimeWidget()
        self.to_date = DateTimeWidget(datetime.timedelta(seconds=1))
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
    
    def get_dates(self):
        if self.to_check:
            return (self.from_date.get_datetime(),self.to_date.get_datetime())
        else:
            return (self.from_date.get_datetime(),
                    datetime.datetime.fromtimestamp(get_true_time))

    def get_active(self):
        return self.from_radio.get_active()

class LastDateOption(gtk.HBox):
    def __init__(self):
        super(LastDateOption, self).__init__()
        self.last_date_radio = gtk.RadioButton(label='Last')
        self.last_date_adj = gtk.Adjustment(value=1, lower=1, upper=100, step_incr=1)
        self.last_date_spin = gtk.SpinButton(adjustment=self.last_date_adj)
        self.last_date_combo = gtk.combo_box_new_text()
        self.last_date_combo.append_text('seconds')
        self.last_date_combo.append_text('minutes')
        self.last_date_combo.append_text('hours')
        self.last_date_combo.append_text('days')
        self.last_date_combo.set_active(1)
        self.pack_start(self.last_date_radio, False, False)
        self.pack_start(self.last_date_spin, False, False)
        self.pack_start(self.last_date_combo, False, False)

    def get_dates(self):
        end_date = datetime.datetime.fromtimestamp(get_true_time())
        dateunit = [1.*24*60*60,1.*24*60,1.*24,1.]
        active = self.last_date_combo.get_active()
        delta = self.last_date_spin.get_value()/dateunit[active]
        start_date = end_date-datetime.timedelta(delta)
        return (start_date, end_date)

    def get_active(self):
        return self.last_date_radio.get_active()

class ThisOption(gtk.HBox):
    def __init__(self):
        super(ThisOption, self).__init__()
        self.this_date_radio = gtk.RadioButton(label='This')
        self.this_date_combo = gtk.combo_box_new_text()
        self.this_date_combo.append_text('hour')
        self.this_date_combo.append_text('day')
        self.this_date_combo.append_text('week')
        self.this_date_combo.append_text('month')
        self.this_date_combo.set_active(0)
        self.pack_start(self.this_date_radio, False, False)
        self.pack_start(self.this_date_combo, False, False)

    def get_dates(self):
        end_date = datetime.datetime.fromtimestamp(get_true_time())
        start_hour = datetime.datetime(end_date.year,
            end_date.month,
            end_date.day,
            end_date.hour
        )
        start_day = datetime.datetime(end_date.year,
            end_date.month,
            end_date.day
        )
        start_month = datetime.datetime(end_date.year,
            end_date.month, 1
        )
        start_week = datetime.datetime(end_date.year,
            end_date.month,
            end_date.day-end_date.weekday()
        )
        this_date = [start_hour, start_day, start_week, start_month]
        start_date = this_date[self.this_date_combo.get_active()]
        print start_date
        print end_date
        return (start_date, end_date)

    def get_active(self):
        return self.this_date_radio.get_active()

class DateFilter(CommonFilter):
    def __init__(self):
        super(DateFilter, self).__init__("Date")
        self.date_box = gtk.VBox()
        self.last_option = LastDateOption()
        self.fromto_option = FromToOption()
        self.this_option = ThisOption()
        self.fromto_option.from_radio.set_group(self.last_option.last_date_radio)
        self.this_option.this_date_radio.set_group(self.last_option.last_date_radio)
        self.fromto_option.from_radio.set_active(True)
        self.add(self.date_box)
        self.date_box.pack_start(self.last_option, False, False)
        self.date_box.pack_start(self.fromto_option, False, False)
        self.date_box.pack_start(self.this_option, False, False)
        self.set_start_active(True)

    @property
    def get_dates(self):
        if self.last_option.get_active():
            return self.last_option.get_dates()
        elif self.fromto_option.get_active():
            return self.fromto_option.get_dates()
        elif self.this_option.get_active():
            return self.this_option.get_dates()


