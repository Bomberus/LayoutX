from .widget     import Widget
from tkinter     import ttk
from ttkwidgets  import Calendar as CalendarWidget


class Calendar(Widget):
  def __init__(self, master,**kwargs):   
    super().__init__(tk=CalendarWidget(master=master), **kwargs)

    self._setter = self.connect_to_prop("value", self.on_changed_value)
    setattr(self._tk, "_pressed", self.on_item_pressed)

  def on_item_pressed(self, evt):
    self._tk._pressed(evt)
    print(self._tk._selection)

  def on_changed_value(self, value):
    
    #self._tk._show_selection()
    pass