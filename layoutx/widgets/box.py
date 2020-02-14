from .widget     import Widget
from tkinter     import ttk


class Box(Widget):
  def __init__(self, master,**kwargs):   
    if kwargs.get("node").text:
      super().__init__(tk=ttk.LabelFrame(master=master), **kwargs)
    else:
      super().__init__(tk=ttk.Frame(master=master), **kwargs)

  