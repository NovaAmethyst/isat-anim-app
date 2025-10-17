"""
Defines a class to display an image in the app.

Classes
-------
ImageFrame
"""

import tkinter as tk
from PIL import Image, ImageTk


class ImageFrame(tk.Frame):
    """
    A class used to display images at a given size.

    Attributes
    ----------
    image_label : tk.Label
        the tkinter widget used to display the image
    current_image : PIL.ImageTK.PhotoImage | None
        the image currently being displayed
    side_length : int
        the size in pixels of the image

    Methods
    -------
    clean() -> None:
        Stops displaying an image.
    set(image) -> None:
        Changes the displayed image.
    """
    def __init__(self, parent: tk.Misc, side_length: int):
        """
        Constructs and packs all necessary attributes for an image frame.

        Parameters
        ----------
        parent : tk.Misc
            the tkinter widget the frame will be placed in
        side_length : int
            the size of the displayed image in pixels
        """
        super().__init__(parent)
        self.image_label: tk.Label = tk.Label(
            self,
            text="No image selected",
            anchor="w",
        )
        self.image_label.pack()
        self.current_image: ImageTk.PhotoImage | None = None
        self.side_length: int = side_length

    def set(self, image: Image.Image) -> None:
        """
        Changes the displayed image.

        Parameters
        ----------
        image : PIL.Image.Image
            the new image to display

        Returns
        -------
        None
        """
        img: Image.Image = image.copy()
        img.thumbnail(
            (self.side_length, self.side_length)
        )
        self.current_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.current_image, text="")

    def clean(self) -> None:
        """
        Stops displaying an image.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.image_label.config(image="", text="No image selected")
        self.current_image = None