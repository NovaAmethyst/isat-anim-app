import tkinter as tk


def create_add_edit_popup(master, label: str, new: bool, builder, save_func):
    window_type = "Add" if new else "Edit"

    popup = tk.Toplevel(master)
    popup.title(f"{window_type} {label}")

    entries, order = builder(popup)
    for entry_name in order:
        entries[entry_name].pack(side="top", fill="x", pady=1)

    def on_btn_click():
        res = save_func(entries)
        if res:
            popup.destroy()

    tk.Button(popup, text=window_type, command=on_btn_click).pack(pady=10)