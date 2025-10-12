import tkinter as tk
from tkinter import ttk


class EditableTreeFrame(tk.Frame):
    def __init__(self, parent, columns, display_func, buttons_info, btns_per_row=2, select_func=None):
        super().__init__(parent)
        self.display_func = display_func
        self.columns = columns
        self.img_storage = []

        n_buttons = len(buttons_info)
        n_btn_frames = n_buttons // btns_per_row + int(n_buttons % btns_per_row != 0)

        for i in range(n_btn_frames):
            btn_frame = tk.Frame(self)
            btn_frame.pack(side="top", fill="x")
            for j in range(i * btns_per_row, min((i + 1) * btns_per_row, n_buttons)):
                tk.Button(
                    btn_frame,
                    text=buttons_info[j].get("text", None),
                    command=buttons_info[j].get("command", None)
                ).pack(side="left", padx=2)

        has_image = columns[0] is not None

        self.treeview = ttk.Treeview(
            self,
            columns=tuple([f"#{i}" for i in range(1, len(columns))]),
            show="tree headings" if has_image else "headings"
        )

        for i in range(len(columns)):
            if columns[i] is None:
                continue
            col_id = f"#{i}"
            self.treeview.heading(col_id, text=columns[i])
            self.treeview.column(col_id, anchor="center")

        self.treeview.pack(side="bottom", fill="both", expand="True")

        if select_func is not None:
            self.treeview.bind("<<TreeviewSelect>>", lambda x: select_func(x, self.treeview))

    def select_clear(self):
        self.treeview.selection_remove(*self.treeview.selection())

    def select(self, idx: int):
        self.treeview.selection_set(str(idx))

    def clean(self):
        self.select_clear()
        self.tree.delete(*self.tree.get_children())
        self.img_storage = []

    def set(self, obj_list):
        self.clean()

        for i in range(len(obj_list)):
            elems = self.display_func(obj_list[i])
            img = elems[0]
            self.img_storage.append(img)

            if img:
                self.treeview.insert(
                    "",
                    "end",
                    image=img,
                    values=tuple(elems[1:]),
                    iid=str(i),
                )
            else:
                self.treeview.insert(
                    "",
                    "end",
                    values=tuple(elems[1:]),
                    iid=str(i),
                )

        self.select_clear()