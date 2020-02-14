from .container import Container
from tkinter    import ttk


class Notebook(Container):
  def __init__(self, **kwargs):
    self._tk = ttk.Notebook(
      master=kwargs.get("master").container
    )
    self._tk.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    Container.__init__(self, **kwargs)
    self._reserved_attr += ["text"]

  def _on_tab_changed(self, event):
    if "index" in self._prop_mapping:
      self.set_connect_state_value("index", self._tk.select())    

  def on_changed_index(self, value):
    if value != "":
      self._tk.select(value)

  def _change_tab_text(self, child):
    def wrapper(value):
      self._tk.tab(child, text = value)
    return wrapper

  def apply_children_grid(self):
    # Calculate text
    for index, child in enumerate(self._children):
      # Clear old observer      
      for key in list(self._prop_mapping.keys()).copy():
        if key.startswith("childtext_"):
          self._prop_mapping[key]["observer"].dispose()
          del self._prop_mapping[key]
      
      self._tk.add(child.tk)
      
      observer = self._view.store.select_exp(exp = f"f\"\"\"{self.text}\"\"\"", path_mapping=child._path_mapping)
      self._prop_mapping[f"childtext_{index}"] = {
        "observer": observer.subscribe(self._change_tab_text(child.tk))
      }

  def clear_children(self):
    for child in self._children:
      self._tk.forget(child.tk)
      child.dispose()
    self._children = []

  def hide_child(self, widget):
    self._tk.hide(widget)
  
  def show_child(self, widget):
    self._tk.add(widget)

  def dispose(self):
    self._tk.unbind("<<NotebookTabChanged>>")
    super().dispose()