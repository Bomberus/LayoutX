import tkinter.ttk as ttk
import tkinter     as tk
from .widget import Widget
from layoutx.utils import is_windows


class AutoScrollbar(ttk.Scrollbar):
  def set(self, lo, hi):
    if float(lo) <= 0.0 and float(hi) >= 1.0:
      if self.grid_info():
        self.grid_remove()
    else:
      if not self.grid_info():
        self.grid()
    super().set(lo, hi)


class ScrollFrame(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(tk=ttk.Frame(master=master), **kwargs)
    self._canvas = tk.Canvas(self._tk, borderwidth=0, background="#ffffff")          #place canvas on self

    self._viewPort = ttk.Frame(self._canvas)                    #place a frame on the canvas, this frame will hold the child widgets 
    
    self._tk.grid_columnconfigure(0, weight=1)
    self._tk.grid_columnconfigure(1, weight=0)
    self._tk.grid_rowconfigure(0, weight=1)
        
    self._vsb = AutoScrollbar(self._tk, orient="vertical", command=self._canvas.yview) #place a scrollbar on self
    self._vsb.grid(row=0, column=1, sticky='ns')
    self._canvas.configure(yscrollcommand=self._vsb.set)
        
    self._canvas.bind('<Enter>', self._bound_to_mousewheel)
    self._canvas.bind('<Leave>', self._unbound_to_mousewheel)
    self._canvas.grid(row=0, column=0, sticky="nswe")
    self._window = self._canvas.create_window(0, 0, window=self._viewPort, anchor="nw")            #add view port frame to canvas
    
    self._viewPort.bind("<Configure>", self._on_frame_configure)                       #bind an event whenever the size of the viewPort frame changes.
    self._canvas.bind("<Configure>", self._on_canvas_configure)

  @property
  def container(self):
    return self._viewPort

  def _bound_to_mousewheel(self, event):
    if is_windows():
      self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    else:      
      self._canvas.bind_all("<Button-4>", self._on_mousewheel) 
      self._canvas.bind_all("<Button-5>", self._on_mousewheel)

  def _unbound_to_mousewheel(self, event):
    if is_windows():
      self._canvas.unbind_all("<MouseWheel>")
    else:
      self._canvas.unbind_all("<Button-4>") 
      self._canvas.unbind_all("<Button-5>")  

  def _on_mousewheel(self, event):
    delta = 1 if (event.num == 5 or event.delta == -120) else -1
    if self._canvas.winfo_height() < self._viewPort.winfo_height():
      self._canvas.yview_scroll(delta, "units")      

  def _on_canvas_configure(self, event):
    self._canvas.itemconfig(self._window, width=event.width)
    #self._canvas.itemconfig(self._window, height=event.height)

  def _on_frame_configure(self, event):                                              
    self._canvas.configure(scrollregion=self._canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

  def on_disposed(self):
    self._vsb.destroy()
    self._canvas.destroy()
    self._mainFrame.destroy()