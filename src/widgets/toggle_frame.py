"""
Defines a class for frames displayed on a toggle.

Classes
-------
ToggleFrame
"""

import tkinter as tk
from tkinter import ttk


class ToggleFrame(tk.Frame):
    """
    A class used to display one of two frames depending on a toggle.

    Attributes
    ----------
    toggle_var : tk.BooleanVar
        the variable corresponding to the toggle
    frame_true : tk.Frame
        the frame displayed when the toggle is set to True
    frame_false : tk.Frame
        the frame displayed when the toggle is set to False

    Methods
    -------
    change_toggle() -> None:
        Changes which frame is visible depending on the toggle value.
    get() -> bool:
        Gets the value of the toggle variable.
    """
    def __init__(
        self,
        parent: tk.Misc,
        toggle_label: str,
        toggle_default: bool,
    ):
        """
        Constructs and packs all necessary attributes for the frames with a toggle.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        toggle_label : str
            the name of the toggle variable
        toggle_default : str
            the default value of the toggle variable
        """
        super().__init__(parent)
        self.toggle_var: tk.BooleanVar = tk.BooleanVar()
        self.toggle_var.set(toggle_default)
        ttk.Checkbutton(
            self,
            text=toggle_label,
            variable=self.toggle_var,
            command=self.change_toggle,
            onvalue=True,
            offvalue=False,
        ).pack(side="top", fill="x", anchor="w")
        self.frame_true: tk.Frame = tk.Frame(self)
        self.frame_false: tk.Frame = tk.Frame(self)

        self.change_toggle()

    def get(self) -> bool:
        """
        Gets the value of the toggle variable.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            the value of the toggle variable
        """
        return self.toggle_var.get()

    def change_toggle(self) -> None:
        """
        Changes which frame is visible depending on the toggle value.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.toggle_var.get():
            self.frame_false.pack_forget()
            self.frame_true.pack(side="top", fill="x", padx=4, pady=1)
        else:
            self.frame_true.pack_forget()
            self.frame_false.pack(side="top", fill="x", padx=4, pady=1)