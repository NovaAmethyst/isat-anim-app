"""
Defines classes used to ask for and get user input.

Classes
-------
BaseEntryFrame
DropdownEntry
ImageFileEntry
IntEntryFrame
PositiveFloatEntryFrame
UnsignedIntEntryFrame
"""

import tkinter as tk
from PIL import Image
from tkinter import messagebox
from typing import Any, Optional

from src.widgets.image_frame import ImageFrame
from src.widgets.utils import *


class BaseEntryFrame(tk.Frame):
    """
    A class to handle user inputs for values.

    Attributes
    ----------
    label : tk.Label
        the tkinter label widget representing the variable
    var : tk.Variable
        the reference to the variable the user can access/modify
    entry : tk.Entry
        the entry tkinter widget for user interaction
    error_message : str
        the end of the error shown if the variable can't be interpreted

    Methods
    -------
    get() -> Any | None:
        Gets value stored in entry, sends warning if value in wrong format.
    set(value) -> None:
        Sets a given value into the entry.
    """
    def __init__(self, parent: tk.Misc, label: str, var_widget: tk.Variable):
        """
        Constructs and packs all necessary attributes for an entry frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        label : str
            the name of the variable
        var_widget : tk.Variable
            the variable to associate with the entry
        """
        super().__init__(parent)
        self.label: tk.Label = tk.Label(self, text=label + ':', anchor="w")
        self.var: tk.Variable = var_widget
        self.entry: tk.Entry = tk.Entry(self, textvariable=self.var)

        self.label.pack(side="top", fill="x")
        self.entry.pack(side="bottom", fill="x", padx=4)
        self.error_message: str = "is in the wrong format"
    
    def get(self) -> Any | None:
        """
        Gets value stored in entry, sends warning if value in wrong format.

        Parameters
        ----------
        None

        Returns
        -------
        Any | None
            the value stored in the entry if it is valid
        """
        try:
            return self.var.get()
        except tk.TclError:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value '{self.label['text'][:-1]}' {self.error_message}."
            )
            return None

    def set(self, value: Any) -> None:
        """
        Sets a given value into the entry.

        Parameters
        ----------
        value : Any
            the value to set the entry to

        Returns
        -------
        None
        """
        self.var.set(value)


class IntEntryFrame(BaseEntryFrame):
    """
    A class to handle user integer inputs.

    Attributes
    ----------
    label : tk.Label
        the tkinter label widget representing the variable
    var : tk.IntVar
        the reference to the variable the user can access/modify
    entry : tk.Entry
        the entry tkinter widget for user interaction
    error_message : str
        the end of the error shown if the variable can't be interpreted

    Methods
    -------
    get() -> Any | None:
        Gets value stored in entry, sends warning if value in wrong format.
    set(value) -> None:
        Sets a given value into the entry.
    """
    def __init__(self, parent: tk.Misc, label: str, default: Optional[int] = None):
        """
        Constructs and packs all necessary attributes for an integer entry frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        label : str
            the name of the variable
        default : int | None
            the default value of the entry
        """
        super().__init__(
            parent=parent,
            label=label,
            var_widget=tk.IntVar(value=default),
        )

        self.error_message = "should be a valid integer"


class UnsignedIntEntryFrame(IntEntryFrame):
    def __init__(self, parent: tk.Misc, label: str, default: Optional[int] = None):
        """
        Constructs and packs all necessary attributes for an unsigned integer entry frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        label : str
            the name of the variable
        default : int | None
            the default value of the entry
        """
        super().__init__(
            parent=parent,
            label=label,
            default=default,
        )

        self.error_message = "should be a valid positive integer"

    def get(self) -> Any | None:
        """
        Gets value stored in entry, sends warning if value in wrong format.

        Parameters
        ----------
        None

        Returns
        -------
        Any | None
            the value stored in the entry if it is valid
        """
        val: Any | None = super().get()
        if val is None:
            return val
        if val <= 0:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value '{self.label['text'][:-1]}' should be greater than 0."
            )
            return None
        return val


