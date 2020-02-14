from .widget import Widget
from tkinter  import IntVar, ttk
from ttkwidgets import TickScale

class TkTickScale(ttk.Frame):
  def __init__(self, master, orient, **kwargs):
    super().__init__(master)
    self.scale = TickScale(self, orient=orient, **kwargs)
    self.orient = orient
    if orient == "horizontal":
      self.scale.pack(fill="x")
    else:
      self.scale.pack(fill="y")

  def configure(self, **kwargs):
    self.scale.configure(**kwargs)

  def cget(self, name):
    return self.scale.cget(name)

  def keys(self):
    return self.scale.keys()

  def winfo_class(self):
    return f"{self.orient.capitalize()}.TScale"

class Scale(Widget):
  def __init__(self, master, **kwargs):
    self._valuev = IntVar()
    super().__init__(tk=TkTickScale(
      master=master,
      orient=kwargs.get("node").get_attr("orient","horizontal"),
      variable=self._valuev), **kwargs)
    self._setter = self.connect_to_prop("value", self.on_changed_value)
    self._trace = self._valuev.trace_add("write", 
      lambda *_: self._setter(self._valuev.get())
    )

  def on_changed_value(self, value):
    self._valuev.set(int(value))

  def on_disposed(self):
    self._valuev.trace_remove("write", self._trace)
    self._valuev = None
    self._setter = None  