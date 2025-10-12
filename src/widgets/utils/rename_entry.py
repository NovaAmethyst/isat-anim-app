import tkinter as tk
from typing import Callable


def create_renaming_entry(listbox, idx: int, old_name: str, save_func: Callable[[int, str], None]):
    x, y, _, h = listbox.bbox(idx)

    entry = tk.Entry(listbox)
    entry.insert(0, old_name)
    entry.select_range(0, "end")
    entry.focus()
    entry.place(x=x, y=y, width=listbox.winfo_width(), height=h)

    def save_entry(event):
        new_name = entry.get().strip()
        if new_name and new_name != old_name:
            save_func(idx, new_name)
        entry.destroy()    

    def cancel(event=None):
        entry.destroy()
        
    entry.bind("<Return>", save_entry)
    entry.bind("<Escape>", cancel)
    entry.bind("<FocusOut>", save_entry)
