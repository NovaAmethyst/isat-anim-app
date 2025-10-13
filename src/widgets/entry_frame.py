import tkinter as tk
from PIL import Image
from tkinter import filedialog, messagebox
from typing import Optional

from src.widgets.image_frame import ImageFrame


class BaseEntryFrame(tk.Frame):
    def __init__(self, parent, label, var_widget):
        super().__init__(parent)
        self.label = tk.Label(self, text=label + ':', anchor="w")
        self.var = var_widget
        self.entry = tk.Entry(self, textvariable=self.var)

        self.label.pack(side="top", fill="x")
        self.entry.pack(side="bottom", fill="x", padx=4)
        self.error_message = "is in the wrong format"
    
    def get(self):
        try:
            return self.var.get()
        except tk.TclError:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value '{self.label['text'][:-1]}' {self.error_message}."
            )
            return None


class IntEntryFrame(BaseEntryFrame):
    def __init__(self, parent, label, default: Optional[int] = None):
        super().__init__(
            parent=parent,
            label=label,
            var_widget=tk.IntVar(value=default),
        )

        self.error_message = "should be a valid integer"


class FloatEntryFrame(BaseEntryFrame):
    def __init__(self, parent, label, default: Optional[float] = None):
        super().__init__(
            parent=parent,
            label=label,
            var_widget=tk.DoubleVar(value=default)
        )

        self.error_message = "should be a valid real number"


class ImageFileEntry(tk.Frame):
    def __init__(self, parent, label, default: Image.Image | None = None):
        super().__init__(parent)
        self.label = tk.Label(self, text=label + ":", anchor="w")
        self.img_frame = ImageFrame(self, 64)
        self.img = default

        if self.img is not None:
            self.img_frame.set(self.img)

        self.label.pack(side="left")
        self.img_frame.pack(side="left", padx=2)
        tk.Button(self, text="...", command=self.set_file).pack(side="left", padx=2)

    def get(self):
        if self.img is None:
            messagebox.showwarning(
                "Erroneous variable",
                f"The value {self.label['text'][:-1]} should be associated with an image.",
            )
        return self.img

    def set_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg"),
                ("GIF Images", "*.gif"),
                ("All Files", "*.*"),
            ],
        )
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                self.img = img
                self.img_frame.set(self.img)
            except:
                messagebox.showwarning(
                    "Image non openable",
                    f"Could not open the image at {path}.",
                )