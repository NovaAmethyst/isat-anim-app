import tkinter as tk


class EditableListFrame(tk.Frame):
    def __init__(self, parent, display_func, buttons_info, btns_per_row=2, select_func=None, double_func=None):
        super().__init__(parent)
        self.display_func = display_func
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
        
        self.listbox = tk.Listbox(self)
        self.listbox.pack(side="bottom", fill="both", expand="True")

        if select_func is not None:
            self.listbox.bind("<<ListboxSelect>>", lambda x: select_func(x, self.listbox))
        if double_func is not None:
            self.listbox.bind("<Double-1>", lambda x: double_func(x, self.listbox))
    
    def select_clear(self):
        self.listbox.selection_clear(0, "end")
    
    def select(self, idx: int):
        self.select_clear()
        self.listbox.selection_set(idx)
    
    def clean(self):
        self.select_clear()
        self.listbox.delete(0, "end")
    
    def set(self, obj_list):
        self.clean()
        for obj in obj_list:
            self.listbox.insert("end", self.display_func(obj))
        self.select_clear()