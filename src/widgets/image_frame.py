import tkinter as tk
from PIL import Image, ImageTk


class ImageFrame(tk.Frame):
    def __init__(self, parent, side_length):
        super().__init__(parent)
        self.image_label = tk.Label(
            self,
            text="No image selected",
            anchor="center",
            width=side_length,
            height=side_length,
            highlightbackground="black",
            highlightthickness=1,
        )
        self.image_label.pack(fill="both", expand=True)
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
        self.image_label.config(image="", text="Noimage selected")
        self.current_image = None