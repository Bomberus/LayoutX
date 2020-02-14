# Declarative tkinter UI with reactive data binding

![Banner](src-docs/img/Banner_no_bg.png)

# Features
- Drag and Drop support (tkDnD)
- Supports async by default (powered by asyncio)
- Two-way data binding
- Flexible layout by design
- Application scrolls automatically
- Simple layout syntax powered by Pug (former Jade)
- Widget parameter support inline python scripting
- ttk themes included
- Lightweight and fast
- Add any custom tkinter widget

![Designer](src-docs/img/designer.GIF)

# Installation
Make sure your python installation is 3.7 or higher.

You need the tk extension **tkDnD** for this framework. 
This can be automatically installed via pip argument. Make sure the python directory is writable (e.g. on Mac OSX, Python library are installed to /System/Library, which cannot be modified, even with sudo!).

```pip install layoutx``` (minimal version)

```pip install layoutx[more_widgets, styles]``` (full version)

```python -m layoutx.install_tkdnd``` (install tkdnd)

The command line tool: `lxdesigner` can be used to easily design some forms.

For lxdesigner to function, you need to install addon **more widgets**.

# Addons
Some dependencies of this project have a GPL v3 license. They are excluded into separate addons.
Please note by installing these dependencies, you confirm to the GPL license agreement.

This project itself is licensed under MIT.

## more widgets:
More information see: [ttkwidgets Github](https://github.com/TkinterEP/ttkwidgets/)

 - Input
 - ComboBox
 - TextArea
 - Scale

```pip install layoutx[more_widgets]```

## ttk themes:
More information see: [ttkthemes Github](https://github.com/TkinterEP/ttkthemes)

```pip install layoutx[styles]```

# Getting started

``` python
from layoutx        import app # Import the app singleton
from layoutx.store  import create_store
from layoutx.view   import View, ResizeOption

store = create_store({}, { "name": "World" })

class RootView(View):
  geometry = "250x50+100+100"
  title = "My first app"
  resizable = ResizeOption.NONE
  template = """\
ScrollFrame
  Box(orient="horizontal")
    Label Hello
    Input(value="{{name}}")
  Button(command="{say_my_name}") Say my name!
"""
  def say_my_name(self):
    print(self.store.state["name"])

if __name__ == "__main__":
  app.setup(store=store, rootView=RootView)
  app.run()
```

![Getting Started](src-docs/img/index/getting-started.png)

# Documentation

Read the [documentation](https://bomberus.gitlab.io/LayoutX/) for more information.
