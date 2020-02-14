from .widget     import Widget
from tkinter     import ttk, StringVar


class Button(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(
      tk = ttk.Button(master=master), **kwargs)
