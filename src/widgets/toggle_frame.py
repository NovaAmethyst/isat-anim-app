import tkinter as tk
from tkinter import ttk


class ToggleFrame(tk.Frame):
    def __init__(
        self,
        parent,
        toggle_label: str,
        toggle_default: bool,
    ):
        super().__init__(parent)
        self.toggle_var = tk.BooleanVar()
        self.toggle_var.set(toggle_default)
        ttk.Checkbutton(
            self,
            text=toggle_label,
            variable=self.toggle_var,
            command=self.change_toggle,
            onvalue=True,
            offvalue=False,
        ).pack(side="top", fill="x", anchor="w")
        self.frame_true = tk.Frame(self)
        self.frame_false = tk.Frame(self)

        self.change_toggle()

    def get(self) -> bool:
        return self.toggle_var.get()

    def change_toggle(self):
        if self.toggle_var.get():
            self.frame_false.pack_forget()
            self.frame_true.pack(side="top", fill="x", padx=4, pady=1)
        else:
            self.frame_true.pack_forget()
            self.frame_false.pack(side="top", fill="x", padx=4, pady=1)