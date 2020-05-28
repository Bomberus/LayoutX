# Original Author: Miguel Martinez Lopez#
# Uncomment the next line to see my email
# print("Author's email: %s"%"61706c69636163696f6e616d656469646140676d61696c2e636f6d".decode("hex"))
# Modified by Bomberus
# Licensed under the MIT License
from .widget     import Widget
import tkinter as Tkinter
from tkinter     import ttk, StringVar
import tkinter.font as tkFont
import calendar
import datetime
from tkinter.constants import CENTER, LEFT, RIGHT, N, E, W, S

"""
These are the default bindings:
    Click button 1 on entry: Show calendar
    Click button 1 outsite calendar and entry: Hide calendar
    Escape: Hide calendar
    CTRL + PAGE UP: Move to the previous month.
    CTRL + PAGE DOWN: Move to the next month.
    CTRL + SHIFT + PAGE UP: Move to the previous year.
    CTRL + SHIFT + PAGE DOWN: Move to the next year.
    CTRL + LEFT: Move to the previous day.
    CTRL + RIGHT: Move to the next day.
    CTRL + UP: Move to the previous week.
    CTRL + DOWN: Move to the next week.
    CTRL + END: Close the datepicker and erase the date.
    CTRL + HOME: Move to the current month.
    CTRL + SPACE: Show date on calendar
    CTRL + Return: Set current selection to entry
"""

def get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)


