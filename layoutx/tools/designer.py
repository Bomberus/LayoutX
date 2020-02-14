from layoutx             import app
from layoutx.store       import create_store
from layoutx.view        import View, ResizeOption
import asyncio
import ast
import logging
import sys


def create_view(template, methods):
  newline = '\n'
  exec(f"""
class DemoView(View):
  geometry = "400x400+900+100"
  title = "Demo"
  template = \"\"\"{template}\"\"\"

{ newline.join([f"  {line}" for line in methods.split(newline)]) }
""")

  return eval("DemoView")

store = create_store({}, {
  "data": """\
{
  "name": "news",
  "counter": 0,
  "isBool": True,
  "code": "import antigravity"
}""",
  "template": """\
ScrollFrame
  Button(command="{partial(print_hello, name)}") asyncio
  Button(command="{reducer}")
    | Hello {name}
  Label(:Button-1:="{partial(print_hello, 'label clicked')}") {name}
  Label hello {getter()}
""",
  "view": """\
async def print_hello(self, txt, *args):
  import asyncio
  await asyncio.sleep(1)
  print("tkEvent", args)
  print(txt)

def getter(self):
  return 'dynamic getter'

def on_drop(self, path):
  print(path)

def reducer(self):
  self.store.dispatch("SET_NAME", "from reducer")
""",
  "store": """\
{
  "SET_NAME": lambda state, payload: {**state, **{"name": payload}}
}
"""
})

class RootView(View):
  geometry = "800x600+100+100" 
  title = "Designer"
  template = """\
SplitPane(orient="vertical")
  SplitPane
    Box Template
      TextArea(autocomplete="{get_autocomplete()}", highlightstyle="monokai", spaces="2", language="pug" value="{{template}}")
    Box Store data
      TextArea(highlightstyle="monokai", spaces="2", language="json" value="{{data}}" )
  SplitPane
    Box View Methods
      TextArea(highlightstyle="monokai", spaces="2", language="python" value="{{view}}")
    Box Store Reducer
      TextArea(highlightstyle="monokai", spaces="2", language="python" value="{{store}}")
"""
  demoView = None
  demoStore = None
  
  def get_autocomplete(self):
    return [{
      "name": "Label",
      "value": "Label hello"
    },{
      "name": "Button",
      "value": "Button(command=\"{cmd}\")"
    },
    {
      "name": "Box",
      "value": "Box(orient=\"vertical\")"
    },{
      "name": "SplitPane",
      "value": "SplitPane"
    },{
      "name": "ComboBox",
      "value": "ComboBox(value='{{name}}', suggestion=['1','2'])"
    },{
      "name": "CheckBox",
      "value": "CheckBox(value='{{isBool}}') Check me"
    },{
      "name": "DropTarget",
      "value": "DropTarget(on_drop=\"{on_drop}\")"
    },{
      "name": "TextArea",
      "value": "TextArea(highlightstyle='monokai', spaces='2', language='python', value='{{code}}' )"
    },{
      "name": "ScrollFrame",
      "value": "ScrollFrame"
    },{
      "name": "Scale",
      "value": "Scale(value='{{counter}}' to=\"100\")"
    },{
      "name": "Input",
      "value": "Input(value='{{name}}' suggestion=['1', '2'])"
    }]

  def set_menu(self):
    return {
      "Reload UI": self.update_ui,
      "Update Data": self.update_data,
      "Import Example": self.import_data,
      "Export Example": self.export_data
    }
  
  @property
  def _get_state(self):
    return self._store.state

  def export_data(self):
    from tkinter import filedialog
    import json
    filename = filedialog.asksaveasfilename(filetypes=[('LxDesign File', '.lxconfig')], defaultextension=".lxconfig")
    if filename:
      with open(filename, "w", encoding='utf-8') as dataFile:
        dataFile.writelines(json.dumps(self._get_state))


  def import_data(self):
    from tkinter import filedialog, messagebox
    try:
      data = filedialog.askopenfilename(filetypes=[('LxDesign File', '.lxconfig')], defaultextension=".lxconfig")
      if data is None:
        return
      with open(data, "r", encoding='utf-8') as dataFile:
        self.store._state.on_next( ast.literal_eval(dataFile.read() ))
    except:
      messagebox.showerror("Error", "Import Data not valid")

  def _create_view(self):
    self.demoStore = create_store(eval(self._get_state["store"]), ast.literal_eval(self._get_state["data"]))
    view_class = create_view(self._get_state["template"], self._get_state["view"])
    self.demoView = app.add_view(view_class(store=self.demoStore)).widget

    if len(self.demoView.logger.handlers) == 0:
      handler = logging.StreamHandler(sys.stdout)
      handler.setLevel(logging.DEBUG)
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      handler.setFormatter(formatter)
      self.demoView.logger.addHandler(handler)
    self.demoView.show()

  def update_ui(self):
    if self.demoView:
      self.demoView.redraw(self._get_state["template"])
    else:
      self._create_view()

  def update_data(self):
    if self.demoStore:
      self.demoStore._state.on_next(ast.literal_eval(self._get_state["data"]))
    else:
      self._create_view()

  def update_store(self):
    self._create_view()

def main():
  app.setup(store=store, rootView=RootView)
  app.run()

if __name__ == "__main__":
  app.setup(store=store, rootView=RootView)
  app.run()