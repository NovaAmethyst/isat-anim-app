import json
import tkinter as tk
from PIL import ImageTk
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
        self.curr_comp_idx: Optional[int] = None

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

        # Bottom right: action component list
        def display_component(comp: ActionComponent) -> list[ImageTk.PhotoImage | str]:
            return [
                ImageTk.PhotoImage(comp.sprite.resize((16, 16))),
                str(comp.duration_sec),
                f"({comp.x_offset},{comp.y_offset})",
            ]

        self.comp_listbox = EditableTreeFrame(
            parent=actor_detail_frame,
            columns=["Sprite", "Duration (s)", "(x, y)"],
            display_func=display_component,
            buttons_info=[
                {
                    "text": "Add Component",
                    "command": lambda: self.add_or_edit_component(new=True)
                },
                {
                    "text": "Edit Component",
                    "command": lambda: self.add_or_edit_component(new=False)
                },
                {"text": "Delete Component", "command": self.delete_component},
            ],
            btns_per_row=4,
            select_func=self.select_component,
        )
        self.comp_listbox.pack(side="top", fill="both", expand=True)

    def set_actor_all(self):
        actor_idx = self.curr_actor_idx
        action_idx = self.curr_action_idx
        comp_idx = self.curr_comp_idx

        self.clean_actor()
        self.actor_listbox.clean()

        self.actor_listbox.set(self.actors)
        if comp_idx is not None:
            self.set_component(comp_idx)
        elif action_idx is not None:
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
        self.action_listbox.clean()

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
        self.clean_component()
        self.action_listbox.select_clear()
        self.curr_action_idx = None

        self.comp_listbox.clean()

    def set_action(self, idx):
        if self.curr_actor_idx is None:
            return
        actor_idx = self.curr_actor_idx

        self.clean_actor()
        self.set_actor(actor_idx)
        self.curr_action_idx = idx
        self.action_listbox.select(idx)

        actor = self.actors[actor_idx]
        action = actor.actions[idx]
        self.comp_listbox.set(action.components)

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

    def clean_component(self):
        self.comp_listbox.select_clear()
        self.curr_comp_idx = None

    def set_component(self, idx):
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return
        action_idx = self.curr_action_idx

        self.clean_action()
        self.set_action(action_idx)
        self.curr_comp_idx = idx
        self.comp_listbox.select(idx)

    def add_or_edit_component(self, new):
        print(self.curr_actor_idx, self.curr_action_idx, self.curr_comp_idx)
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        actor_idx = self.curr_actor_idx
        actor = self.actors[actor_idx]
        action_idx = self.curr_action_idx
        action = actor.actions[action_idx]

        comp = None
        idx = len(action.components)
        if not new:
            if self.curr_comp_idx is None:
                return
            idx = self.curr_comp_idx
            comp = action.components[idx]

        window_type = "Add" if new else "Edit"

        popup = tk.Toplevel(self)
        popup.title(f"{window_type} Action Component")

        sprite_entry = ImageFileEntry(
            popup, "Sprite", default = comp.sprite if comp else None,
        )
        sprite_entry.pack(side="top", fill="x", pady=1)

        duration_entry = FloatEntryFrame(
            popup, "Duration (s)", comp.duration_sec if comp else 1.0,
        )
        duration_entry.pack(side="top", fill="x", pady=1)

        x_off_entry = IntEntryFrame(
            popup, "X Offset", comp.x_offset if comp else 0,
        )
        x_off_entry.pack(side="top", fill="x", pady=1)

        y_off_entry = IntEntryFrame(
            popup, "Y Offset", comp.y_offset if comp else 0,
        )
        y_off_entry.pack(side="top", fill="x", pady=1)

        def save_component():
            sprite = sprite_entry.get()
            duration = duration_entry.get()
            x_off = x_off_entry.get()
            y_off = y_off_entry.get()

            if sprite is None or duration is None or x_off is None or y_off is None:
                return

            new_comp = ActionComponent(
                sprite=sprite,
                duration_sec=duration,
                x_offset=x_off,
                y_offset=y_off,
            )
            if new:
                action.components.append(new_comp)
            else:
                action.components[idx] = new_comp

            popup.destroy()
            self.unsaved_actor(actor_idx)
            self.set_component(idx)

        tk.Button(popup, text=window_type, command=save_component).pack(pady=10)

    def delete_component(self):
        if self.curr_actor_idx is None or self.curr_action_idx is None or self.curr_comp_idx is None:
            return

        actor_idx = self.curr_actor_idx
        actor = self.actors[actor_idx]
        action_idx = self.curr_action_idx
        action = actor.actions[action_idx]
        action.components.pop(self.curr_comp_idx)

        self.clean_component()
        self.unsaved_actor(actor_idx)
        self.set_action(action_idx)

    def select_component(self, event, treeview):
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_comp_idx:
                self.set_component(idx)

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