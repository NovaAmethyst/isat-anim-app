"""
Defines a class for an editable treeview associated with buttons.

Classes
-------
EditableTreeFrame
"""

import tkinter as tk
from PIL import ImageTk
from tkinter import ttk
from typing import Any, Callable


class EditableTreeFrame(tk.Frame):
    """
    A class used to display a treeview and the buttons associated with it.

    Attributes
    ----------
    display_func : Callable[[Any], list[ImageTk.PhotoImage | str | None]]
        the function used to display elements in the treeview
    columns : list[str | None]
        the names of the treeview columns
    img_storage : list[PIL.ImageTk.PhotoImage]
        the list of images used in the treeview
    treeview : ttk.Treeview
        the treeview tkinter element

    Methods
    -------
    cleans() -> None:
        Removes all elements from the treeview and clears selection.
    select(idx) -> None:
        Sets a new index as a selection.
    select_clear() -> None:
        Clears all selections from the treeview.
    set(obj_list) -> None:
        Replaces treeview content with the given object list.
    """
    def __init__(
        self,
        parent: tk.Misc,
        columns: list[str | None],
        display_func: Callable[[Any], list[ImageTk.PhotoImage | str | None]],
        buttons_info: list[dict],
        btns_per_row: int = 2,
        select_func: Callable[[tk.Event, ttk.Treeview], None] | None = None,
    ):
        """
        Constructs, packs and binds all necessary attributes for the editable treeview frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        columns : list[str | None]
            the names of columns in the treeview
        display_func : Callable[[Any], list[ImageTk.PhotoImage | str | None]]
            the function used to display the objects in the tree as strings
        buttons_info : list[dict]
            the information about the buttons to place: text and command
        btns_per_row : int
            the number of buttons placed per row
        select_func : Callable[[tk.Event, ttk.Treeview], None] | None
            the optional function called when a treeview element is selected
        """
        super().__init__(parent)
        # Initiate attributes
        self.display_func: Callable[[Any], list[ImageTk.PhotoImage | str | None]] = display_func
        self.columns: list[str | None] = columns
        self.img_storage: list[ImageTk.PhotoImage] = []

        # Compute the number of button rows needed
        n_buttons: int = len(buttons_info)
        n_btn_frames: int = n_buttons // btns_per_row + int(n_buttons % btns_per_row != 0)

        # Create all buttons in their given row
        for i in range(n_btn_frames):
            btn_frame: tk.Frame = tk.Frame(self)
            btn_frame.pack(side="top", fill="x")
            # Pack all buttons in a row
            for j in range(i * btns_per_row, min((i + 1) * btns_per_row, n_buttons)):
                tk.Button(
                    btn_frame,
                    text=buttons_info[j].get("text", None),
                    command=buttons_info[j].get("command", None)
                ).pack(side="left", padx=2)

        # Create a treeview with an image column if needed
        has_image: bool = columns[0] is not None
        self.treeview: ttk.Treeview = ttk.Treeview(
            self,
            columns=tuple([f"#{i}" for i in range(1, len(columns))]),
            show="tree headings" if has_image else "headings"
        )

        # Create a reference to all columns needed
        for i in range(len(columns)):
            if columns[i] is None:
                continue
            col_id: str = f"#{i}"
            self.treeview.heading(col_id, text=columns[i])
            self.treeview.column(col_id, anchor="center")

        self.treeview.pack(side="bottom", fill="both", expand="True")

        # Bind a selection function to the treeview element selection event if one is given
        if select_func is not None:
            self.treeview.bind("<<TreeviewSelect>>", lambda x: select_func(x, self.treeview))

    def select_clear(self) -> None:
        """
        Clears all selections from the treeview.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.treeview.selection_remove(*self.treeview.selection())

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
        self.treeview.selection_set(str(idx))

    def clean(self) -> None:
        """
        Removes all elements from the treeview and clears selection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.select_clear()
        self.treeview.delete(*self.treeview.get_children())
        self.img_storage = []

    def set(self, obj_list: list[Any]) -> None:
        """
        Replaces treeview content with the given object list.

        Parameters
        ----------
        obj_list : list[Any]
            the list to place in the treeview

        Returns
        -------
        None
        """
        self.clean()

        for i in range(len(obj_list)):
            elems = self.display_func(obj_list[i])
            img = elems[0]
            self.img_storage.append(img)

            # Insert differently based on whether an image was given
            if img:
                self.treeview.insert(
                    "",
                    "end",
                    image=img,
                    values=tuple(elems[1:]),
                    iid=str(i),
                )
            else:
                self.treeview.insert(
                    "",
                    "end",
                    values=tuple(elems[1:]),
                    iid=str(i),
                )

        self.select_clear()