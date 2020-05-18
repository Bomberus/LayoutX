from .widget     import Widget
from tksheet import Sheet as tkSheet

class Sheet(Widget):
  def __init__(self, master,**kwargs):
    self._tksheet = tkSheet(master)
    super().__init__(tk=self._tksheet, **kwargs)

    self.connect_to_prop("theme", self._on_theme_changed)
    self.connect_to_prop("headers", self._on_headers_changed)
    self._setter = self.connect_to_prop("value", self._on_value_changed)
    self.connect_to_prop("highlight", self._on_highlight_changed)
    self.connect_to_prop("editable", self._on_editable_changed)
    
    self._tksheet.extra_bindings([
      ("edit_cell", self._on_data_edited),
      ("rc_delete_row", self._on_data_edited),
      ("rc_delete_column", self._on_data_edited),
      ("rc_insert_column", self._on_data_edited),
      ("rc_insert_row", self._on_data_edited),
      ("ctrl_z", self._on_data_edited),
      ("delete_key", self._on_data_edited),
      ("ctrl_v", self._on_data_edited),
      ("ctrl_x", self._on_data_edited)
    ])

    self._editable = True
    self._tksheet.enable_bindings((
      "single_select",
      "copy",
      "cut",
      "paste",
      "delete",
      "undo",
      "edit_cell"
    ))

  def _on_data_edited(self, *_):
    self._setter(self._tksheet.get_sheet_data(return_copy=True))

  def _on_theme_changed(self, value):
    self._tksheet.change_theme(value)
  
  def _on_headers_changed(self, value):
    self._tksheet.headers(value)

  def _on_highlight_changed(self):
    #self.sheet.highlight_cells(row = 5, column = 5, bg = "#ed4337", fg = "white")
    #self.sheet.dehighlight_cells(self, row = 0, column = 0, cells = [], canvas = "table", all_ = False, redraw = True):
    #self.sheet.get_highlighted_cells
    pass
  
  def _on_value_changed(self, value):
    self._tksheet.set_sheet_data(value)

  def _on_editable_changed(self, value):
    self._editable = value
    self._tksheet.disable_bindings()
    if (self._editable):
      self._tksheet.enable_bindings(
        "single_select",
        "copy",
        "cut",
        "paste",
        "delete",
        "undo",
        "edit_cell"
      )
    else:
      self._tksheet.enable_bindings(
        "single_select",
        "copy",
        "cut",
        "paste",
        "delete",
        "undo",
        "edit_cell"
      )

  def on_disposed(self):
    self._tksheet = None