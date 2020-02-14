from layoutx._registry          import RegistryNode
from layoutx.view               import View
from layoutx.utils              import get_os
from ast                        import literal_eval
import re
import logging
import weakref
import tkinter
from tkinter import font as tkFont
from functools import partial
from tkinter.constants import HORIZONTAL, VERTICAL


possible_cursors = ["X_cursor","arrow","based_arrow_down","based_arrow_up","boat","bogosity","bottom_left_corner","bottom_right_corner","bottom_side","bottom_tee","box_spiral","center_ptr","circle","clock","coffee_mug","cross","cross_reverse","crosshair","diamond_cross","dot","dotbox","double_arrow","draft_large","draft_small","draped_box","exchange","fleur","gobbler","gumby","hand1","hand2","heart","icon","iron_cross","left_ptr","left_side","left_tee","leftbutton","ll_angle","lr_angle","man","middlebutton","mouse","pencil","pirate","plus","question_arrow","right_ptr","right_side","right_tee","rightbutton","rtl_logo","sailboat","sb_down_arrow","sb_h_double_arrow","sb_left_arrow","sb_right_arrow","sb_up_arrow","sb_v_double_arrow","shuttle","sizing","spider","spraycan","star","target","tcross","top_left_arrow","top_left_corner","top_right_corner","top_side","top_tee","trek","ul_angle","umbrella","ur_angle","watch","xterm"]

if get_os() == "Windows":
  possible_cursors += ["no","starting","size","size_ne_sw","size_ns","size_nw_se","size_we","uparrow","wait"]
if get_os() == "Darwin":
  possible_cursors += ["copyarrow","aliasarrow","contextualmenuarrow","text","cross-hair","closedhand","openhand","pointinghand","resizeleft","resizeright","resizeleftright","resizeup","resizedown","resizeupdown","none","notallowed","poof","countinguphand","countingdownhand","countingupanddownhand","spinning"]


