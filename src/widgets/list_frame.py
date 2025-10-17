"""
Defines a class for an editable listbox associated with buttons.

Classes
-------
EditableListFrame
"""

import tkinter as tk
from typing import Any, Callable


class EditableListFrame(tk.Frame):
    """
    A class used to display a listbox and the buttons associated with it.

    Attributes
    ----------
    display_func : Callable[[Any], str]
        the function used to display elements in the listbox
    listbox : tk.Listbox
        the listbox tkinter element

    Methods
    -------
    clean() -> None:
        Removes all elements from the listbox and clears selection.
    select(idx) -> None:
        Sets a new index as a selection.
    select_clear() -> None:
        Clears all selections from the listbox.
    set(obj_list) -> None:
        Replaces listbox content with the given object list.
    """
    def __init__(
        self,
        parent: tk.Misc,
        display_func: Callable[[Any], str],
        buttons_info: list[dict],
        btns_per_row: int = 2,
        select_func: Callable[[tk.Event, tk.Listbox], str] | None = None,
        double_func: Callable[[tk.Event, tk.Listbox], str] | None = None,
    ):
        """
        Constructs, packs and binds all necessary attributes for the editable list frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        display_func : Callable[[Any], str]
            the function used to display the objects in the list as strings
        buttons_info : list[dict]
            the information about the buttons to place: text and command
        btns_per_row : int
            the number of buttons placed per row
        select_func : Callable[[tk.Event, tk.Listbox], str] | None
            the optional function called when a listbox element is selected
        double_func : Callable[[tk.Event, tk.Listbox], str] | None
            the optional function called when a user double clicks on a listbox element
        """
        super().__init__(parent)
        self.display_func: Callable[[Any], str] = display_func

        # Compute the number of rows needed
        n_buttons: int = len(buttons_info)
        n_btn_frames: int = n_buttons // btns_per_row + int(n_buttons % btns_per_row != 0)

        # Pack all buttons in order, across all rows
        for i in range(n_btn_frames):
            btn_frame: tk.Frame = tk.Frame(self)
            btn_frame.pack(side="top", fill="x")
            for j in range(i * btns_per_row, min((i + 1) * btns_per_row, n_buttons)):
                # Create and pack button
                tk.Button(
                    btn_frame,
                    text=buttons_info[j].get("text", None),
                    command=buttons_info[j].get("command", None)
                ).pack(side="left", padx=2)

        # Create and pack the listbox
        self.listbox: tk.Listbox = tk.Listbox(self)
        self.listbox.pack(side="bottom", fill="both", expand="True")

        # Set a selection event if a selection function is given
        if select_func is not None:
            self.listbox.bind("<<ListboxSelect>>", lambda x: select_func(x, self.listbox))
        # Set a double click event if a double click function is given
        if double_func is not None:
            self.listbox.bind("<Double-1>", lambda x: double_func(x, self.listbox))
    
    def select_clear(self) -> None:
        """
        Clears all selections from the listbox.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.listbox.selection_clear(0, "end")
    
    def select(self, idx: int) -> None:
        """
        Sets a new index as a selection.

        Parameters
        ----------
        idx : int
            the new index of the selection

        Returns
        -------
        None
        """
        self.select_clear()
        self.listbox.selection_set(idx)
    
    def clean(self) -> None:
        """
        Removes all elements from the listbox and clears selection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.select_clear()
        self.listbox.delete(0, "end")
    
    def set(self, obj_list: list[Any]) -> None:
        """
        Replaces listbox content with the given object list.

        Parameters
        ----------
        obj_list: list[Any]
            the list to place in the listbox

        Returns
        -------
        None
        """
        self.clean()
        for obj in obj_list:
            self.listbox.insert("end", self.display_func(obj))
        self.select_clear()