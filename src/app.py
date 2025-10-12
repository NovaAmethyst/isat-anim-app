import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from src.data_models import *
from src.widgets import *
from src.widgets.utils import create_renaming_entry


class AnimationEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Animation Editor")
        self.protocol("WM_DELETE_WINDOW", self.window_close)

        self.actors: list[Actor] = []
        self.actors_save_status: list[tuple[bool, str]] = []
        self.curr_actor_idx: Optional[int] = None

        self.create_tabs()
    
    def create_tabs(self):
        self.tab_notebook = ttk.Notebook(self)
        self.tab_notebook.pack(fill="both", expand=True)

        self.actor_frame = tk.Frame(self.tab_notebook, highlightbackground="black", highlightthickness=1)
        self.tab_notebook.add(self.actor_frame, text="Actors")
        self.init_actor_tab()
    
    def init_actor_tab(self):
        # Left: actor list
        def display_actor(actor: Actor) -> str:
            idx = self.actors.index(actor)
            name = actor.name
            if not self.actors_save_status[idx][0]:
                name = '*' + name
            return name

        self.actor_listbox = EditableListFrame(
            parent=self.actor_frame,
            display_func=display_actor,
            buttons_info=[
                {"text": "Add Actor", "command": self.add_actor},
                {"text": "Open Actor", "command": self.open_actor},
                {"text": "Delete Actor", "command": self.delete_actor},
            ],
            select_func=self.select_actor,
            double_func=self.rename_actor,
        )
        self.actor_listbox.pack(side="left", fill="y", expand=True, padx=10, pady=10)
    
    def unsaved_actor(self, idx: int):
        self.actors_save_status[idx] = (False, self.actors_save_status[idx][1])

        self.actor_listbox.clean()
        self.actor_listbox.set(self.actors)
    
    def clean_actor(self):
        self.actor_listbox.select_clear()
        self.curr_actor_idx = None
    
    def set_actor(self, idx: int):
        self.clean_actor()

        self.curr_actor_idx = idx
        self.actor_listbox.select(idx)
    
    def _add_or_replace_actor(self, actor: Actor, path: str | None = None, idx: int | None = None):
        save_status = (path is not None, path)
        if idx is None:
            idx = len(self.actors)
            self.actors.append(actor)
            self.actors_save_status.append(save_status)
        else:
            self.actors[idx] = actor
            self.actors_save_status[idx] = save_status
        
        self.actor_listbox.set(self.actors)
        self.set_actor(idx)
    
    def add_actor(self):
        actor_names = [actor.name for actor in self.actors]
        i = 1
        while f"Actor {i}" in actor_names:
            i += 1
        
        actor = Actor(name=f"Actor {i}")
        self._add_or_replace_actor(actor)
    
    def open_actor(self):  # TODO test the function once whole actors interface and saving is done
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
        )
        if not path:
            return
        with open(path, "r") as f:
            data = json.load(f)
        
        actor = Actor.from_dict(data)
        # TODO add checks and behaviour for opening actor with pre-existing name in register
        self._add_or_replace_actor(actor)
    
    def delete_actor(self):
        if self.curr_actor_idx is None:
            return
        idx = self.curr_actor_idx

        if not self.actors_save_status[idx][0]:
            answer = messagebox.askokcancel(
                title="Confirmation",
                message=f"The actor {self.actors[idx].name} wasn't saved. Delete anyway?",
                icon=messagebox.WARNING,
            )
            if not answer:
                return
        
        self.actors.pop(idx)
        self.actors_save_status.pop(idx)
        self.clean_actor()
        self.actor_listbox.set(self.actors)

    def select_actor(self, event, listbox):
        idx = listbox.curselection()
        if idx and idx[0] != self.curr_actor_idx:
            self.set_actor(idx[0])
    
    def rename_actor(self, event, listbox):
        if self.curr_actor_idx is None:
            return

        def save_actor_name(idx: int, name: str) -> None:
            self.actors[idx].name = name
            self.unsaved_actor(idx)
            self.set_actor(idx)
        
        actor_idx = self.curr_actor_idx
        old_name = self.actors[actor_idx].name
        create_renaming_entry(listbox, actor_idx, old_name, save_actor_name)

    def window_close(self):
        unsaved_actors = False
        for status in self.actors_save_status:
            if not status[0]:
                unsaved_actors = True
                break
        
        if not unsaved_actors:
            self.quit()
            return
        
        unsaved_kind = ""
        if unsaved_actors:
            unsaved_kind += "actors"
        
        message = f"There are unsaved {unsaved_kind}. Close the window anyway?"

        answer = messagebox.askokcancel(
            title="Confirmation",
            message=message,
            icon=messagebox.WARNING,
        )

        if answer:
            self.quit()