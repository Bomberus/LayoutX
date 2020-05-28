from .widget import Widget
from tkinter import ttk, IntVar


class CheckBox(Widget):
  def __init__(self, master, **kwargs):
    self._value = IntVar()
    super().__init__(
      tk=ttk.Checkbutton(
        master=master, 
        variable=self._value
      ), **kwargs
    )

    self._setter = self.connect_to_prop("value", self.on_changed_value)
    self._trace = self._value.trace_add("write",
      lambda *_: self._setter(self._value.get())
    )
    
  def on_changed_value(self, value):
    self._value.set(value)

  def on_disposed(self):
    self._value.trace_remove("write", self._trace)
    self._value = None
    self._setter = None
  