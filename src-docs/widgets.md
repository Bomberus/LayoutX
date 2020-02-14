## BaseWidget
The BaseWidget has no visual representation, but all other widgets inherit it. It provides some lifecycle methods and attributes to ease widget development.

### Boilerplate

This is a simple example that creates a tkinter label widget.
The **TK** parent widget is always passed to the init method via the name **master**.

```python
from layoutx.widgets import Widget
from tkinter     import ttk

class MyWidget(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(tk=ttk.Label(master=master), **kwargs)

```

### Lifecycle Methods

Lifecycle Methods can be hooked into, to change the behavior of the widget in runtime. For example, if additional data needs to be cleaned up, if the widget is disposed. You can hook into these methods, by extending the base class methods.

```python
class MyWidget(Widget):
  # We overwrite Parent Lifecycle method
  def on_init(self):
    print("I was created")
  
  def on_dispose(self):
    print("I am about to be disposed")
```

| Name | Description |
| ---  | ---         |
| on_init | tkinter widget is created, databinding is already usable  |
| on_placed | widget was placed in parent |
| on_disposed | called before widget is disposed (use it for cleanup tasks that are unique to this widget) |
| on_children_cleared | child widgets are cleared  |
| on_children_updated | child widgets were placed  |

### Internal Properties

To ease development some properties are provided for each widget.
Access them directly via `self.<property>`.

| Name |  Description   | DataType    |
| ---  |  ---           |   ---       |
| hidden |    is widget hidden    |  Boolean    |
| path | a unique path in the registry tree, that represents this widget | String |
| view | the parent view | layoutx.view.View |
| children | own children tkinter widgets | [ Tk.Widget ] |
| store | the data store | layoux.store.Store |
| tk | own tkinter widget | Tk.Widget |
| text | Text given from layout declaration | string \| None |
| container | In case the widget consists of multiple tkinter widget, use this attribute to specify where to place children widgets | Tk.Widget |

### Helper Methods

In order to ease widget interaction with the view and data store this is abstracted by helper methods.

!!! important
    Please note that you do not need to manually watch any tkinter property with **connect_to_prop**. The Framework automatically listen to changes for these properties and forwards them to the tkinter widget.

    Automatically watched properties include:
      - tkinter widget keys
      - ["ipadx", "ipady", "padx", "pady", "sticky",
        "columnspan", "rowspan", "height", "width",
        "if", "for", "orient", "enabled", "foreground", "background", "font", "style", "fieldbackground"]

    Keep that in mind when developing custom widgets

| Name |  Description  |  Pseudocode     |
| ---  |  ---          |  ---            |
| get_attr | Get current value of widget attribute, if None use specified default value | `get_attr("background", "grey")`  |
| set_attr | Set value of widget attribute | set_attr("background", "red")  |
| set_prop_value | Same as set_attr but notifies Store | `set_prop_value("background", "red")` |
| connect_to_prop | Subscribe to changes of a widget attribute, if changes to the attribute are possible will return a setter method, to pass value changes to |  `connect_to_prop("background", self._on_changed_mybackground)` |

### Style Compatibility

The framework adds an compatibility layer, so the basic styling options: 

- font
- background
- foreground
- fieldbackground

can still be used with ttk widgets.


## Widgets Example
### Label

#### Simple

``` pug
Label A new Label
```

#### Multiline

``` pug
Label 
  | first line
  | second line
```

### Box
A collection widget, it aligns childs vertical by default.


#### Horizontal

``` pug
Box(orient="horizontal")
```

#### Vertical

``` pug
Box
```

### Input

!!! important
    When use pass suggestion using static binding, exclude the double quotes!

```pug
  Input(value='{{name}}' suggestion=['1', '2'])
```

### ComboBox

!!! important
    When use pass suggestion using static binding, exclude the double quotes!

```pug
  ComboBox(value='{{name}}', suggestion=['1','2'])
```

### DropTarget

```pug
  DropTarget(on_drop="{on_drop}")
```

!!! important
    Do not forget to include a view method (on_drop) in this case

### Button

```pug
  Button(command="{cmd}")
```

### Textarea

```pug
  TextArea(highlightstyle='monokai', spaces='2', language='python', value='{{code}}' )
```

!!! note
    Highlighting powered by pygments

### SplitPane

```pug
  SplitPane
    Box 1
    Box 2
```

### Scale

```pug
  Scale(value='{{counter}}' to="100")
```

### CheckBox

```pug
  CheckBox(value='{{isBool}}') Check me
```