class PositiveFloatEntryFrame(BaseEntryFrame):
    """
    A class to handle user integer inputs.

    Attributes
    ----------
    label : tk.Label
        the tkinter label widget representing the variable
    var : tk.DoubleVar
        the reference to the variable the user can access/modify
    entry : tk.Entry
        the entry tkinter widget for user interaction
    error_message : str
        the end of the error shown if the variable can't be interpreted

    Methods
    -------
    get() -> Any | None:
        Gets value stored in entry, sends warning if value in wrong format.
    set(value) -> None:
        Sets a given value into the entry.
    """
    def __init__(self, parent: tk.Misc, label: str, default: Optional[float] = None):
        """
        Constructs and packs all necessary attributes for a float entry frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        label : str
            the name of the variable
        default : float | None
            the defautl value of the entry
        """
        super().__init__(
            parent=parent,
            label=label,
            var_widget=tk.DoubleVar(value=default)
        )

        self.error_message = "should be a valid positive real number"

    def get(self) -> Any | None:
        """
        Gets value stored in entry, sends warning if value in wrong format.

        Parameters
        ----------
        None

        Returns
        -------
        Any | None
            the value stored in the entry if it is valid
        """
        val: Any | None = super().get()
        if val is None:
            return val
        if val < 0.0:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value '{self.label['text'][:-1]}' should be greater than 0."
            )
            return None
        return val


class ImageFileEntry(tk.Frame):
    """
    A class to handle user image inputs.

    Attributes
    ----------
    label : tk.Label
        the tkinter label widget representing the variable
    img_frame : ImageFrame
        the widget used to represent the chosen image or lack thereof
    img : the chosen image

    Methods
    -------
    get() -> PIL.Image.Image | None:
        Gets image stored in entry, sends warning no image is found.
    set_file() -> None:
        Asks the user for a path to an image, sets it if one is given.
    """
    def __init__(self, parent: tk.Misc, label: str, default: Image.Image | None = None):
        """
        Constructs and packs all necessary attributes for an image entry frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        label : str
            the name of the variable
        default : PIL.Image.Image | None
            the defautl value of the entry
        """
        super().__init__(parent)
        self.label: tk.Label = tk.Label(self, text=label + ":", anchor="w")
        self.img_frame: ImageFrame = ImageFrame(self, 64)
        self.img: Image.Image = default

        if self.img is not None:
            self.img_frame.set(self.img)

        self.label.pack(side="left")
        self.img_frame.pack(side="left", padx=2)
        tk.Button(self, text="...", command=self.set_file).pack(side="left", padx=2)

    def get(self) -> Image.Image | None:
        """
        Gets image stored in entry, sends warning no image is found.

        Parameters
        ----------
        None

        Returns
        -------
        PIL.Image.Image | None
            the value stored in the entry if it is valid
        """
        if self.img is None:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value {self.label['text'][:-1]} should be associated with an image.",
            )
        return self.img

    def set_file(self) -> None:
        """
        Asks the user for a path to an image, sets it if one is given.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        img = open_image_file()
        if img:
            self.img = img
            self.img_frame.set(self.img)
        return


class DropdownEntry(tk.Frame):
    """
    A class to handle user selection from a list of strings.

    Attributes
    ----------
    label : tk.Label
        the tkinter widget representing the variable
    var : tk.StringVar
        the tkinter variable representing the user's choice
    dropdown : tk.OptionMenu
        the actual dropdown menu
    options : list[str]
        the options given to the user

    Methods
    -------
    get() -> str | None:
        Gets the choice selected by the user if one is.
    """
    def __init__(
        self,
        parent: tk.Misc,
        label: str,
        options: list[str],
        default: str | None = None
    ):
        """
        Constructs and packs all necessary attributes for a float entry frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        label : str
            the name of the variable
        options : list[str]
            the choices available to the user
        default : str | None
            the defautl value of the entry
        """
        super().__init__(parent)
        self.label : tk.Label = tk.Label(self, text=label + ':', anchor="w")
        self.var: tk.StringVar = tk.StringVar(value=default if default is not None else "Please select an option")
        self.dropdown: tk.OptionMenu = tk.OptionMenu(
            self,
            self.var,
            default if default is not None else "Please select an option",
            *options,
        )
        self.options: list[str] = options

        self.label.pack(side="top", fill="x")
        self.dropdown.pack(side="bottom", fill="x", padx=4)

    def get(self) -> str | None:
        """
        Gets the choice selected by the user if one is.

        Parameters
        ----------
        None

        Returns
        -------
        str | None
            the option selected by the user if there is one
        """
        value: str = self.var.get()
        if value in self.options:
            return value
        messagebox.showinfo(
            "Unset option",
            f"No choice was made for the value '{self.label['text'][:-1]}'."
        )
        return None