class Widget:
  def __init__(self, node: RegistryNode, tk: tkinter.Widget ):
    self._node   = node
    self._tk     = tk
    self._hidden = False
    self._style_name = None
    self._font = None

  # Helper Properties
    
  @property
  def hidden(self):
    return self._hidden
  
  @property
  def path(self):
    return self._node.path

  @property
  def parent(self):
    return self._node.parent

  @property
  def view(self) -> View:
    return self._node.view

  @property
  def children(self):
    return [child.widget for child in self._node.children]

  @property
  def store(self):
    return self.view.store

  @property
  def tk(self):
    return getattr(self, "_tk")

  @property
  def text(self):
    return self._node.text

  @property
  def container(self):
    return self._tk

  def _init(self):   
    properties = self.tk.keys()
    if "style" in properties:
      orient_style = ""
      if "orient" in properties:
        orient_style = "Horizontal." if self.tk.cget("orient") == "horizontal" else "Vertical."
      self._style_name = f"{self.get_attr('style', self.path)}.{ orient_style }{self.tk.winfo_class()}"
      self._configure_tk("style", self._style_name)

    # Font Handling
    sysfontName = None
    if self._style_name:
      # ttk
      sysfontName = self._get_app_style().lookup(self._style_name, 'font')
    else:
      # tk
      if "font" in self._tk.keys():
        sysfontName = self._tk.cget('font')
    
    if sysfontName and sysfontName.startswith("Tk"):
      font = tkFont.nametofont(sysfontName).actual()
      font.update(self._get_app_config("font"))
      self._font = tkFont.Font(**font)
      self._apply_style_attribute("font", self._font)
      
    # Read Layout Attributes
    for prop in [prop for prop in self._node.prop_mapping.keys() if prop not in ["style", "value"]]:
      if prop == "if":
        self.connect_to_prop("if", self._on_changed_visibility)
      elif prop == "enabled":
        self.connect_to_prop("enabled", self._on_changed_state)
      elif prop == "cursor":
        self.connect_to_prop("cursor", self._on_changed_cursor)
      elif prop == "font":
        self.connect_to_prop("font", self._on_changed_font)
      elif prop == "foreground":
        self.connect_to_prop("foreground", self._on_changed_foreground)
      elif prop == "fieldbackground":
        self.connect_to_prop("fieldbackground", self._on_changed_fieldbackground)
      elif prop == "background":
        self.connect_to_prop("background", self._on_changed_background)
      elif self.parent.widget.tk and prop in ["weight", "pad", "ipadx", "ipay", "padx", "pady", "columnspan", "rowspan", "sticky", "minsize"]:
        self.connect_to_prop(prop, self.parent.widget.place_children)
      elif prop in properties:
        self.connect_to_prop(prop, partial(self._configure_tk, prop))
      elif prop[0] == ":" and prop[-1] == ":":
        self.connect_to_prop(prop, partial(self._on_bind_event, f"<{prop[1:-1]}>"))
  
  # Lifecycle Methods
  def on_init(self):
    pass

  def on_children_cleared(self):
    pass
  
  def on_children_updated(self):
    pass
  
  def on_placed(self):
    pass
  
  def on_disposed(self):
    pass

  def get_style_attr(self, key, default=None):
    if key in self.tk.keys():
      return self._tk.cget(key)
    elif self._style_name:
      return self._get_app_style().lookup(self._style_name, key)

    return None


  def get_attr(self, key, default=None):
    if key in self._node.prop_mapping:
      return self._node.prop_mapping[key]["value"]
    else:
      return self._node.get_attr(key, default)

    return default
  def set_attr(self, key, value):
    if key in self._node.prop_mapping:
      self._node.prop_mapping[key]["value"] = value

  def connect_to_prop(self, key, fn_changed=None):
    if key in self._node.prop_mapping:
      if fn_changed:
        self._node.add_prop_subscriber(key, fn_changed)
        fn_changed(self.view.execute_in_loop(self.get_attr(key)))
      return self._node.prop_mapping[key].get("setter")
  
  def set_prop_value(self, key, value):
    if key in self._node.prop_mapping:
      if "setter" in self._node.prop_mapping[key]:
        self._node.prop_mapping[key]["setter"](value)

  def forget_children(self):
    for child in self.children:
      child.tk.grid_forget()
  
  def place_children(self, changed_value = None):
    self.forget_children()

    index = 0
    orientation = self.get_attr("orient", VERTICAL)

    if orientation == VERTICAL:
      self.container.grid_columnconfigure(0, weight=1)
    else:
      self.container.grid_rowconfigure(0, weight=1)
    
    for child in self.children:
      if not child.hidden:
        
        grid_info = {
          "padx":   int(child.get_attr("padx", "0")), 
          "pady":   int(child.get_attr("pady", "0")),
          "ipadx":  int(child.get_attr("ipadx", "0")),
          "ipady":  int(child.get_attr("ipady", "0")),
          "columnspan": int(child.get_attr("columnspan", "1")),
          "rowspan": int(child.get_attr("rowspan", "1")),
          "sticky": child.get_attr("sticky", "news")
        }
        
        if orientation == VERTICAL:
          grid_info["column"] = 0
          grid_info["row"] = index
          self.container.grid_rowconfigure(
            index, 
            pad=int(child.get_attr("pad", "0")), 
            minsize=int(child.get_attr("minsize", "0")),
            weight=int(child.get_attr("weight", "1")))
        else:
          grid_info["row"] = 0
          grid_info["column"] = index
          self.container.grid_columnconfigure(
            index, 
            pad=int(child.get_attr("pad", "0")), 
            minsize=int(child.get_attr("minsize", "0")),
            weight=int(child.get_attr("weight", "1")))
        child.tk.grid(**grid_info)
        index += 1
      child._node.placed()

  def hide_child(self):
    self.place_children()
 
  def show_child(self):
    self.place_children()
    
  def dispose(self):
    self.view.logger.debug(f"DISPOSE widget {self.path}")
    self._tk.destroy()

  # internal methods
  def _get_app_style(self):
    return self._node.app.style

  def _get_app_config(self, key):
    return self._node.app.config.get(key, None)

  def _configure_tk(self, name, value):
    if name in self.tk.keys():
      self.tk.configure(**{name: value})

  def _on_bind_event(self, name, value):
    self._tk.bind(name, self.view.execute_in_loop(value))

  def _on_changed_cursor(self, value):
    if not value in possible_cursors:
      self.view.logger.error(f"cursor: {value} not supported!")
      return
    self._configure_tk("cursor", value)

  def _on_changed_font(self, value):
    if "family" in value and not value["family"] in list(tkFont.families()):
      self.view.logger.error(f"font-family: { value['family'] } not installed!")
      return
    self._font.configure(**value)

  def _apply_style_attribute(self, key, value):
    if key in self.tk.keys():
      self._configure_tk(key, **value) if isinstance(value, dict) else self._configure_tk(key, value)
    elif self._style_name:
      self._get_app_style().configure(self._style_name, **{ key: value })
  
  def _on_changed_background(self, value):
    self._apply_style_attribute("background", value)

  def _on_changed_fieldbackground(self, value):
    self._apply_style_attribute("fieldbackground", value)
  
  def _on_changed_foreground(self, value):
    self._apply_style_attribute("foreground", value)
  
  def _on_changed_visibility(self, value):
    self._hidden = not bool(value)
    if not self.parent:
      return

    if value:
      self.parent.widget.show_child()
    else:
      self.parent.widget.hide_child()
  
  def _on_changed_state(self, value):
    if value:
      self._configure_tk("state", "normal")
    else:
      self._configure_tk("state", "disabled")