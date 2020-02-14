from layoutx        import app
from layoutx.store  import create_store
from layoutx.view   import View, ResizeOption
from uuid           import uuid4

store = create_store({
  "DELETE_TODO": lambda state, payload: {**state, **{"todos": list(filter(lambda x: x["id"] != payload, state["todos"])) }},
  "ADD_TODO":    lambda state, *_: {**state, **{"todos": state["todos"] + [{ "id": uuid4(), "text": "Edit me" }] }}
}, {
  "todos": [],
  "selected": -1
})


class ChangeToDoText(View):
  geometry  = "300x50+500+500"
  title     = "Change Text"
  resizable = ResizeOption.NONE
  template = """\
Box Edit Todo: {todos[selected].id}
  Input(value="{{todos[selected].text}}")
"""

class ToDoList(View):
  geometry  = "500x100+200+200"
  title     = "ToDoList"
  resizable = ResizeOption.BOTH
  template  = """\
Box
  ScrollFrame To-Do\'s
    Box(orient="vertical" for="{todo in todos}")
      Box(orient="horizontal")
        Label {todo.text}
        Button(weight="0" command="{partial(change_todo, todo.id)}") Edit
        Button(weight="0" command="{partial(DELETE_TODO, todo.id)}") Del
  Button(weight="0" command="{ADD_TODO}") Add Todo
"""
  
  # private attributes
  _editView = None
  
  def change_todo(self, todo_id):
    list_id = next((i for i, x in enumerate(self.store.state["todos"]) if x["id"] == todo_id), -1)
    if list_id == -1:
      return
    
    self.store.dispatch("SET_VALUE", {
      "path": ["selected"],
      "value": list_id
    })
    if not self._editView or self._editView._tk.winfo_exists() == 0:
      self._editView = app.add_view( ChangeToDoText(store=store) ).widget
      self._editView.show()
 
if __name__ == "__main__":
  app.setup(store=store, rootView=ToDoList)
  app.run()