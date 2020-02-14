from .widget        import Widget
from .label         import Label
from .input         import Input
from tkinter        import ttk
from copy           import deepcopy


class FormItem(Container):
  def __init__(self, **kwargs):   
    self._tk = ttk.Frame(
      master=kwargs.get("master").container)

    kwargs.get("node").attrib["orient"] = "horizontal"
    super().__init__(**kwargs)

    label_node = deepcopy(self._node)
    label_node.tag = "Label"
    del label_node.attrib["value_type"]
    del label_node.attrib["orient"]

    self.init_child(label_node, self._path_mapping)

    value_type = self.get_attr("value_type", None)
    if value_type:
      self.on_changed_value_type(value_type)
  
  def on_changed_value_type(self, value):
    data_node = deepcopy(self._node)
    del data_node.attrib["value_type"]
    del data_node.attrib["orient"]

    if value == "Input":
      data_node.tag = "Input"
    else:
      return

    if self.children_count == 2:
      child = self._children.pop(1)
      child.dispose()
    
    self.init_child(data_node, self._path_mapping)

    self.apply_children_grid()

