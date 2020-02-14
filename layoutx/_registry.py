from __future__ import annotations
import re
import ast
from enum          import Enum
from copy          import deepcopy
from typing        import List
from functools     import reduce, partial
from .utils import Singleton, safer_eval, safe_get, compile_exp, compile_ast, eval_compiled, set_state
from .view  import View
from ._parser import XMLElement
from .store import Store
import weakref
import asyncio


class WIDGET_LIFECYCLE(Enum):
  CHILDREN_CLEARED = "on_children_cleared"
  CHILDREN_UPDATED = "on_children_updated"
  PLACED           = "on_placed"
  DISPOSE          = "on_dispose"
  INIT             = "on_init"

reserverd_attributes = [
  "ipadx", "ipady", "padx", "pady", "sticky",
  "columnspan", "rowspan", "height", "width",
  "if", "for", "orient", "enabled", "foreground", "background",
  "font", "style", "fieldbackground", "command", "state"
]

non_reactive_attributes = [
  "for", "style", "name", "orient"
]

class RegistryNode:
  def __init__(
    self, 
    widget,
    node: XMLElement = None, 
    name: str = None,
    view: View = None,
    path_mapping = None,
    parent = None):
    
    self._widget = widget
    self._view = view
    if issubclass(self._widget.__class__, View):
      self._view = weakref.proxy(self._widget)

    self._name = name
    self._node = node
    self._nodes = []
    self._parent = weakref.proxy(parent) if parent else None
    self._path_mapping = path_mapping
    self._prop_mapping = {}
  
  def has_node(self, node):
    return node in self._nodes

  def add_widget(self, node:XMLElement, path_mapping = None):
    from layoutx import app
    widget_class = app.get_widget_cls(node.tag)
    widget_node =  self._add_node(
      name=node.get_attribute("name", None),
      widget=None,
      path_mapping=path_mapping if path_mapping else self._path_mapping,
      node=node,
      view=self._view
    )
    widget_node._init_binding()
    widget_node._init_tk(widget_class=widget_class)
    if node.count_children > 0:
      widget_node._init_repeater(node.get_attribute("for"))
    widget_node.widget._init()
    return widget_node

  def remove_node(self, node):
    if self.has_node(node):
      node.dispose()
      self._nodes.remove(node)

  def get_attr(self, key, default=None):
    return self._node.get_attribute(key, default)

  def set_attr(self, key, value):
    self._node.set_attribute(key, value)
  
  @property
  def text(self):
    return self._node.text.rstrip() if self._node.text else None

  @property
  def prop_mapping(self):
    return self._prop_mapping

  @property
  def app(self):
    from layoutx import app
    return app

  @property
  def name(self):
    return self._name  

  @property
  def widget_type(self):
    return self._widget.__class__.__name__

  @property
  def widget(self):
    return self._widget

  @property
  def view(self) -> View:
    return self._view

  @property
  def children(self) -> List[RegistryNode]:
    return self._nodes

  @property
  def parent(self):
    return self._parent

  def filter_children(self, name: str = None, widget_type: str = None):
    if name:
      return [child for child in self.children if child.name == name]
    else:
      return [child for child in self.children if child.widget_type == widget_type]

  @property
  def path(self):
    path = []
    node = self
    while node and node.widget_type != "Application":
      part = ''
      parent = node.parent
      if node.name:
        child_names =  parent.filter_children(name=node.name)
        part = node.name
        if len(child_names) > 1:
          part += f"[{child_names.index(node)}]"
      else:
        child_types = parent.filter_children(widget_type=node.widget_type)
        part = f"!{node.widget_type}"
        if len(child_types) > 1:
          part += f"[{child_types.index(node)}]"

      path.insert(0, part)
      node = node.parent
    
    return '.'.join(path)

  def find_by_name(self, name = ""):
    return self._find(path=f"{name}", skip=True, all=True)

  def find_by_component(self, name):
    return self._find(path=f"{name}", skip=True, all=True)

  def find_all(self, path = str):
    return self._find(path=path.split("."), all=True)

  def find_first(self, path = str):
    found = self._find(path=path.split("."), all=True)
    return found[0] if len(found) > 0 else None
  
  def placed(self):
    self.app.update()
    self._call_child_lifecycle(WIDGET_LIFECYCLE.PLACED)

  def load_children(self, path_mapping=None):
    for child in self._node.children:
      child_widget = self.add_widget(node=child, path_mapping=path_mapping)
      child_widget._call_child_lifecycle(WIDGET_LIFECYCLE.INIT)
    self._call_child_lifecycle(WIDGET_LIFECYCLE.CHILDREN_UPDATED)
    
  def clear_children(self):
    for node in self.children:
      node.dispose()
    self._nodes = []
    self._call_child_lifecycle(WIDGET_LIFECYCLE.CHILDREN_CLEARED)

  def dispose(self):
    for child in self.children:
      child.dispose()
      
    self._call_child_lifecycle(method=WIDGET_LIFECYCLE.DISPOSE)
    if self._prop_mapping:
      for key in self._prop_mapping.keys():
        if "observer" in self._prop_mapping[key]:
          self._prop_mapping[key]["observer"].dispose()
    self._prop_mapping = None
    self._path_mapping = None
    if self._widget:
      self._widget.dispose()
    self._nodes = []
    self._node = None

  def add_prop_subscriber(self, key, subscriber):
    self._prop_mapping[key]["subscriber"].append(subscriber)

  def _call_child_lifecycle(self, method: WIDGET_LIFECYCLE):
    if self._widget:
      cb = getattr(self._widget, method.value, None)
      if cb:
        cb()

  def _init_tk(self, widget_class):
    self._widget = widget_class(node=self, master=self.parent.widget.container)
    self._view.logger.debug(f"INIT Widget: {self.path}")

  def _init_binding(self):
    for key, value in self._node.attributes.items():
      if key in non_reactive_attributes:
        continue
      
      if value[0] == "{" and value[-1] == "}":
        value = value[1:-1]
        isTwoWay = False
        if value[0] == "{" and value[-1] == "}":
          isTwoWay = True
          value = value[1:-1]
        tree = ast.parse(value).body[0].value
        comp = compile_ast(tree, path_mapping=self._path_mapping )
        if isTwoWay:
          self._connect(key, comp, compile_ast(tree, path_mapping=self._path_mapping, mode="exec" ))
        else:
          self._connect_exp(key, comp)
      else:
        self._prop_mapping[key] = {
          "subscriber": [],
          "value": value
        }

    text_exp = self._node.text
    if text_exp:     
      if '{' in text_exp and '}' in text_exp:
        comp = compile_exp(f"f\"\"\"{text_exp}\"\"\"", path_mapping=self._path_mapping)
        self._connect_exp("text", comp)
      else:
        self._prop_mapping["text"] = {
          "subscriber": [],
          "value": text_exp
        }

  def _init_repeater(self, data_for: str):
    if data_for is None:
      self.load_children()
      self._widget.place_children()
      return

    if data_for[0] == "{":
      data_for = data_for[1:-1]
    self._for_target, *self._for_in = data_for.split(' ', 1)
    self._for_in = ''.join(self._for_in)
    #list( (x for x in enumerate([1,2,3]) if x[1] != 2 ) )

    self._gen_exp = f"list( ((index, {self._for_target}) for (index, {self._for_target}) {self._for_in}))"         
    self._for_tree = ast.parse(self._gen_exp).body[0].value
    self._for_iter   = deepcopy(self._for_tree.args[0].generators[0].iter)
    #self._for_ifs    = self._for_tree.args[0].args[0].generators[0].ifs
    #add enumerate to iter 
    #Call(func=Name(id='enumerate', ctx=Load()), args=
    self._for_tree.args[0].generators[0].iter = ast.Call(
      func = ast.Name(id='enumerate', ctx=ast.Load()), 
      keywords=[],
      args=[self._for_iter]
    )
    self._for_tree = ast.fix_missing_locations(self._for_tree)
    self._iter_compiled = compile_ast(
      self._for_tree, 
      path_mapping=self._path_mapping
    )
    
    observer = self._view.store.select_compiled(self._iter_compiled, built_in=self.get_built_in(), logger=self.view.logger)

    self._prop_mapping["iter"] = {
      "observer": observer.subscribe(self._on_changed_children)
    }


  def _add_node(self, widget:str, name:str='', path_mapping=None, node=None, view=None):
    node = RegistryNode(
      widget=widget, 
      name=name,
      node=node,
      parent=self,
      path_mapping=path_mapping, 
      view=self._view)
    self._nodes.append(node)
    return node

  def _connect_exp(self, name: str, comp):
    observer = self._view.store.select_compiled(comp, built_in=self.get_built_in(), logger=self.view.logger)
    self._prop_mapping[name] = {
      "subscriber": [],
      "value": None
    }
    self._prop_mapping[name]["observer"] = observer.subscribe(self._on_prop_changed(name))

    self._view.logger.debug(f"{self.path} [{name}] connect_exp")

  def _connect(self, name: str, comp, comp_set):
    # Check if path mapping for nested path
    
    observer = self._view.store.select_compiled(comp, built_in=self.get_built_in(), logger=self.view.logger)
    self._prop_mapping[name] = {
      "subscriber": [],
      "value": None
    }
    self._prop_mapping[name]["observer"] = observer.subscribe(self._on_prop_changed(name))
    self._prop_mapping[name]["setter"]   = self._set_connect_state_value(comp_set)
    
    self._view.logger.debug(f"{self.path} [{name}] connected")

  def _on_changed_children(self, value):
    if (value == None):
      return
    
    if len(value) == len(self.children):
      return
    
    self.clear_children()
    for index, item in value:
      path_mapping = deepcopy(self._path_mapping) if self._path_mapping else {}
      path_mapping[self._for_target] = ast.Subscript(
        value=self._for_iter, 
        slice=ast.Index(
          value=ast.Constant(
            value=index, 
            kind=None
          )
        ),
        ctx=ast.Load()
      )
      
      self.load_children(path_mapping=path_mapping)
    self._widget.place_children()

  def get_built_in(self):
    built_in_methods = {k:v for k,v in [(meth, getattr(self._view, meth)) for meth in dir(self._view) if callable(getattr(self._view, meth)) and not meth.startswith('_')] } if self._view else {}
    built_in_methods.update(self._view.store.state)
    built_in_methods.update(self._view.store.get_reducers())
    return built_in_methods

  def _set_connect_state_value(self, comp):
    def wrapper(value):
      variables = self.get_built_in()
      set_state(comp, variables, value)

      self._view.store._state.on_next(
        { k:variables[k] for k in self._view.store.state.keys() }
      )
    return wrapper

  def _on_prop_changed(self, name):
    def wrapper(value):      
      if name in self._prop_mapping:
        if self._prop_mapping[name]["value"] == value:
          return
        self._prop_mapping[name]["value"] = value
      
        for cb in self._prop_mapping[name]["subscriber"]:
          cb(self.view.execute_in_loop(value))
          self._view.logger.debug(f"{self.path} [{name}] changed {value}")

    return wrapper

  def _find(self, path = [], skip=False, all=False):
    def read_part(text: str):
      match = re.match(r"^!?(.*?)(\[(.*?)\])?$", text)
      return (match[1], match[3] if match.lastindex > 1 else 0)

    def search_children(childs, path, skip, all):
      found = []
      for child in childs:
        found += child._find(path = path, skip=skip, all=all)
        if len(found) > 0 and not all:
          return found
      return found
    
    if len(path) == 0 or len(self.children) == 0:
      return []

    part, *_path = path
    if part == "*":
      return search_children(childs=self.children, path=_path, skip=True, all=all)
    
    name, index = read_part(part)
    childs = self.filter_children(widget_type=name) if part.startswith("!") else self.filter_children(name=name)

    if index == "*":
      if len(_path) == 0:
        return childs if all else [childs[0]]
      else:
        return search_children(childs, path=_path, skip=skip, all=all)

    if int(index) >= len(childs):
      return search_children(self.children, path=path, skip=skip, all=all) if skip else []
    else:
      if len(_path) == 0:
        return [childs[int(index)]]
      return search_children(childs, path=_path, skip=False, all=all)