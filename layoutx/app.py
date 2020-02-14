import tkinter           as tk
import tkinter.font      as tkFont
from .store              import Store
from .view               import View, ResizeOption
from .utils              import Singleton, is_windows
from ._registry           import RegistryNode
from .tkDnD              import TkinterDnD
import logging
import asyncio

__all__ = ["Application"]

@Singleton
class Application(RegistryNode):
  def __init__(self):
    super().__init__(widget = self, name = "app")

    #Import Widgets
    import layoutx.widgets
    self._widgets = {}
    for name in layoutx.widgets.__all__:
      self._widgets.update({name : getattr(layoutx.widgets, name)})

    self._tk = None
    self._loop = None
    self._root_node = None
    self._style = None
    self._config = {}

  def setup(self, store: Store, rootView: View, font=None, style: str=None, interval=1/120, loop=None):
    if not self._tk:
      self._tk = TkinterDnD.Tk()
      self._loop = loop if loop else asyncio.get_event_loop()
      self._tk.protocol("WM_DELETE_WINDOW", self.close)
      self._ui_task = self._loop.create_task(self._updater(interval))

    # Pick first system font as default if none given
    if font:
      self._config["font"] = font 
    else:
      if is_windows():
        self._config["font"] = {"family": "Courier New", "size": 12} if "Courier New" in tkFont.families() else {"family":tkFont.families()[1], "size": 12}
      else:
        self._config["font"] = {"family": "DejaVu Sans Mono", "size": 12} if "DejaVu Sans Mono" in tkFont.families() else {"family":tkFont.families()[1], "size": 12}
    
    if style and not self._style:
      try:
        from ttkthemes import ThemedStyle
        self._style   = ThemedStyle(self._tk)
        self._style.set_theme(style)
      except ImportError:
        # ttkstyles not installed
        self._style   = tk.ttk.Style()
    else:
      self._style   = tk.ttk.Style()

    if self._root_node:
      self.remove_node(self._root_node)
    
    self._root_node = self.add_view(
      rootView(
        tkinter=self._tk,
        store=store
      )
    )
    self._root_node.widget.redraw()

  @property
  def loop(self):
    return self._loop

  def close(self):
    self._ui_task.add_done_callback(lambda *_: self._cleanup())
    self._ui_task.cancel()

  @property
  def config(self):
    return self._config
  
  @property
  def style(self):
    return self._style

  def run( self ):
    self._loop.run_forever()
    self._loop.close()

  def get_root_node(self) -> RegistryNode:
    return self._root_node

  def get_view(self, name: str) -> RegistryNode:
    filter_view = self.filter_children(name=name)
    if len(filter_view) == 1:
      return filter_view[0]
    else:
      raise ValueError(f"View {name} not registed")
    
  def add_view(self, view: View) -> RegistryNode:
    name = view.__class__.__name__
    old_view = self.filter_children(name=name)
    if len(old_view) > 0:
      self.remove_node(old_view[0])
    if len(self.children) > 0: 
      view.hide()
    return self._add_node(widget=view, name=view.__class__.__name__)

  def add_custom_widget(self, name, cls):
    if name in self._widgets:
      raise ValueError(f"Widget name: {name} already exists")
    
    self._widgets[name] = cls

  def update(self):
    self._tk.update()

  def get_widget_cls(self, name):
    if name not in self._widgets:
      raise KeyError(f"Widget: {name}, does not exist or was never added to the registry")
    return self._widgets[name]

  async def _updater(self, interval):
    while True:
      self.update()
      await asyncio.sleep(interval)

  def _cleanup(self):
    self._loop.stop()
    self._tk.destroy()
