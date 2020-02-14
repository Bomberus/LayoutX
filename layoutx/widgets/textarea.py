from .widget              import Widget
import tkinter            as tk
from tkinter              import Frame, Text, Scrollbar, Pack, Grid, Place, INSERT, END, Toplevel, Listbox
from tkinter.constants    import RIGHT, LEFT, Y, BOTH
from tkinter.font         import Font, BOLD, nametofont
from .scroll_frame        import AutoScrollbar
from pygments.styles      import get_style_by_name
from pygments.lexers      import get_lexer_by_name
from ttkwidgets.autocomplete import AutocompleteEntryListbox


class ScrolledText(Text):
  def __init__(self, master=None, **kw):
    self.frame = Frame(master)
    self.vbar = AutoScrollbar(self.frame, orient="vertical")
    self.vbar.grid(row=0, column=1, sticky="ns")
    self.frame.grid_columnconfigure(0, weight=1)
    self.frame.grid_columnconfigure(1, weight=0)
    self.frame.grid_rowconfigure(0, weight=1)

    kw.update({'yscrollcommand': self.vbar.set})
    Text.__init__(self, self.frame, **kw)
    self.vbar['command'] = self.yview
    Text.grid(self, row=0, column=0, sticky="news")
    
    # Copy geometry methods of self.frame without overriding Text
    # methods -- hack!
    text_meths = vars(Text).keys()
    methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
    methods = methods.difference(text_meths)

    for m in methods:
      if m[0] != '_' and m != 'config' and m != 'configure' and m not in ["grid", "pack"]:
        setattr(self, m, getattr(self.frame, m))

  def __str__(self):
    return str(self.frame)

  def pack(self, *args, **kwargs):
    self.frame.pack(*args, **kwargs)
    #self.frame.pack_propagate(False)

  def grid(self, *args, **kwargs):
    self.frame.grid(*args, **kwargs)

class TextArea(Widget):
  def __init__(self, master, **kwargs):
    super().__init__(tk=ScrolledText(master=master, wrap=tk.WORD), **kwargs)
    self._spaces = '  '
    self._lexer  = None
    self._lexer_style = None
    self._autocomplete_list = None
    self._tk.bind('<KeyRelease>', self._set_data)
    self._tk.bind('<Tab>', self._tab_to_spaces)
    self._tk.bind('<Return>', self._autoindent)
    self._tk.bind("<Control-KeyRelease-plus>", self._increase_size)
    self._tk.bind("<Control-KeyRelease-minus>", self._decrease_size)
    self._tk.bind("<Control-KeyRelease-space>", self._autocomplete)
    self._value_setter = self.connect_to_prop("value", self.on_changed_value)
    self.connect_to_prop("spaces", self._on_changed_spaces)
    self.connect_to_prop("language", self._on_changed_language)
    self.connect_to_prop("highlightstyle", self._on_changed_highlightstyle)
    self.connect_to_prop("autocomplete", self._on_changed_autocomplete)

  def _on_changed_autocomplete(self, value):
    self._autocomplete_list = value

  def _autocomplete(self, event):
    if not self._autocomplete_list or len(self._autocomplete_list) == 0:
      return

    index = self._tk.index(INSERT).split(".")
    self._text_index = '.'.join(index)
    tw = Toplevel(self._tk)
    tw.wm_overrideredirect(True)

    font = self._get_font()
    font_size = int(font.cget("size"))

    tw.geometry(f"+{ self._tk.winfo_rootx() + int(index[1]) * int(font_size / 2) }+{ self._tk.winfo_rooty() + int(index[0]) * font_size }")

    self._listbox = AutocompleteEntryListbox(tw, font=font, allow_other_values=False, completevalues=[v["name"] for v in self._autocomplete_list])
    self._listbox.pack()

    tw.lift()
    tw.focus_force()
    tw.grab_set()
    tw.grab_release()

    self._listbox.focus_force()

    self._listbox.listbox.bind("<Double-Button-1>", self._autocomplete_selected)
    self._listbox.entry.bind("<Return>", self._autocomplete_selected)
    self._listbox.bind("<Leave>", self._autocomplete_destroy)
    self._listbox.bind("<Escape>", self._autocomplete_destroy)

    self._autocomplete_window = tw

  def _autocomplete_selected(self, event):
    value = next(v["value"] for v in self._autocomplete_list if v["name"] == self._listbox.get())

    self._tk.insert(self._text_index, value)
    
    self._listbox.event_generate("<Leave>")

  def _autocomplete_destroy(self, event):
    if self._autocomplete_window:
      self._autocomplete_window.destroy()
      self._autocomplete_window = None
      self._tk.focus_force()
      self._tk.mark_set("insert", self._text_index)

  def _get_font(self):
    return nametofont(self.get_style_attr('font'))

  def _increase_size(self, event):
    font = self._get_font()
    font.configure(size=int(font.cget("size") + 1))
    #self._tk.configure(font=font)

  def _decrease_size(self, event):
    font = self._get_font()
    font.configure(size=int(font.cget("size") - 1))
    #self._tk.configure(font=font)

  def _highlight(self):
    if not self._lexer:
      return
    code = self._get_text()
    
    self._tk.mark_set("range_start", "1" + ".0")

    for token, value in self._lexer.get_tokens(code):
      if len(value) == 0:
        continue
      self._tk.mark_set("range_end", "range_start + %dc" % len(value))
      self._tk.tag_add(str(token), "range_start", "range_end")
      self._tk.mark_set("range_start", "range_end")

  def _on_changed_highlightstyle(self, value):
    self._lexer_style = get_style_by_name(value)
    self._tk.configure(
      background=self._lexer_style.background_color,
      insertbackground=self._lexer_style.highlight_color,
      foreground=self._lexer_style.highlight_color)
    
    for tag in self._tk.tag_names():
      self._tk.tag_delete(tag)

    for token, value in self._lexer_style.styles.items():
      token_value = value.split(' ')
      foreground = list(filter(lambda x: x.startswith("#"), token_value))
      
      if len(foreground) == 0:
        continue
      
      if str(token) == "Token.Text":
        self._tk.configure(
          insertbackground=foreground[0],
          foreground=foreground[0])

      self._tk.tag_configure(str(token), foreground=foreground[0])

    
    self._highlight()

  def _on_changed_language(self, value):
    if value:
      self._lexer = get_lexer_by_name(value)

  def _on_changed_spaces(self, value):
    self._spaces = ''.join([" "] * int(value))

  def _autoindent(self, event):
    indentation = ""
    lineindex = self._tk.index("insert").split(".")[0]
    linetext = self._tk.get(lineindex+".0", lineindex+".end")

    for character in linetext:
      if character in [" ","\t"]:
        indentation += character
      else:
        break
                
    self._tk.insert(self._tk.index("insert"), "\n"+indentation)
    return "break"

  def _tab_to_spaces(self, event):
    self._tk.insert(self._tk.index("insert"), self._spaces)
    return "break"

  def _get_text(self):
    return self._tk.get("1.0", tk.END)[:-1]

  def _set_data(self, event):
    if self._value_setter:
      self._value_setter(self._get_text())
    
  def on_changed_value(self, value):
    index = self._tk.index(tk.INSERT)
    self._tk.delete("1.0", tk.END)
    self._tk.insert(tk.END, value)
    self._tk.mark_set("insert", index)
    self._tk.see(index)
    
    self._highlight()

  def on_disposed(self):
    self._tk.unbind('<KeyRelease>')