"""
Functions to handle opening and saving files in the app.

Functions
---------
get_json_save_filepath(Actor | Scene) -> str | None
    Ask for a file path to same the object as a json file.
open_image_file() -> PIL.Image.Image | None
    Asks for an image filepath to open it.
open_json_file() -> tuple[str, dict] | None
    Ask for a json file path to open.
"""

import json
from PIL import Image
from tkinter import filedialog, messagebox

from src.data_models import *


def open_image_file() -> Image.Image | None:
    """
    Asks for an image filepath to open it.

    Parameters
    ----------
    None

    Returns
    -------
    PIL.Image.Image | None
        the image if one is selected and opened without issue
    """
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
    """
    Ask for a json file path to open.

    Parameters
    ----------
    None

    Returns
    -------
    tuple[str, dict] | None
        the file path and file content if one is selected
    """
    path = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json")],
    )
    if not path:
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return path, data


def get_json_save_filepath(obj: Actor | Scene) -> str | None:
    """
    Ask for a file path to same the object as a json file.

    Parameters
    ----------
    obj : Actor | Scene
        the actor or scene to save

    Returns
    -------
    str | None
        the requested file path if one is given
    """
    file_name = obj.name.replace(' ', '_').lower()
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        initialfile=file_name,
    )
    return path