class Calendar(ttk.Frame):
    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, 
    master=None, 
    year=None, 
    month=None, 
    firstweekday=calendar.MONDAY, 
    locale=None, 
    activebackground='#b1dcfb', 
    activeforeground='black', 
    selectbackground='#003eff', 
    selectforeground='white', 
    command=None, 
    borderwidth=1, 
    relief="solid", 
    on_click_month_button=None,
    on_click_year_button=None):
        """
        WIDGET OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground, activebackground, activeforeground, 
            command, borderwidth, relief, on_click_month_button
        """

        if year is None:
            year = self.datetime.now().year
        
        if month is None:
            month = self.datetime.now().month

        self._selected_date = None

        self._sel_bg = selectbackground 
        self._sel_fg = selectforeground

        self._act_bg = activebackground 
        self._act_fg = activeforeground
        
        self.on_click_month_button = on_click_month_button
        self.on_click_year_button = on_click_year_button
        
        self._selection_is_visible = False
        self._command = command

        ttk.Frame.__init__(self, master, borderwidth=borderwidth, relief=relief)
        
        self.bind("<FocusIn>", lambda event:self.event_generate('<<DatePickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event:self.event_generate('<<DatePickerFocusOut>>'))
    
        self._cal = get_calendar(locale, firstweekday)

        # custom ttk styles
        style = ttk.Style()
        style.layout('L.TButton', (
            [('Button.focus', {'children': [('Button.leftarrow', None)]})]
        ))
        style.layout('R.TButton', (
            [('Button.focus', {'children': [('Button.rightarrow', None)]})]
        ))

        self._font = tkFont.Font()

        # header frame and its widgets
        hframe = ttk.Frame(self)
        #self._header_var = StringVar()
        # Month
        self._month_var = StringVar()
        self._month_var.set("month")
        mframe = ttk.Frame(hframe)
        mframe.pack(side=LEFT)
        lmbtn = ttk.Button(mframe, style='L.TButton', command=self._on_press_left_month_button)
        lmbtn.pack(side=LEFT)

        mheader = ttk.Label(mframe, width=15, anchor=CENTER, textvariable=self._month_var)
        mheader.pack(side=LEFT, padx=12)

        rmbtn = ttk.Button(mframe, style='R.TButton', command=self._on_press_right_month_button)
        rmbtn.pack(side=LEFT)
        # Year
        self._year_var = StringVar()
        self._year_var.set("year")
        yframe = ttk.Frame(hframe)
        yframe.pack(side=LEFT)
        
        lybtn = ttk.Button(yframe, style='L.TButton', command=self._on_press_left_year_button)
        lybtn.pack(side=LEFT)

        yheader = ttk.Label(yframe, width=15, anchor=CENTER, textvariable=self._year_var)
        yheader.pack(side=LEFT, padx=12)

        rybtn = ttk.Button(yframe, style='R.TButton', command=self._on_press_right_year_button)
        rybtn.pack(side=LEFT)

        hframe.grid(columnspan=7, pady=4)

        self._day_labels = {}

        days_of_the_week = self._cal.formatweekheader(3).split()
 
        for i, day_of_the_week in enumerate(days_of_the_week):
            Tkinter.Label(self, text=day_of_the_week, background='grey90').grid(row=1, column=i, sticky=N+E+W+S)

        for i in range(6):
            for j in range(7):
                self._day_labels[i,j] = label = Tkinter.Label(self, background = "white")
                
                label.grid(row=i+2, column=j, sticky=N+E+W+S)
                label.bind("<Enter>", lambda event: event.widget.configure(background=self._act_bg, foreground=self._act_fg))
                label.bind("<Leave>", lambda event: event.widget.configure(background="white"))

                label.bind("<1>", self._pressed)
        
        # adjust its columns width
        font = tkFont.Font()
        maxwidth = max(font.measure(text) for text in days_of_the_week)
        for i in range(7):
            self.grid_columnconfigure(i, minsize=maxwidth, weight=1)

        self._year = None
        self._month = None

        # insert dates in the currently empty calendar
        self._build_calendar(year, month)

    def _build_calendar(self, year, month):
        if not( self._year == year and self._month == month):
            self._year = year
            self._month = month

            # update header text (Month, YEAR)
            header = self._cal.formatmonthname(year, month, 0)
            self._year_var.set(self._year)
            self._month_var.set(self._month)
            #self._header_var.set(header.title())

            # update calendar shown dates
            cal = self._cal.monthdayscalendar(year, month)

            for i in range(len(cal)):
                
                week = cal[i] 
                fmt_week = [('%02d' % day) if day else '' for day in week]
                
                for j, day_number in enumerate(fmt_week):
                    self._day_labels[i,j]["text"] = day_number

            if len(cal) < 6:
                for j in range(7):
                    self._day_labels[5,j]["text"] = ""

        if self._selected_date is not None and self._selected_date.year == self._year and self._selected_date.month == self._month:
            self._show_selection()

    def _find_label_coordinates(self, date):
         first_weekday_of_the_month = (date.weekday() - date.day) % 7
         
         return divmod((first_weekday_of_the_month - self._cal.firstweekday)%7 + date.day, 7)
        
    def _show_selection(self):
        """Show a new selection."""

        i,j = self._find_label_coordinates(self._selected_date)

        label = self._day_labels[i,j]

        label.configure(background=self._sel_bg, foreground=self._sel_fg)

        label.unbind("<Enter>")
        label.unbind("<Leave>")
        
        self._selection_is_visible = True
        
    def _clear_selection(self):
        """Show a new selection."""
        i,j = self._find_label_coordinates(self._selected_date)

        label = self._day_labels[i,j]
        label.configure(background= "white", foreground="black")

        label.bind("<Enter>", lambda event: event.widget.configure(background=self._act_bg, foreground=self._act_fg))
        label.bind("<Leave>", lambda event: event.widget.configure(background="white"))

        self._selection_is_visible = False

    # Callback

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        
        text = evt.widget["text"]
        
        if text == "":
            return

        day_number = int(text)

        new_selected_date = datetime.datetime(self._year, self._month, day_number)
        if self._selected_date != new_selected_date:
            if self._selected_date is not None:
                self._clear_selection()
            
            self._selected_date = new_selected_date
            
            self._show_selection()
        
        if self._command:
            self._command(self._selected_date)

    def _on_press_left_month_button(self):
        self.prev_month()
        
        if self.on_click_month_button is not None:
            self.on_click_month_button()

    def _on_press_left_year_button(self):
        self.prev_year()

        if self.on_click_year_button is not None:
            self.on_click_year_button()
        
    
    def _on_press_right_month_button(self):
        self.next_month()

        if self.on_click_month_button is not None:
            self.on_click_month_button()

    def _on_press_right_year_button(self):
        self.next_year()

        if self.on_click_year_button is not None:
            self.on_click_year_button()
        
    def select_prev_day(self):
        """Updated calendar to show the previous day."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date - self.timedelta(days=1)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar

    def select_next_day(self):
        """Update calendar to show the next day."""

        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date + self.timedelta(days=1)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar


    def select_prev_week_day(self):
        """Updated calendar to show the previous week."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date - self.timedelta(days=7)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar

    def select_next_week_day(self):
        """Update calendar to show the next week."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date + self.timedelta(days=7)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar

    def select_current_date(self):
        """Update calendar to current date."""
        if self._selection_is_visible: self._clear_selection()

        self._selected_date = datetime.datetime.now()
        self._build_calendar(self._selected_date.year, self._selected_date.month)

    def prev_month(self):
        """Updated calendar to show the previous week."""
        if self._selection_is_visible: self._clear_selection()
        
        date = self.datetime(self._year, self._month, 1) - self.timedelta(days=1)
        self._build_calendar(date.year, date.month) # reconstuct calendar

    def next_month(self):
        """Update calendar to show the next month."""
        if self._selection_is_visible: self._clear_selection()

        date = self.datetime(self._year, self._month, 1) + \
            self.timedelta(days=calendar.monthrange(self._year, self._month)[1] + 1)

        self._build_calendar(date.year, date.month) # reconstuct calendar

    def prev_year(self):
        """Updated calendar to show the previous year."""
        
        if self._selection_is_visible: self._clear_selection()

        self._build_calendar(self._year-1, self._month) # reconstruct calendar

    def next_year(self):
        """Update calendar to show the next year."""
        
        if self._selection_is_visible: self._clear_selection()

        self._build_calendar(self._year+1, self._month) # reconstruct calendar

    def get_selection(self):
        """Return a datetime representing the current selected date."""
        return self._selected_date
        
    selection = get_selection

    def set_selection(self, date):
        """Set the selected date."""
        if self._selected_date is not None and self._selected_date != date:
            self._clear_selection()

        self._selected_date = date

        self._build_calendar(date.year, date.month) # reconstruct calendar

# see this URL for date format information:
#     https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

class CalendarWidget(Widget):
  def __init__(self, master, **kwargs):
    self._textv = StringVar()
    super().__init__(tk=Datepicker(master, datevar=self._textv, dateformat=kwargs.get("node").get_attr("dateformat", "%Y-%m-%d")), **kwargs)

    self._setter = self.connect_to_prop("value", self.on_changed_value)
    self._trace = self._textv.trace_add("write", 
      lambda *_: self._setter(self._textv.get())
    )

  def on_changed_value(self, value):
    self._textv.set(value)

  def on_disposed(self):
    self._textv.trace_remove("write", self._trace)
    self._setter = None

class Datepicker(ttk.Entry):   
    def __init__(self, master, entrywidth=None, entrystyle=None, datevar=None, dateformat="%Y-%m-%d", onselect=None, firstweekday=calendar.MONDAY, locale=None, activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff', selectforeground='white', borderwidth=1, relief="solid"):
        self.date_var = datevar
        entry_config = {}
        if entrywidth is not None:
            entry_config["width"] = entrywidth
            
        if entrystyle is not None:
            entry_config["style"] = entrystyle
    
        ttk.Entry.__init__(self, master, textvariable=self.date_var, **entry_config)

        self.date_format = dateformat
        
        self._is_calendar_visible = False
        self._on_select_date_command = onselect

        self.calendar_frame = Calendar(self.winfo_toplevel(), firstweekday=firstweekday, locale=locale, activebackground=activebackground, activeforeground=activeforeground, selectbackground=selectbackground, selectforeground=selectforeground, command=self._on_selected_date, on_click_month_button=lambda: self.focus())

        self.bind_all("<1>", self._on_click, "+")

        self.bind("<FocusOut>", lambda event: self._on_entry_focus_out())
        self.bind("<Escape>", lambda event: self.hide_calendar())
        self.calendar_frame.bind("<<DatePickerFocusOut>>", lambda event: self._on_calendar_focus_out())


        # CTRL + PAGE UP: Move to the previous month.
        self.bind("<Control-Prior>", lambda event: self.calendar_frame.prev_month())
        
        # CTRL + PAGE DOWN: Move to the next month.
        self.bind("<Control-Next>", lambda event: self.calendar_frame.next_month())

        # CTRL + SHIFT + PAGE UP: Move to the previous year.
        self.bind("<Control-Shift-Prior>", lambda event: self.calendar_frame.prev_year())

        # CTRL + SHIFT + PAGE DOWN: Move to the next year.
        self.bind("<Control-Shift-Next>", lambda event: self.calendar_frame.next_year())
        
        # CTRL + LEFT: Move to the previous day.
        self.bind("<Control-Left>", lambda event: self.calendar_frame.select_prev_day())
        
        # CTRL + RIGHT: Move to the next day.
        self.bind("<Control-Right>", lambda event: self.calendar_frame.select_next_day())
        
        # CTRL + UP: Move to the previous week.
        self.bind("<Control-Up>", lambda event: self.calendar_frame.select_prev_week_day())
        
        # CTRL + DOWN: Move to the next week.
        self.bind("<Control-Down>", lambda event: self.calendar_frame.select_next_week_day())

        # CTRL + END: Close the datepicker and erase the date.
        self.bind("<Control-End>", lambda event: self.erase())

        # CTRL + HOME: Move to the current month.
        self.bind("<Control-Home>", lambda event: self.calendar_frame.select_current_date())
        
        # CTRL + SPACE: Show date on calendar
        self.bind("<Control-space>", lambda event: self.show_date_on_calendar())
        
        # CTRL + Return: Set to entry current selection
        self.bind("<Control-Return>", lambda event: self.set_date_from_calendar())
    
    def set_date_from_calendar(self):
        if self.is_calendar_visible:
            selected_date = self.calendar_frame.selection()

            if selected_date is not None:
                self.date_var.set(selected_date.strftime(self.date_format))
                
                if self._on_select_date_command is not None:
                    self._on_select_date_command(selected_date)

            self.hide_calendar()
      
    @property
    def current_text(self):
        return self.date_var.get()
        
    @current_text.setter
    def current_text(self, text):
        return self.date_var.set(text)
        
    @property
    def current_date(self):
        try:
            date = datetime.datetime.strptime(self.date_var.get(), self.date_format)
            return date
        except ValueError:
            return None
    
    @current_date.setter
    def current_date(self, date):
        self.date_var.set(date.strftime(self.date_format))
        
    @property
    def is_valid_date(self):
        if self.current_date is None:
            return False
        else:
            return True

    def show_date_on_calendar(self):
        date = self.current_date
        if date is not None:
            self.calendar_frame.set_selection(date)

        self.show_calendar()

    def show_calendar(self):
        if not self._is_calendar_visible:
            self.calendar_frame.place(in_=self, relx=0, rely=1)
            self.calendar_frame.lift()

        self._is_calendar_visible = True

    def hide_calendar(self):
        if self._is_calendar_visible:
            self.calendar_frame.place_forget()
        
        self._is_calendar_visible = False

    def erase(self):
        self.hide_calendar()
        self.date_var.set("")
    
    @property
    def is_calendar_visible(self):
        return self._is_calendar_visible

    def _on_entry_focus_out(self):
        if not str(self.focus_get()).startswith(str(self.calendar_frame)):
            self.hide_calendar()
        
    def _on_calendar_focus_out(self):
        if self.focus_get() != self:
            self.hide_calendar()

    def _on_selected_date(self, date):
        self.date_var.set(date.strftime(self.date_format))
        self.hide_calendar()
        
        if self._on_select_date_command is not None:
            self._on_select_date_command(date)

    def _on_click(self, event):
        str_widget = str(event.widget)

        if str_widget == str(self):
            if not self._is_calendar_visible:
                self.show_date_on_calendar()
        else:
            if not str_widget.startswith(str(self.calendar_frame)) and self._is_calendar_visible:
                self.hide_calendar()