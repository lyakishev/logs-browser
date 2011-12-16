import gtk


class ProgressBar(gtk.ProgressBar):

    class BreakException(Exception): pass
    class StopException(Exception): pass

    def __init__(self, signals, stop_break_sens):
        gtk.ProgressBar.__init__(self)
        self.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.dfrac = None
        self.frac = 0
        self.signals = signals
        self.stop_break_sens = stop_break_sens

    def begin(self, count):
        self.dfrac = (1./count) if count else 0
        self.clear()
        self.stop_break_sens(True)

    def wrap_action(self, action, *args):
        while gtk.events_pending():
            gtk.main_iteration()
        action(*args)
        while gtk.events_pending():
            gtk.main_iteration()

    def execute(self, action, undo_actions, info_text, *action_args):
        if info_text:
            self.set_text(info_text)
        self.wrap_action(action, *action_args)
        if self.signals['break']:
            self.set_text("Stopping...")
            self.stop_break_sens(False)
            for undo_action in undo_actions:
                self.wrap_action(undo_action)
            raise self.BreakException
        elif self.signals['stop']:
            self.set_text("Breaking...")
            self.stop_break_sens(False)
            for undo_action in undo_actions:
                self.wrap_action(undo_action)
            raise self.StopException

    def add_frac(self):
        self.frac += self.dfrac
        self.set_fraction(self.frac)

    def set_frac(self, val):
        self.set_fraction(self.dfrac*val)

    def undo_all(self):
        pass

    def end(self):
        self.clear()
        self.signals['stop'] = False
        self.signals['break'] = False
        self.stop_break_sens(False)

    def clear(self):
        self.set_text("")
        self.set_fraction(0.0)
        self.frac = 0
