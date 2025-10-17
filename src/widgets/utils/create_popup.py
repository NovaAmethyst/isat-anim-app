"""
Function to create a popup to add or edit an element in the app.

Functions
---------
create_add_edit_popup(tk.Misc, str, bool, Callable[[tk.Toplevel], tuple[dict[str, tk.Misc], list[str]]], Callable[[tuple[dict[str, tk.Misc]]], bool]) -> None
    Creates a popup with entries to edit from the given tkinter element.
"""

import tkinter as tk
from typing import Callable


def create_add_edit_popup(
        master: tk.Misc,
        label: str,
        new: bool,
        builder: Callable[[tk.Toplevel], tuple[dict[str, tk.Misc], list[str]]],
        save_func: Callable[[tuple[dict[str, tk.Misc]]], bool],
    ) -> None:
    """
    Creates a popup with entries to edit from the given tkinter element.

    Parameters
    ----------
    master : tk.Misc
        the tkinter element to which the popup is connected
    label : str
        the name of the element added or edited
    new : bool
        whether the popup is for an edit (False) or addition (True)
    builder : Callable[[tk.Toplevel], tuple[dict[str, tk.Misc], list[str]]]
        a function to get a dictionary of tkinter elements and the order of insertion in the popup
    save_func : Callable[[tuple[dict[str, tk.Misc]]], bool]
        a function to call when trying to save the contents of the popup

    Returns
    -------
    None
    """
    # Create popup
    window_type: str = "Add" if new else "Edit"

    popup: tk.Toplevel = tk.Toplevel(master)
    popup.title(f"{window_type} {label}")

    # Insert all given entries into popup in the correct order
    entries, order = builder(popup)
    for entry_name in order:
        entries[entry_name].pack(side="top", fill="x", pady=1)

    # Set save and close event on the saving button
    def on_btn_click():
        res: bool = save_func(entries)
        if res:
            popup.destroy()

    tk.Button(popup, text=window_type, command=on_btn_click).pack(pady=10)