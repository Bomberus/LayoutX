import logging
import weakref
import inspect
import tkinter      as tk
from enum import Enum
from .store  import Store
from ._parser import parse_pug_to_obj
from traceback import format_exc
from inspect   import iscoroutine
from os import path

__all__ = [ "ResizeOption", "View" ]

class ResizeOption(Enum):
  NONE   = (0, 0)
  BOTH   = (1, 1)
  X_ONLY = (1, 0)
  Y_ONLY = (0, 1)


class View:
  template: str = ''
  title = "New Window"
  geometry = "800x600+100+100"
  resizable = ResizeOption.BOTH
  icon = None

  def __init__(self, store:Store, tkinter = None, logger=None):    
    self._store = weakref.proxy(store)
    self._widget = None
    self._logger = weakref.proxy(logger) if logger else logging.getLogger(self.__class__.__name__)
    self._logger.setLevel(logging.DEBUG)
    self._tk = tkinter if tkinter else tk.Toplevel()

    if self.icon == None:
      import inspect
      from pathlib import Path
      self.icon = Path(inspect.getfile(inspect.currentframe())).parent / 'resources' / 'favicon.gif'

    menu = self.set_menu()
    if menu:
      self._set_menu(menu)
    self.set_title(self.title)
    self.set_geometry(self.geometry)
    self.set_resizable(self.resizable)

  def _init(self):
    self._templateTree = parse_pug_to_obj(self.template)
    from layoutx import app
    view_name = self.__class__.__name__ 
    self._node = app.get_view(view_name)
    self._widget = self._node.add_widget(
      node=self._templateTree
    )
    if path.isfile(self.icon):
      icon = tk.PhotoImage(file=self.icon)
      self._node.app._tk.call('wm', 'iconphoto', self._tk, icon)
    self._widget.widget.tk.pack(side="top", fill="both", expand=True)

  def set_menu(self):
    return None
  
  def set_resizable( self, resizable: ResizeOption ):
    self._tk.resizable(*resizable.value)
  
  def set_geometry( self, geometry: str):
    self._tk.geometry(geometry)
  
  def set_title( self, title:str ):
    self._tk.title(title)

  def show( self ):
    self.redraw()
    self._tk.deiconify()

  def hide( self ): 
    self._tk.withdraw()

  @property
  def tk(self):
    return self._tk
  
  @property
  def container(self):
    return self._tk

  @property
  def logger(self):
    return self._logger

  @property
  def store(self) -> Store:
    return self._store

  def redraw(self, template=None):
    try:
      if self._widget:
        from layoutx import app
        view_node = app.get_view(self.__class__.__name__)
        view_node.clear_children()
    finally:
      self._widget = None
    if template:
      self.template = template
    self._init()

  def execute_in_loop(self, method=None):
    if not callable(method):
      # Nothing to evaluate
      return method

    def wrapper(*args, **kwargs):
      loop = self._node.app.loop
      logger = self._logger

      try:
        co = method(*args, **kwargs)
            
        if co and iscoroutine(co):
          loop.create_task(co)
      except:
        if logger:
          logger.warn(f"Error executing method")
          logger.warn(format_exc())
    return wrapper

  def dispose(self):
    if isinstance(self._tk, tk.Tk):
      raise ValueError("Cannot dispose main window, use app.close()")
    if self._widget:
      from layoutx import app
      view_node = app.get_view(self.__class__.__name__)
      view_node.clear_children()
    self._widget = None
    if self._tk:
      self._tk.destroy()
    self._tk = None

  def _set_menu(self, menu_tree: dict):
    def tree_traverse(menu_bar: tk.Menu, tree: dict):
      for key, value in tree.items():
        if isinstance(value, dict):
          submenu = tk.Menu(menu_bar, tearoff=0)
          menu_bar.add_cascade(label=key, menu=tree_traverse(submenu, value))
        else:
          menu_bar.add_command(label=key, command=self.execute_in_loop(value))
      return menu_bar

    menubar = tree_traverse(menu_bar=tk.Menu(self._tk), tree=menu_tree)
    self._tk.config(menu=menubar)