from .widget import Widget
from tkinter import ttk


class TreeDisplay(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(
      tk=ttk.Treeview(master), **kwargs)

    self.connect_to_prop("value", self._on_value_changed)
    self.connect_to_prop("header", self._on_header_changed)

  def _clear(self):
    self._tk.delete(*self._tk.get_children())

  def _set_children(self, treeNode, value):
    for i, item in enumerate(value):
      childNode = self._tk.insert(treeNode, 'end', text=item["text"], values=item["values"])
      if "children" in item:
        self._set_children(childNode, item["children"])

  def _on_header_changed(self, value):
    self._tk["columns"]= list(k for k in value.keys() if k != "#0")
    
    for key, v in value.items():
      if "column" in v:
        self._tk.column(key, **v["column"])
      if "heading" in v:
        self._tk.heading(key, **v["heading"])

  def _on_value_changed(self, value):
    self._clear()

    for item in value:
      treeNode = self._tk.insert('', 'end', text=item["text"], values=item["values"], open=False)
      if "children" in item:
        self._set_children(treeNode, item["children"])