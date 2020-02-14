The view can be seen as the controller in the classical MVC aspect. The widget can call the views methods.

!!! note
    If you want to call a view method with a parameter from the store, use the **partial** method.


## Methods
Any method inside the view is callable from a widget:

```python tab="View"
class MyView(View):
  def print_greeting(self, value):
    print(value)

```

```pug tab="Layout"
Button(command="{partial(print_greeting,'Hello World')}")
```

## Adding a menu
To set a topbar menu in the window, overwrite the **set_menu** method.


```python
class MyView(View):
  def set_menu(self):
    return {
      "Print": self.print_greeting
    }

  def print_greeting(self):
    print("menu_called")

```

## Find child widget

All Widgets and Views can search itself for corresponding children.

You can search via widget type (put !-Symbol before the type) or widget name.

Additionally you can use the wildcard symbol (*) to search for nested widgets

``` python

view.find_by_name("NamedWidget") # named widget
view.find_all("!Button") # all buttons
view.find_all("!Box.*.!Button") # all buttons that are part of a Box Widget
view.find_first("!Button") # return first button you can find

# If you want to search all views, use the app singleton

from layoutx import app

app.find_all("!Label")

```

## Properties

| Name  | Description             |
|  ---  |   -------------------   | 
| store | Reference to data store |