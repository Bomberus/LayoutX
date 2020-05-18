from .widget     import Widget
from tkinter     import ttk, StringVar

class RadioButton(Widget):
  def __init__(self, master, **kwargs):
    self._v = StringVar()
    super().__init__(
      tk=ttk.Radiobutton(
        master, 
        variable=self._v), **kwargs
    )
    self._setter = self.connect_to_prop("value", self.on_changed_value)
    self._setter = self.connect_to_prop("sel", self.on_changed_sel)
    self._trace = self._v.trace_add("write", 
      lambda *_: self._setter(self._v.get())
    )

  def on_changed_sel(self, value):
    self._v.set(value)

  def on_changed_value(self, value):
    self._tk.config(value=value)

  def on_disposed(self):
    self._v.trace_remove("write", self._trace)
    self._setter = None