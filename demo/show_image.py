from layoutx        import app
from layoutx.store  import create_store
from layoutx.view   import View, ResizeOption

store = create_store({
  "SET_IMAGE": lambda state, payload: {**state, **{"data": payload}} 
}, { "data": "" })

class ImageShowcase(View):
  geometry = "800x600+200+200"
  title = "ImageViewer"
  resizable = ResizeOption.NONE
  template= """\
Box
  Label(weight="0") Image Viewer
  ImageViewer(name="image" background="black" imagedata="{data}")
  Button(weight="0" height="20" command="{load_image}") New Image
"""

  async def load_image(self):
    # Find view child widget api not yet finalized
    imageViewer = self._widget.find_first("image")
    
    # Get tkinter attributes
    height  = imageViewer.widget.tk.winfo_height()
    width   = imageViewer.widget.tk.winfo_width()

    import aiohttp
    import io
    from random import randint

    imagedata = None
    session = aiohttp.ClientSession()
    async with session.get(f"http://placekitten.com/{width}/{height}?image={randint(0,17)}") as imageResource:
      from PIL import Image, ImageTk
      load = Image.open(io.BytesIO(await imageResource.read()))
      imagedata = ImageTk.PhotoImage(load)
    await session.close()
    self.store.dispatch("SET_IMAGE", imagedata)

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

if __name__ == "__main__":
  app.setup(store=store, rootView=ImageShowcase)
  app.run()