from .widget     import Widget
from tkinter     import ttk, IntVar

class ProgressBar(Widget):
  def __init__(self, master, **kwargs):
    self._value = IntVar()
    super().__init__(tk=ttk.Progressbar( 
      master=master, 
      variable=self._value ), **kwargs)
    self.connect_to_prop("value", self.on_changed_value)

  def on_changed_value(self, value):
    self._value.set(int(value))

  def on_disposed(self):
    self._value = None