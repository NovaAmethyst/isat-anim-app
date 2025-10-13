import tkinter as tk
from PIL import Image, ImageTk


class ImageFrame(tk.Frame):
    def __init__(self, parent, side_length):
        super().__init__(parent)
        self.image_label = tk.Label(
            self,
            text="No image selected",
            anchor="w",
        )
        self.image_label.pack()
        self.current_image = None
        self.side_length = side_length

    def set(self, image: Image):
        img = image.copy()
        img.thumbnail(
            (self.side_length, self.side_length)
        )
        self.current_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.current_image, text="")

    def clean(self):
        self.image_label.config(image="", text="No image selected")
        self.current_image = None