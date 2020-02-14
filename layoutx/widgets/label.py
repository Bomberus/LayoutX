from .widget     import Widget
from tkinter     import ttk


class Label(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(tk=ttk.Label(master=master), **kwargs)
