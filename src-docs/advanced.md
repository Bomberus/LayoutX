## Creating your own widgets

Create a new class, that inherits the layoutx **Widget** class.

Import any tkinter widget and pass it to the **tk** attribute.

If you want to listen to changes on a specific attribute, use **connect_to_prop**

```python
from layoutx.widgets import Widget
from tkinter import ttk
class ImageViewer(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(tk=ttk.Label(master=master), **kwargs)
    self.connect_to_prop("imagedata", self.on_imagedata_changed)
  
  def on_imagedata_changed(self, imagedata):
    if imagedata == '':
      return
    self._tk.configure(image=imagedata)

app.add_custom_widget("ImageViewer", ImageViewer)
```

## Create a subview

```python
class RootView(View):
  ...
  _childView = None

  def create_child(self):
    class ChildView(View):
      geometry  = "300x50+500+500"
      title     = "Child Window"
      resizable = ResizeOption.NONE
      template = """\
    Box Child Window
    """

    # check if child exists
    if not self._childView or self._childView._tk.winfo_exists() == 0:
      self._childView = app.add_view( ChildView(store=store) ).widget
      self._childView.show()

```

## Security aspects
Please note to offer dynamic expressions, **eval** and **exec** are used.
But in order to increase security the ast is parsed before executing.

Some expression, like accessing private attributes like: `data.__class__` is prohibited by default.

!!! danger
    Never dynamically create views from user input!

## Package your application
As an example, this is how you would package the designer with pyinstaller.

1. `pip install pyinstaller`
2. `python -O -m PyInstaller --noconsole --icon="layoutx/resources/favicon.ico"  --hidden-import="pkg_resources.py2_warn" layoutx\tools\designer.py`
3. Distribute dist/designer folder

## React to tkinter widget events
You can add a method to a tkinter native event, by specifying a widget attribute with surrounding double points. Then specify a view method that should be called, when the event is triggered.

```pug
  Label(:Button-1:="{partial(print_hello, 'label clicked')}") {name}
```

## Change default font
The fonts in the project might look a bit off. By default the application picks the first font it finds on the system. You can manually specify a font via app setup. Make sure the font is installed on the system.

```python
app.setup(store=store, rootView=RootView, font={"family": "roboto", "size": "14"})
```

!!! note
    Some python distribution (like conda) do not include necessary font libraries in unix distribution. 
    This might lead to missing anti-alias feature for fonts.