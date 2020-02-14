from .widget     import Widget
import tkinter   as tk
from tkinter     import ttk, END
from tkinter.scrolledtext import ScrolledText
import logging
import re


class Logger(Widget):
  class LoggingFilter(logging.Filter):
    def filter(self, record):
      return record.level == self._level and re.match(self._regex_filter, record.message)


  class Handler(logging.Handler):
    def __init__(self, widget):
      logging.Handler.__init__(self)
      self.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
      self._tk = widget
      self._tk.config(state='disabled')

    def emit(self, record):
      self._tk.config(state='normal')
      if record.msg.startswith("INIT"):
        self._tk.insert(END, self.format(record) + "\n", "init")
      elif record.msg.startswith("DISPOSE"):
        self._tk.insert(END, self.format(record) + "\n", "dispose")
      else:
        self._tk.insert(END, self.format(record) + "\n")
      self._tk.see(END)
      self._tk.config(state='disabled')
  
  def __init__(self, **kwargs):
    self._tk = ScrolledText(master=kwargs.get("master").container)
    Widget.__init__(self, **kwargs)

    self.logging_handler = Logger.Handler(self._tk)

    self._logger.addHandler(self.logging_handler)
    self._level = self.get_attr("level", "DEBUG")
    self._regex_filter = self.get_attr("filter", ".*")
  
  def on_changed_level(self, value):
    self._level = value
    self._setFilters()

  def on_changed_filter(self, value):
    self._regex_filter = value
    self._setFilters()
  
  def clear(self):
    self._tk.delete("1.0", tk.END)

  def _setFilters(self):
    for log_filter in self.logging_handler.filters:
      self.logging_handler.removeFilter(log_filter)

    self.logging_handler.addFilter(LoggingFilter)

  def dispose(self):
    self._logger.removeHandler(self.logging_handler)
    super().dispose()
