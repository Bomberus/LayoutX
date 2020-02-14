from .widget     import Widget
import tkinter   as tk
from ..tkDnD import DND_FILES


class DropTarget(Widget):
  def __init__(self, master, **kwargs):
    self._cmd_drop_begin  = None
    self._cmd_drop        = None
    self._cmd_drop_end    = None
    super().__init__(tk=tk.Canvas(
      master = master
    ), **kwargs)
    self._redraw = lambda *_: self._draw("Drop here", "blue")
    self._tk.bind( "<Configure>", self._redraw)
    self._tk.drop_target_register(DND_FILES)
    self._tk.dnd_bind('<<DropEnter>>', self._drop_begin)
    self._tk.dnd_bind('<<DropLeave>>', self._drop_end)
    self._tk.dnd_bind('<<Drop>>', self._drop)
    self._draw("Drop here", "blue")

    self.connect_to_prop("on_drop_begin", self._on_drop_begin_command)
    self.connect_to_prop("on_drop",       self._on_drop_command)
    self.connect_to_prop("on_drop_end",   self._on_drop_end_command)
  
  def _on_drop_begin_command(self, value):
    pass

  def _on_drop_command(self, value: str):
    self._cmd_drop = value

  def _on_drop_end_command(self, value):
    pass

  def _draw(self, text: str, color: str):
    width  = self._tk.winfo_width()
    height = self._tk.winfo_height()

    self._tk.delete("all")
    self._tk.create_rectangle(0, 0, width, height, fill=color)
    self._tk.create_text(width / 2 - 10, height / 2 - 4,
      anchor="center", 
      font=("Purisa", 16),
      text=text,
      fill="white"
    )

  def _drop_begin(self, event):
    self._draw("Release mouse to add File", "orange")

  def _drop_end(self, event):
    self._draw("GIMME FILE!!!", "red")

  def _drop(self, event):
    self._draw("Drop here", "blue")
    if event.data and self._cmd_drop:
        files = self._tk.tk.splitlist(event.data)
        for f in files:
          self._cmd_drop(**{ "path": f })
    return event.action

  def on_disposed(self):
    self._tk.unbind("<Configure>", self._redraw)