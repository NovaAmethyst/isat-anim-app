"""
Function to handle the renaming of listbox elements.

Functions
---------
create_renaming_entry(tk.Listbox, int, str, Callable[[int, str], None]) -> None
    Function to rename an entry at a given index in a listbox object.
"""

import tkinter as tk
from typing import Callable


def create_renaming_entry(listbox: tk.Listbox, idx: int, old_name: str, save_func: Callable[[int, str], None]) -> None:
    """
    Function to rename an entry at a given index in a listbox object.

    Parameters
    ----------
    listbox : tk.Listbox
        the tkinter listbox widget
    idx : int
        the index of the listbox entry to rename
    old_name : str
        the previous content in the listbox entry
    save_func : Callable[[int, str], None]
        the function used to save the new content

    Returns
    -------
    None
    """
    x, y, _, h = listbox.bbox(idx)

    # Create an editable entry above the selected listbox case
    entry = tk.Entry(listbox)
    entry.insert(0, old_name)
    entry.select_range(0, "end")
    entry.focus()
    entry.place(x=x, y=y, width=listbox.winfo_width(), height=h)

    # Save the input if requested
    def save_entry(event):
        new_name = entry.get().strip()
        if new_name and new_name != old_name:
            save_func(idx, new_name)
        entry.destroy()    

    def cancel(event=None):
        entry.destroy()

    # Bind saving and cancel events
    entry.bind("<Return>", save_entry)
    entry.bind("<Escape>", cancel)
    entry.bind("<FocusOut>", save_entry)
