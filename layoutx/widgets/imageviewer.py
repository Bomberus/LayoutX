import os
import math
import hashlib
import warnings
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from .scroll_frame import AutoScrollbar
from .widget     import Widget
from pathlib import Path

MAX_IMAGE_PIXELS = 1500000000  # maximum pixels in the image, use it carefully

class ImageViewer(Widget):  
  def __init__(self, master, **kwargs):
    self._canvasImage = CanvasImage()
    self._canvasImage.init(master)
    super().__init__(tk=self._canvasImage._CanvasImage__imframe, **kwargs)
    self.connect_to_prop("value", self._on_image_changed)
  
  def _on_image_changed(self, path):
    if not isinstance(path, str) or Path(path).exists() and path != '':
      if self._canvasImage.busy:
        self._canvasImage.queue = path
      else:
        #self._canvasImage._CanvasImage__imframe.update()
        #self._canvasImage.canvas.update()
        try:
          self._canvasImage.new_image(path)
          self._canvasImage._CanvasImage__center_img()
          self._canvasImage._CanvasImage__show_image()
        except:
          self._canvasImage.path = ""
          self._canvasImage.busy = False
          self._canvasImage.init = False
        


class CanvasImage:
  busy = False
  queue = ""
  path = ""
  init_widget = False
  master = None

  def _on_resize(self, *_):
    #self.master.grid_columnconfigure(0, weight=1)
    #self.master.grid_rowconfigure(0, weight=1)
    self.__imframe.grid_columnconfigure(0, weight=1)
    self.__imframe.grid_rowconfigure(0, weight=1)
    self.__imframe.update()

  def new_image(self, path):
    self.queue = ""
    self.busy = True
    self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
    self.__delta = 1.3  # zoom magnitude
    self.__filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
    self.__previous_state = 0  # previous state of the keyboard
    self.path = path  # path to the image, should be public for outer classes
    # Decide if this image huge or not
    self.__huge = False  # huge or not
    self.__huge_size = 14000  # define size of the huge image
    self.__band_width = 1024  # width of the tile band
    Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS  # suppress DecompressionBombError for big image
    with warnings.catch_warnings():  # suppress DecompressionBombWarning for big image
      warnings.simplefilter('ignore')
      self.__image =  Image.open(self.path)  # open image, but down't load it into RAM
    self.imwidth, self.imheight = self.__image.size  # public for outer classes
    if self.imwidth * self.imheight > self.__huge_size * self.__huge_size and \
            self.__image.tile[0][0] == 'raw':  # only raw images could be tiled
      self.__huge = True  # image is huge
      self.__offset = self.__image.tile[0][2]  # initial tile offset
      self.__tile = [self.__image.tile[0][0],  # it have to be 'raw'
               [0, 0, self.imwidth, 0],  # tile extent (a rectangle)
               self.__offset,
               self.__image.tile[0][3]]  # list of arguments to the decoder
    self.__min_side = min(self.imwidth, self.imheight)  # get the smaller image side
    # Create image pyramid
    self.__pyramid = [self.smaller()] if self.__huge else [Image.open(self.path)]
    # Set ratio coefficient for image pyramid
    self.__ratio = max(self.imwidth, self.imheight) / self.__huge_size if self.__huge else 1.0
    self.__curr_img = 0  # current image from the pyramid
    self.__scale = self.imscale * self.__ratio  # image pyramide scale
    self.__reduction = 2  # reduction degree of image pyramid
    (w, h), m, j = self.__pyramid[-1].size, 512, 0
    n = math.ceil(math.log(min(w, h) / m, self.__reduction)) + 1  # image pyramid length
    while w > m and h > m:  # top pyramid image is around 512 pixels in size
      j += 1
      w /= self.__reduction  # divide on reduction degree
      h /= self.__reduction  # divide on reduction degree
      self.__pyramid.append(self.__pyramid[-1].resize((int(w), int(h)), self.__filter))
    # Put image into container rectangle and use it to set proper coordinates to the image
    self.wrapper = self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)
    # Create MD5 hash sum from the image. Public for outer classes
    self.md5 = hashlib.md5(self.__pyramid[0].tobytes()).hexdigest()
    #self.__center_img()
    #self.__show_image()  # show image on the canvas
    self.canvas.focus_set()  # set focus on the canvas
    self.busy = False
    self.init_widget = True
    if self.queue != "":
      self.new_image(self.queue)

  """ Display and zoom image """
  def init(self, placeholder):
    """ Initialize the ImageFrame """
    self.master = placeholder
    self.__imframe = ttk.Frame(placeholder)  # placeholder of the ImageFrame object    
    self.__imframe.bind('<Configure>', self._on_resize)

    #setattr(self.__imframe, "grid_forget", self.grid_forget)
    # Vertical and horizontal scrollbars for canvas
    hbar = AutoScrollbar(self.__imframe, orient='horizontal')
    vbar = AutoScrollbar(self.__imframe, orient='vertical')
    hbar.grid(row=1, column=0, sticky='we')
    vbar.grid(row=0, column=1, sticky='ns')
    # Create canvas and bind it with scrollbars. Public for outer classes
    self.canvas = tk.Canvas(self.__imframe, highlightthickness=0,
                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    self.canvas.grid(row=0, column=0, sticky='nswe')
    self.canvas.update()  # wait till canvas is created
    hbar.configure(command=self.__scroll_x)  # bind scrollbars to the canvas
    vbar.configure(command=self.__scroll_y)
    # Bind events to the Canvas
    self.canvas.bind('<Configure>', self.__show_image())  # canvas is resized
    self.canvas.bind('<ButtonPress-1>', self.__move_from)  # remember canvas position
    self.canvas.bind('<B1-Motion>',   self.__move_to)  # move canvas to the new position
    self.canvas.bind('<MouseWheel>', self.__wheel)  # zoom for Windows and MacOS, but not Linux
    self.canvas.bind('<Button-5>',   self.__wheel)  # zoom for Linux, wheel scroll down
    self.canvas.bind('<Button-4>',   self.__wheel)  # zoom for Linux, wheel scroll up

  def smaller(self):
    """ Resize image proportionally and return smaller image """
    w1, h1 = float(self.imwidth), float(self.imheight)
    w2, h2 = float(self.__huge_size), float(self.__huge_size)
    aspect_ratio1 = w1 / h1
    aspect_ratio2 = w2 / h2  # it equals to 1.0
    if aspect_ratio1 == aspect_ratio2:
      image = Image.new('RGB', (int(w2), int(h2)))
      k = h2 / h1  # compression ratio
      w = int(w2)  # band length
    elif aspect_ratio1 > aspect_ratio2:
      image = Image.new('RGB', (int(w2), int(w2 / aspect_ratio1)))
      k = h2 / w1  # compression ratio
      w = int(w2)  # band length
    else:  # aspect_ratio1 < aspect_ration2
      image = Image.new('RGB', (int(h2 * aspect_ratio1), int(h2)))
      k = h2 / h1  # compression ratio
      w = int(h2 * aspect_ratio1)  # band length
    i, j, n = 0, 0, math.ceil(self.imheight / self.__band_width)
    while i < self.imheight:
      j += 1
      print('\rOpening image: {j} from {n}'.format(j=j, n=n), end='')
      band = min(self.__band_width, self.imheight - i)  # width of the tile band
      self.__tile[1][3] = band  # set band width
      self.__tile[2] = self.__offset + self.imwidth * i * 3  # tile offset (3 bytes per pixel)
      self.__image.close()
      self.__image = Image.open(self.path)  # reopen / reset image
      self.__image.size = (self.imwidth, band)  # set size of the tile band
      self.__image.tile = [self.__tile]  # set tile
      cropped = self.__image.crop((0, 0, self.imwidth, band))  # crop tile band
      image.paste(cropped.resize((w, int(band * k)+1), self.__filter), (0, int(i * k)))
      i += band
    print('\r' + (40 * ' ') + '\r', end='')  # hide printed string
    return image

  @staticmethod
  def check_image(path):
    """ Check if it is an image. Static method """
    # noinspection PyBroadException
    try:  # try to open and close image with PIL
      Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS  # suppress DecompressionBombError for big image
      with warnings.catch_warnings():  # suppress DecompressionBombWarning for big image
        warnings.simplefilter(u'ignore')
        img = Image.open(path)
      img.close()
    except:
      return False  # not image
    return True  # image

  def redraw_figures(self):
    """ Dummy function to redraw figures in the children classes """
    pass
  
  # noinspection PyUnusedLocal
  def __scroll_x(self, *args, **kwargs):
    """ Scroll canvas horizontally and redraw the image """
    self.canvas.xview(*args)  # scroll horizontally
    self.__show_image()  # redraw the image

  # noinspection PyUnusedLocal
  def __scroll_y(self, *args, **kwargs):
    """ Scroll canvas vertically and redraw the image """
    self.canvas.yview(*args)  # scroll vertically
    self.__show_image()  # redraw the image

  def __show_image(self):
    """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
    
    if self.path == '' or self.busy:
      return
    
    box_image = self.canvas.coords(self.wrapper)  # get image area
    box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
            self.canvas.canvasy(0),
            self.canvas.canvasx(self.canvas.winfo_width()),
            self.canvas.canvasy(self.canvas.winfo_height()))
    box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
    # Get scroll region box
    box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
            max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]
    #print("box_canvas", box_canvas)
    #print("box_scroll", box_scroll)
    # Horizontal part of the image is in the visible area
    if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
      box_scroll[0]  = box_img_int[0]
      box_scroll[2]  = box_img_int[2]
    # Vertical part of the image is in the visible area
    if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
      box_scroll[1]  = box_img_int[1]
      box_scroll[3]  = box_img_int[3]
    # Convert scroll region to tuple and to integer
    self.canvas.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region
    x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
    y1 = max(box_canvas[1] - box_image[1], 0)
    x2 = min(box_canvas[2], box_image[2]) - box_image[0]
    y2 = min(box_canvas[3], box_image[3]) - box_image[1]
    if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
      if self.__huge and self.__curr_img < 0:  # show huge image, which does not fit in RAM
        h = int((y2 - y1) / self.imscale)  # height of the tile band
        self.__tile[1][3] = h  # set the tile band height
        self.__tile[2] = self.__offset + self.imwidth * int(y1 / self.imscale) * 3
        self.__image.close()
        self.__image = Image.open(self.path)  # reopen / reset image
        self.__image.size = (self.imwidth, h)  # set size of the tile band
        self.__image.tile = [self.__tile]
        image = self.__image.crop((int(x1 / self.imscale), 0, int(x2 / self.imscale), h))
      else:  # show normal image
        image = self.__pyramid[max(0, self.__curr_img)].crop(  # crop current img from pyramid
                  (int(x1 / self.__scale), int(y1 / self.__scale),
                   int(x2 / self.__scale), int(y2 / self.__scale)))
      #
      imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.__filter))
      imageid = self.canvas.create_image(max(box_canvas[0], box_img_int[0]),
                         max(box_canvas[1], box_img_int[1]),
                         anchor='nw', image=imagetk)
      self.canvas.lower(imageid)  # set image into background
      self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

  def __move_from(self, event):
    """ Remember previous coordinates for scrolling with the mouse """
    if not self.init_widget or self.busy:
      return
    self.canvas.scan_mark(event.x, event.y)

  def __move_to(self, event):
    """ Drag (move) canvas to the new position """
    if not self.init_widget or self.busy:
      return
    self.canvas.scan_dragto(event.x, event.y, gain=1)
    self.__show_image()  # zoom tile and show it on the canvas

  def outside(self, x, y):
    """ Checks if the point (x,y) is outside the image area """
    bbox = self.canvas.coords(self.wrapper)  # get image area
    if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
      return False  # point (x,y) is inside the image area
    else:
      return True  # point (x,y) is outside the image area
  
  def __center_img(self):
    #box_canvas = (self.canvas.canvasx(self.canvas.winfo_width()),self.canvas.canvasy(self.canvas.winfo_height()))
    scale = 1.0
    # Respond to Linux (event.num) or Windows (event.delta) wheel event
    self.__imframe.update()
    target_scale = self.imheight / self.canvas.canvasy(self.canvas.winfo_height())
    sk = round(math.log(target_scale)/math.log(self.__delta))
    self.imscale /= math.pow(self.__delta, sk)
    scale    /= math.pow(self.__delta, sk)
    # Take appropriate image from the pyramid
    k = self.imscale * self.__ratio  # temporary coefficient
    self.__curr_img = min((-1) * int(math.log(k, self.__reduction)), len(self.__pyramid) - 1)
    self.__scale = k * math.pow(self.__reduction, max(0, self.__curr_img))
    self.canvas.scale('all', 0, 0, scale, scale)  # rescale all objects
    
  def __wheel(self, event):
    """ Zoom with mouse wheel """
    if not self.init_widget or self.busy:
      return
    x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
    y = self.canvas.canvasy(event.y)
    if self.outside(x, y): return  # zoom only inside image area
    scale = 1.0
    # Respond to Linux (event.num) or Windows (event.delta) wheel event
    if event.num == 5 or event.delta == -120:  # scroll down, zoom out, smaller
      if round(self.__min_side * self.imscale) < 30: return  # image is less than 30 pixels
      self.imscale /= self.__delta
      scale    /= self.__delta
    if event.num == 4 or event.delta == 120:  # scroll up, zoom in, bigger
      i = float(min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1)
      if i < self.imscale: return  # 1 pixel is bigger than the visible area
      self.imscale *= self.__delta
      scale    *= self.__delta
    # Take appropriate image from the pyramid
    k = self.imscale * self.__ratio  # temporary coefficient
    self.__curr_img = min((-1) * int(math.log(k, self.__reduction)), len(self.__pyramid) - 1)
    self.__scale = k * math.pow(self.__reduction, max(0, self.__curr_img))
    self.canvas.scale('all', x, y, scale, scale)  # rescale all objects
    # Redraw some figures before showing image on the screen
    self.redraw_figures()  # method for child classes
    self.__show_image()

  def crop(self, bbox):
    """ Crop rectangle from the image and return it """
    if self.__huge:  # image is huge and not totally in RAM
      band = bbox[3] - bbox[1]  # width of the tile band
      self.__tile[1][3] = band  # set the tile height
      self.__tile[2] = self.__offset + self.imwidth * bbox[1] * 3  # set offset of the band
      self.__image.close()
      self.__image = Image.open(self.path)  # reopen / reset image
      self.__image.size = (self.imwidth, band)  # set size of the tile band
      self.__image.tile = [self.__tile]
      return self.__image.crop((bbox[0], 0, bbox[2], band))
    else:  # image is totally in RAM
      return self.__pyramid[0].crop(bbox)

  def destroy(self):
    """ ImageFrame destructor """
    self.__image.close()
    map(lambda i: i.close, self.__pyramid)  # close all pyramid images
    del self.__pyramid[:]  # delete pyramid list
    del self.__pyramid  # delete pyramid variable
    self.canvas.destroy()
    self.__imframe.destroy()


if __name__ == "main":
  tkroot = tk.Tk()
  tkroot.geometry("1000x600+200+200")
  tkroot.grid_columnconfigure(0, weight=1)
  tkroot.grid_rowconfigure(0, weight=1)
  image = CanvasImage(tkroot, "/home/pmbremer/Bilder/japan/LAR01756.JPG")
  image.grid(row=0,column=0)
  image._CanvasImage__imframe.update()
  image.canvas.update()
  image._CanvasImage__center_img()
  image._CanvasImage__show_image()
  tkroot.mainloop()