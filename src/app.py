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
        self.curr_action_idx: Optional[int] = None

        self.create_tabs()
    
    def create_tabs(self):
        self.tab_notebook = ttk.Notebook(self)
        self.tab_notebook.pack(fill="both", expand=True)

        self.actor_frame = tk.Frame(self.tab_notebook)
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
        self.actor_listbox.pack(side="left", fill="y", padx=10, pady=10)

        # Right: Actor details, actions and action components
        actor_detail_frame = tk.Frame(self.actor_frame)
        actor_detail_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Top right: name display and save buttons
        actor_name_frame = tk.Frame(actor_detail_frame)
        actor_name_frame.pack(side="top", fill="x")
        self.actor_name_label = tk.Label(actor_name_frame, text="")
        self.actor_name_label.pack(side="left", fill="x")
        tk.Button(actor_name_frame, text="Save As", command=self.save_actor_as).pack(side="right", padx=2)
        tk.Button(actor_name_frame, text="Save", command=self.save_actor).pack(side="right", padx=2)

        # Middle right: action list
        def display_action(action: Action) -> str:
            return action.name

        self.action_listbox = EditableListFrame(
            parent=actor_detail_frame,
            display_func=display_action,
            buttons_info=[
                {"text": "Add Action", "command": self.add_action},
                {"text": "Delete Action", "command": self.delete_action},
            ],
            btns_per_row=3,
            select_func=self.select_action,
            double_func=self.rename_action,
        )
        self.action_listbox.pack(side="top", fill="both", expand=True)

    def set_actor_all(self):
        actor_idx = self.curr_actor_idx
        action_idx = self.curr_action_idx

        self.clean_actor()
        self.actor_listbox.clean()

        self.actor_listbox.set(self.actors)
        if action_idx is not None:
            self.set_action(action_idx)
        elif actor_idx is not None:
            self.set_actor(actor_idx)

    def unsaved_actor(self, idx: int):
        self.actors_save_status[idx] = (False, self.actors_save_status[idx][1])

        self.actor_listbox.clean()
        self.actor_listbox.set(self.actors)

    def clean_actor(self):
        self.clean_action()

        self.actor_listbox.select_clear()
        self.curr_actor_idx = None

        self.actor_name_label["text"] = ""

    def set_actor(self, idx: int):
        self.clean_actor()

        self.curr_actor_idx = idx
        self.actor_listbox.select(idx)

        actor = self.actors[idx]

        self.actor_name_label["text"] = actor.name
        self.action_listbox.set(actor.actions)
    
    def _add_or_replace_actor(self, actor: Actor, path: str | None = None, idx: int | None = None):
        save_status = (path is not None, path)
        if idx is None:
            idx = len(self.actors)
            self.actors.append(actor)
            self.actors_save_status.append(save_status)
        else:
            self.actors[idx] = actor
            self.actors_save_status[idx] = save_status

        self.set_actor_all()
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
        self._add_or_replace_actor(actor, path=path)
    
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
        self.set_actor_all()

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

    def clean_action(self):
        self.action_listbox.select_clear()
        self.curr_action_idx = None

    def set_action(self, idx):
        if self.curr_actor_idx is None:
            return
        actor_idx = self.curr_actor_idx

        self.clean_actor()
        self.set_actor(actor_idx)
        self.curr_action_idx = idx
        self.action_listbox.select(idx)

    def add_action(self):
        if self.curr_actor_idx is None:
            return
        actor_idx = self.curr_actor_idx
        actor = self.actors[actor_idx]

        action_names = [action.name for action in actor.actions]
        i = 1
        while f"Action {i}" in action_names:
            i += 1

        action = Action(name=f"Action {i}")
        actor.actions.append(action)
        idx = len(actor.actions) - 1

        self.unsaved_actor(actor_idx)
        self.set_action(idx)

    def delete_action(self):
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        actor_idx, action_idx = self.curr_actor_idx, self.curr_action_idx
        actor = self.actors[actor_idx]
        actor.actions.pop(action_idx)

        self.unsaved_actor(actor_idx)
        self.set_actor(actor_idx)

    def select_action(self, event, listbox):
        if self.curr_actor_idx is None:
            return

        idx = listbox.curselection()
        if idx and idx[0] != self.curr_action_idx:
            self.set_action(idx[0])

    def rename_action(self, event, listbox):
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        actor_idx = self.curr_actor_idx
        actor = self.actors[actor_idx]

        def save_action_name(idx: int, name: str):
            actor.actions[idx].name = name
            self.unsaved_actor(actor_idx)
            self.set_action(idx)

        action_idx = self.curr_action_idx
        old_name = actor.actions[action_idx].name
        create_renaming_entry(listbox, actor_idx, old_name, save_action_name)

    def save_actor_as(self):
        if self.curr_actor_idx is None:
            return

        idx = self.curr_actor_idx
        actor = self.actors[idx]
        file_name = actor.name.replace(' ', '_').lower()

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=file_name,
        )
        if not path:
            return

        self.actors_save_status[idx] = (self.actors_save_status[idx][0], path)
        self.save_actor()

    def save_actor(self):
        if self.curr_actor_idx is None:
            return

        idx = self.curr_actor_idx
        path = self.actors_save_status[idx][1]
        if path is None:
            self.save_actor_as()
            return

        actor = self.actors[idx]
        actor_dict = actor.to_dict()

        with open(path, "w") as f:
            json.dump(actor_dict, f, indent=2)

        self.actors_save_status[idx] = (True, path)
        self.set_actor_all()
        self.set_actor(idx)

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