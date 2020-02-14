from .widget     import Widget
from tkinter     import ttk, StringVar
from ttkwidgets.autocomplete  import AutocompleteCombobox


class ComboBox(Widget):
  def __init__(self, master, **kwargs):
    self._textv = StringVar()
    super().__init__(
      tk=AutocompleteCombobox(
        master=master,
        textvariable=self._textv
      ),**kwargs
    )
    self._setter = self.connect_to_prop("value", self.on_changed_value)
    self._trace = self._textv.trace_add("write", 
      lambda *_: self._setter(self._textv.get())
    )
    self.connect_to_prop("suggestion", self.on_changed_suggestion)

  def on_changed_suggestion(self, value):
    self._tk.set_completion_list(value if value else [])

  def on_changed_value(self, value):
    self._textv.set(value)

  def on_disposed(self):
    self._textv.trace_remove("write", self._trace)
    self._setter = None
