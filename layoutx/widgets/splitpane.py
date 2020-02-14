# Modified by me
from .widget import Widget
from tkinter import ttk
from tkinter.constants import HORIZONTAL, VERTICAL


class SplitPane(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(
      tk=ttk.PanedWindow(
        orient=kwargs.get("node").get_attr("orient", HORIZONTAL), 
        master=master), **kwargs)

  def forget_children(self):
    for child in self.tk.panes():
      self.tk.forget(child)

  def place_children(self, changed_value=None):
    self.forget_children()

    index = 0
    for child in self.children:
      if not child.hidden:
        self.tk.add(child.tk)
        self.tk.pane(index, **{
          "weight": int(self.get_attr("weight", "1"))
        })
        index += 1

      child._node.placed()