from .widget import Widget
from tkinter import ttk
from tkinter.constants import HORIZONTAL, VERTICAL

class Notebook(Widget):
  def __init__(self,master, **kwargs):
    super().__init__(
      tk=ttk.Notebook(
        master=master), **kwargs)
  
  def forget_children(self):
    for child in self.tk.tabs():
      self.tk.forget(child)

  def place_children(self, changed_value=None):
    self.forget_children()

    for child in self.children:
      if child and not child.hidden:
        self.tk.add(child.tk, text=child.text)

        child._node.placed()