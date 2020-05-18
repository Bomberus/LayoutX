from .widget     import Widget
from tkinter     import ttk, StringVar

class SpinBox(Widget):
  def __init__(self, master, **kwargs):
    self._textv = StringVar()
    super().__init__(
      tk=ttk.Spinbox(master, textvariable=self._textv), **kwargs
    )
    self._setter = self.connect_to_prop("value", self.on_changed_value)
    self._trace = self._textv.trace_add("write", 
      lambda *_: self._setter(self._textv.get())
    )

  def on_changed_value(self, value):
    if value:
      self._textv.set(value)

  def on_disposed(self):
    self._textv.trace_remove("write", self._trace)
    self._setter = None