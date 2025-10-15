import json
from PIL import Image
from tkinter import filedialog, messagebox

from src.data_models import *


def open_image_file() -> Image.Image | None:
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
            return img
        except:
            messagebox.showwarning(
                "Could not open image",
                f"Could not open the image at {path}.",
            )
    return None


def open_json_file() -> tuple[str, dict] | None:
    path = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json")],
    )
    if not path:
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return path, data


def get_json_save_filepath(obj: Actor | Scene) -> str | None:
    file_name = obj.name.replace(' ', '_').lower()
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        initialfile=file_name,
    )
    return path