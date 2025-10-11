import tkinter as tk
from tkinter import messagebox
from typing import Optional


class BaseEntryFrame(tk.Frame):
    def __init__(self, parent, label, var_widget):
        super().__init__(parent)
        self.label = tk.Label(self, text=label, anchor="w")
        self.var = var_widget
        self.entry = tk.Entry(self, textvariable=self.var)

        self.label.pack(side="top", fill="x")
        self.entry.pack(side="bottom", fill="x", padx=4)
        self.error_message = "is in the wrong format"
    
    def get(self):
        try:
            return self.var.get()
        except tk.TclError:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value '{self.label['text']}' {self.error_message}."
            )
            return None


class IntEntryFrame(BaseEntryFrame):
    def __init__(self, parent, label, default: Optional[int] = None):
        super().__init__(
            parent=parent,
            label=label,
            var_widget=tk.IntVar(value=default),
        )

        self.error_message = "should be a valid integer"


class FloatEntryFrame(BaseEntryFrame):
    def __init__(self, parent, label, default: Optional[float] = None):
        super().__init__(
            parent=parent,
            label=label,
            var_widget=tk.DoubleVar(value=default)
        )

        self.error_message = "should be a valid real number"