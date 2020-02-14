from .widget import Widget
from tkinter import ttk


class Sep(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(tk=ttk.Separator(
      master=master
    ), **kwargs)