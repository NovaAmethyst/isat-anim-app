"""
Defines functions used to handle common tkinter elements in the app.

Functions
---------
create_add_edit_popup(tk.Misc, str, bool, Callable[[tk.Toplevel], tuple[dict[str, tk.Misc], list[str]]], Callable[[tuple[dict[str, tk.Misc]]], bool]) -> None
create_renaming_entry(tk.Listbox, int, str, Callable[[int, str], None]) -> None
get_json_save_filepath(Actor | Scene) -> str | None
open_image_file() -> PIL.Image.Image | None
open_json_file() -> tuple[str, dict] | None
"""

from src.widgets.utils.create_popup import *
from src.widgets.utils.file_gestion import *
from src.widgets.utils.rename_entry import *