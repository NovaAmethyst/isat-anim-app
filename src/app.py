import json
import tkinter as tk
from PIL import ImageTk
from tkinter import messagebox, ttk
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
        self.actors_save_status: list[tuple[bool, str | None]] = []
        self.curr_actor_idx: Optional[int] = None
        self.curr_action_idx: Optional[int] = None
        self.curr_comp_idx: Optional[int] = None

        self.scenes: list[Scene] = []
        self.scenes_save_status: list[tuple[bool, str | None]] = []
        self.curr_scene_idx: Optional[int] = None
        self.curr_cam_move_idx: Optional[int] = None
        self.curr_sa_idx: Optional[int] = None
        self.curr_sched_idx: Optional[int] = None

        self.create_tabs()
    
    def create_tabs(self):
        self.tab_notebook = ttk.Notebook(self)
        self.tab_notebook.pack(fill="both", expand=True)

        self.actor_frame = tk.Frame(self.tab_notebook)
        self.tab_notebook.add(self.actor_frame, text="Actors")
        self.init_actor_tab()

        self.scene_frame = tk.Frame(self.tab_notebook)
        self.tab_notebook.add(self.scene_frame, text="Scenes")
        self.init_scene_tab()

        def on_tab_change(event):
            notebook = event.widget
            tab_id = notebook.select()
            tab_text = notebook.tab(tab_id, "text")

            if tab_text == "Scenes":
                self.setup_scene_tab()

        self.tab_notebook.bind(
            "<<NotebookTabChanged>>", on_tab_change,
        )
    
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

    def set_actor_list(self):
        self.actor_listbox.set(self.actors)

    def unsaved_actor(self, actor_idx: int):
        self.actors_save_status[actor_idx] = (
            False, self.actors_save_status[actor_idx][1]
        )
        self.set_actor_list()

    def clean_actor(self):
        self.clean_action()

        self.actor_listbox.select_clear()
        self.curr_actor_idx = None

        self.actor_name_label["text"] = ""
        self.action_listbox.clean()

    def set_actor(self, actor_idx: int):
        if actor_idx != self.curr_actor_idx:
            self.clean_action()
        self.curr_actor_idx = actor_idx

        actor = self.actors[actor_idx]
        self.actor_name_label["text"] = actor.name
        self.action_listbox.set(actor.actions)

        self.actor_listbox.select(actor_idx)

    def _add_or_replace_actor(self, actor: Actor, path: str | None = None, idx: int | None = None):
        save_status = (path is not None, path)
        if idx is None:
            idx = len(self.actors)
            self.actors.append(actor)
            self.actors_save_status.append(save_status)
        else:
            self.actors[idx] = actor
            self.actors_save_status[idx] = save_status

        self.set_actor_list()
        self.set_actor(idx)
    
    def add_actor(self):
        actor_names = [actor.name for actor in self.actors]
        i = 1
        while f"Actor {i}" in actor_names:
            i += 1
        
        actor = Actor(name=f"Actor {i}")
        self._add_or_replace_actor(actor)
    
    def open_actor(self):
        file_res = open_json_file()
        if file_res is None:
            return
        path, data = file_res

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
                message=f"The actor '{self.actors[idx].name}' wasn't saved. Delete anyway?",
                icon=messagebox.WARNING,
            )
            if not answer:
                return
        
        self.actors.pop(idx)
        self.actors_save_status.pop(idx)
        self.clean_actor()
        self.set_actor_list()

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

    def set_action(self, action_idx: int):
        if self.curr_actor_idx is None:
            return
        if self.curr_action_idx != action_idx:
            self.clean_component()

        self.curr_action_idx = action_idx
        self.comp_listbox.set(
            self.actors[self.curr_actor_idx].actions[action_idx].components
        )

        self.action_listbox.select(action_idx)

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
        self.set_actor(actor_idx)
        self.set_action(idx)

    def delete_action(self):
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        actor_idx, action_idx = self.curr_actor_idx, self.curr_action_idx
        actor = self.actors[actor_idx]
        actor.actions.pop(action_idx)

        self.unsaved_actor(actor_idx)
        self.set_actor(actor_idx)
        self.clean_action()

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
            self.set_actor(actor_idx)
            self.set_action(idx)

        action_idx = self.curr_action_idx
        old_name = actor.actions[action_idx].name
        create_renaming_entry(listbox, actor_idx, old_name, save_action_name)

    def clean_component(self):
        self.comp_listbox.select_clear()
        self.curr_comp_idx = None

    def set_component(self, component_idx: int):
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        self.curr_comp_idx = component_idx
        self.comp_listbox.select(component_idx)

    def add_or_edit_component(self, new: bool):
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

        def get_popup_content(popup) -> tuple[dict, list[str]]:
            entries = {
                "sprite": ImageFileEntry(
                    popup, "Sprite", default = comp.sprite if comp else None,
                ),
                "duration": FloatEntryFrame(
                    popup, "Duration (s)", comp.duration_sec if comp else 1.0,
                ),
                "x_offset": IntEntryFrame(
                    popup, "X Offset", comp.x_offset if comp else 0,
                ),
                "y_offset": IntEntryFrame(
                    popup, "Y Offset", comp.y_offset if comp else 0,
                ),
            }
            return entries, ["sprite", "duration", "x_offset", "y_offset"]

        def save_component(entries) -> bool:
            sprite = entries["sprite"].get()
            duration = entries["duration"].get()
            x_off = entries["x_offset"].get()
            y_off = entries["y_offset"].get()

            if sprite is None or duration is None or x_off is None or y_off is None:
                return False

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

            self.unsaved_actor(actor_idx)
            self.set_action(action_idx)
            self.set_component(idx)
            return True

        create_add_edit_popup(self, "Action Component", new, get_popup_content, save_component)

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
        path = get_json_save_filepath(actor)
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
        self.set_actor_list()
        self.set_actor(idx)

    def init_scene_tab(self):
        # Left: scene list
        def display_scene(scene: Scene):
            idx = self.scenes.index(scene)
            name = scene.name
            if not self.scenes_save_status[idx][0]:
                name = "*" + name
            return name

        self.scene_listbox = EditableListFrame(
            parent=self.scene_frame,
            display_func=display_scene,
            buttons_info=[
                {"text": "Add Scene", "command": self.add_scene},
                {"text": "Open Scene", "command": self.open_scene},
                {"text": "Delete Scene", "command": self.delete_scene},
            ],
            select_func=self.select_scene,
            double_func=self.rename_scene,
        )
        self.scene_listbox.pack(side="left", fill="y", padx=10, pady=10)

        # Right: scene details, camera definition, actors definition
        scene_detail_frame = tk.Frame(self.scene_frame)
        scene_detail_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Top right: name display, save buttons and scene length setting
        scene_name_frame = tk.Frame(scene_detail_frame)
        scene_name_frame.pack(side="top", fill="x")

        name_save_frame = tk.Frame(scene_name_frame)
        name_save_frame.pack(side="top", fill="x")
        self.scene_name_label = tk.Label(name_save_frame, text="")
        self.scene_name_label.pack(side="left", fill="x")
        tk.Button(name_save_frame, text="Save As", command=self.save_scene_as).pack(side="right", padx=2)
        tk.Button(name_save_frame, text="Save", command=self.save_scene).pack(side="right", padx=2)

        self.scene_setting_frame = tk.Frame(scene_name_frame)
        self.scene_len_entry = FloatEntryFrame(
            parent=self.scene_setting_frame,
            label="Scene length (s)",
        )
        self.scene_len_entry.pack(side="left")
        tk.Button(
            self.scene_setting_frame,
            text="Update Scene Settings",
            command=self.update_scene,
        ).pack(side="left", padx=2)

        # Scene appearance and actors notebook
        self.scene_notebook = ttk.Notebook(scene_detail_frame)

        # Scene appearance
        appearance_frame = tk.Frame(self.scene_notebook)
        self.scene_notebook.add(appearance_frame, text="Appearance")

        # Background
        background_frame = tk.Frame(appearance_frame)
        background_frame.pack(side="top", fill="x")
        tk.Button(background_frame, text="Set Background", command=self.set_background).pack(side="top", pady=2)
        self.background_image = ImageFrame(background_frame, 200)
        self.background_image.pack(side="top", fill="both")

        # Camera details
        camera_frame = tk.Frame(appearance_frame)
        camera_frame.pack(side="bottom", fill="both", expand=True, pady=5)

        # Global camera data
        global_cam_frame = tk.Frame(camera_frame)
        global_cam_frame.pack(side="left", fill="both", expand=True)
        self.cam_width_entry = IntEntryFrame(global_cam_frame, "Camera Width")
        self.cam_width_entry.pack(side="top", fill="x", pady=2)
        self.cam_height_entry = IntEntryFrame(global_cam_frame, "Camera Height")
        self.cam_height_entry.pack(side="top", fill="x", pady=2)
        self.cam_start_x_entry = IntEntryFrame(global_cam_frame, "Camera Start X")
        self.cam_start_x_entry.pack(side="top", fill="x", pady=2)
        self.cam_start_y_entry = IntEntryFrame(global_cam_frame, "Camera Start Y")
        self.cam_start_y_entry.pack(side="top", fill="x", pady=2)
        tk.Button(global_cam_frame, text="Update Camera", command=self.update_cam_settings).pack(side="bottom")

        # Camera moves
        def display_cam_moves(cam_move: CameraMove) -> list[str | None]:
            return [
                None,
                cam_move.linked_sa.actor.name if cam_move.linked_sa else f"({cam_move.x},{cam_move.y})",
                str(cam_move.duration_sec),
            ]

        self.cam_listbox = EditableTreeFrame(
            parent=camera_frame,
            columns=[None, "Actor or (x,y)", "Duration (s)"],
            display_func=display_cam_moves,
            buttons_info=[
                {"text": "Add Camera Move", "command": lambda: self.add_or_edit_camera_move(True)},
                {"text": "Edit Camera Move", "command": lambda: self.add_or_edit_camera_move(False)},
                {"text": "Delete Camera Move", "command": self.delete_camera_move},
            ],
            btns_per_row=3,
            select_func=self.select_camera_move,
        )
        self.cam_listbox.pack(side="right", fill="both", expand=True)

        # Scene actors and actions
        scene_actor_frame = tk.Frame(self.scene_notebook)
        self.scene_notebook.add(scene_actor_frame, text="Actors")

        # Scene actor list
        def display_scene_actor(sa: SceneActor) -> list[None| str]:
            return [None, sa.actor.name, f"({sa.start_x},{sa.start_y})"]

        self.sa_listbox = EditableTreeFrame(
            parent=scene_actor_frame,
            columns=[None, "Name", "(x,y)"],
            display_func=display_scene_actor,
            buttons_info=[
                {"text": "Add Actor", "command": self.add_scene_actor},
                {"text": "Edit Actor", "command": self.edit_scene_actor},
                {"text": "Delete Actor", "command": self.delete_scene_actor},
                {"text": "Move Up", "command": lambda: self.move_scene_actor(-1)},
                {"text": "Move Down", "command": lambda: self.move_scene_actor(1)},
            ],
            btns_per_row=5,
            select_func=self.select_scene_actor,
        )
        self.sa_listbox.pack(side="top", fill="both", expand=True)

        # Scheduled action list
        def display_scheduled_action(sched: ScheduledAction) -> list[None | str]:
            return [
                None,
                sched.action.name,
                str(sched.duration_sec),
                str(sched.start_offset_sec)
            ]

        self.sched_listbox = EditableTreeFrame(
            parent=scene_actor_frame,
            columns=[None, "Name", "Duration (s)", "Start offset (s)"],
            display_func=display_scheduled_action,
            buttons_info=[
                {
                    "text": "Add Action",
                    "command": lambda: self.add_or_edit_scheduled_action(True),
                },
                {
                    "text": "Edit Action",
                    "command": lambda: self.add_or_edit_scheduled_action(False),
                },
                {"text": "Delete Action", "command": self.delete_scheduled_action},
            ],
            btns_per_row=5,
            select_func=self.select_scheduled_action,
        )
        self.sched_listbox.pack(side="top", fill="both", expand=True)

    def setup_scene_tab(self):
        scene_idx = self.curr_scene_idx
        cam_idx = self.curr_cam_move_idx
        sa_idx = self.curr_sa_idx
        sched_idx = self.curr_sched_idx

        self.set_scene_list()
        if scene_idx is not None:
            self.set_scene(scene_idx)
        if cam_idx is not None:
            self.set_cam_move(cam_idx)
        if sa_idx is not None:
            self.set_scene_actor(sa_idx)
        if sched_idx is not None:
            self.set_scheduled_action(sched_idx)

    def unsaved_scene(self, idx: int):
        self.scenes_save_status[idx] = (False, self.scenes_save_status[idx][1])
        self.set_scene_list()

    def set_scene_list(self):
        self.scene_listbox.set(self.scenes)

    def clean_scene(self):
        self.clean_cam_move()
        self.clean_scene_actor()
        self.curr_scene_idx = None
        self.scene_listbox.select_clear()
        self.scene_notebook.pack_forget()
        self.scene_setting_frame.pack_forget()
        self.scene_name_label["text"] = ""
        self.sa_listbox.clean()

    def set_scene(self, scene_idx: int):
        if self.curr_scene_idx != scene_idx:
            self.clean_action()
            self.clean_cam_move()

        if self.curr_scene_idx is None:
            self.scene_setting_frame.pack(side="top", fill="x")
            self.scene_notebook.pack(side="top", fill="both", expand=True)

        self.curr_scene_idx = scene_idx
        scene = self.scenes[scene_idx]

        self.scene_len_entry.set(scene.duration_sec)
        self.scene_name_label["text"] = scene.name
        if scene.background is None:
            self.background_image.clean()
        else:
            self.background_image.set(scene.background)
        self.sa_listbox.set(scene.actors)

        cam = scene.camera
        self.cam_width_entry.set(cam.width)
        self.cam_height_entry.set(cam.height)
        self.cam_start_x_entry.set(cam.start_x)
        self.cam_start_y_entry.set(cam.start_y)
        self.cam_listbox.set(cam.moves)

        self.scene_listbox.select(scene_idx)

    def add_scene(self):
        scene_names = [scene.name for scene in self.scenes]
        i = 1
        while f"Scene {i}" in scene_names:
            i += 1
        scene = Scene(name=f"Scene {i}")
        self.scenes.append(scene)
        self.scenes_save_status.append((False, None))

        self.set_scene_list()
        self.set_scene(len(self.scenes) - 1)

    def open_scene(self):
        file_res = open_json_file()
        if file_res is None:
            return
        path, data = file_res

        scene = Scene.from_dict(data)

        self.scenes.append(scene)
        self.scenes_save_status.append((True, path))

        self.set_scene_list()
        self.set_scene(len(self.scenes) - 1)

    def delete_scene(self):
        if self.curr_scene_idx is None:
            return
        idx = self.curr_scene_idx

        if not self.scenes_save_status[idx][0]:
            answer = messagebox.askokcancel(
                title="Confirmation",
                message=f"The scene '{self.scenes[idx].name}' wasn't saved. Delete anyway?",
                icon=messagebox.WARNING,
            )
            if not answer:
                return

        self.scenes.pop(idx)
        self.scenes_save_status.pop(idx)
        self.clean_scene()
        self.set_scene_list()

    def select_scene(self, event, listbox):
        idx = listbox.curselection()
        if idx and idx[0] != self.curr_scene_idx:
            self.set_scene(idx[0])

    def rename_scene(self, event, listbox):
        if self.curr_scene_idx is None:
            return

        def save_scene_name(idx: int, name: str) -> None:
            self.scenes[idx].name = name
            self.unsaved_scene(idx)
            self.set_scene(idx)

        scene_idx = self.curr_scene_idx
        old_name = self.scenes[scene_idx].name
        create_renaming_entry(listbox, scene_idx, old_name, save_scene_name)

    def update_scene(self):
        if self.curr_scene_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]

        scene_len = self.scene_len_entry.get()
        if scene_len is None:
            return
        scene.duration_sec = scene_len
        self.unsaved_scene(scene_idx)

    def set_background(self):
        if self.curr_scene_idx is None:
            return

        idx = self.curr_scene_idx
        scene = self.scenes[idx]

        img = open_image_file()
        if img is None:
            return

        scene.background = img
        self.background_image.set(img)
        self.unsaved_scene(idx)

    def update_cam_settings(self):
        if self.curr_scene_idx is None:
            return

        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        cam = scene.camera

        width = self.cam_width_entry.get()
        height = self.cam_height_entry.get()
        start_x = self.cam_start_x_entry.get()
        start_y = self.cam_start_y_entry.get()

        cam.width = width
        cam.height = height
        cam.start_x = start_x
        cam.start_y = start_y

        self.unsaved_scene(scene_idx)

    def clean_cam_move(self):
        self.curr_cam_move_idx = None
        self.cam_listbox.select_clear()

    def set_cam_move(self, move_idx: int):
        if self.curr_scene_idx is None:
            return
        self.curr_cam_move_idx = move_idx
        self.cam_listbox.select(move_idx)

    def add_or_edit_camera_move(self, new: bool):
        if self.curr_scene_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        cam = scene.camera

        cam_move = None
        idx = len(cam.moves)
        if not new:
            if self.curr_cam_move_idx is None:
                return
            idx = self.curr_cam_move_idx
            cam_move = cam.moves[idx]

        actor_names = [sa.actor.name for sa in scene.actors]

        def get_popup_content(popup) -> tuple[dict, list[str]]:
            toggle = ToggleFrame(
                parent=popup,
                toggle_label="Is linked",
                toggle_default=(cam_move.linked_sa is not None) if cam_move else False,
            )
            false_frame = toggle.frame_false
            true_frame = toggle.frame_true

            entries = {
                "toggle": toggle,
                "linked_actor": DropdownEntry(
                    parent=true_frame,
                    label="Linked Actor",
                    options=actor_names,
                    default=cam_move.linked_sa.actor.name if (cam_move and cam_move.linked_sa) else None,
                ),
                "x_coord": IntEntryFrame(false_frame, "X Offset", cam_move.x if cam_move else 0),
                "y_coord": IntEntryFrame(false_frame, "Y Offset", cam_move.y if cam_move else 0),
                "duration": FloatEntryFrame(popup, "Duration (s)", cam_move.duration_sec if cam_move else 1.0),
            }
            return entries, ["toggle", "linked_actor", "x_coord", "y_coord", "duration"]

        def save_cam_move(entries) -> bool:
            duration = entries["duration"].get()
            if duration is None:
                return False

            if entries["toggle"].get():
                actor_name = entries["linked_actor"].get()
                if actor_name is None:
                    return False
                actor_idx = actor_names.index(actor_name)
                actor = scene.actors[actor_idx]
                new_cam_move = CameraMove(linked_sa=actor, duration_sec=duration)
            else:
                x = entries["x_coord"].get()
                y = entries["y_coord"].get()
                if x is None or y is None:
                    return False
                new_cam_move = CameraMove(x=x, y=y, duration_sec=duration)

            if new:
                cam.moves.append(new_cam_move)
            else:
                cam.moves[idx] = new_cam_move

            self.unsaved_scene(scene_idx)
            self.set_scene(scene_idx)
            self.set_cam_move(idx)
            return True

        create_add_edit_popup(self, "Camera Movement", new, get_popup_content, save_cam_move)

    def delete_camera_move(self):
        if self.curr_scene_idx is None or self.curr_cam_move_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        cam = scene.camera
        cam.moves.pop(self.curr_cam_move_idx)
        self.clean_cam_move()
        self.unsaved_scene(scene_idx)
        self.set_scene(scene_idx)

    def select_camera_move(self, event, treeview):
        if self.curr_scene_idx is None:
            return

        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_cam_move_idx:
                self.set_cam_move(idx)

    def clean_scene_actor(self):
        self.clean_scheduled_action()
        self.curr_sa_idx = None
        self.sched_listbox.clean()
        self.sa_listbox.select_clear()

    def set_scene_actor(self, sa_idx: int, clean: bool = True):
        if self.curr_scene_idx is None:
            return
        if self.curr_sa_idx != sa_idx and clean:
            self.clean_scheduled_action()

        self.curr_sa_idx = sa_idx
        sa = self.scenes[self.curr_scene_idx].actors[sa_idx]
        self.sched_listbox.set(sa.scheduled_actions)

        self.sa_listbox.select(sa_idx)

    def add_scene_actor(self):
        if self.curr_scene_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]

        if len(self.actors) == 0:
            messagebox.showinfo(
                "No actors",
                "There are no actors defined. Please create at least one actor first."
            )
            return

        actor_names = [actor.name for actor in self.actors]

        popup = tk.Toplevel(self)
        popup.title("Add Actor to Scene")

        actor_entry = DropdownEntry(
            popup, "Actor", actor_names,
        )
        actor_entry.pack(side="top", fill="x", pady=1)
        start_x_entry = IntEntryFrame(popup, "Start X Coord")
        start_x_entry.pack(side="top", pady=1)
        start_y_entry = IntEntryFrame(popup, "Start Y Coord")
        start_y_entry.pack(side="top", pady=1)

        def add_and_close():
            actor_name, start_x, start_y = actor_entry.get(), start_x_entry.get(), start_y_entry.get()
            if actor_name is None or start_x is None or start_y is None:
                return
            actor_idx = actor_names.index(actor_name)
            sa = SceneActor(actor=self.actors[actor_idx], start_x=start_x, start_y=start_y)
            scene.actors.append(sa)
            self.unsaved_scene(scene_idx)
            self.set_scene(scene_idx)
            self.set_scene_actor(len(scene.actors) - 1)
            popup.destroy()

        tk.Button(popup, text="Add", command=add_and_close).pack(side="bottom", pady=10)

    def edit_scene_actor(self):
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        sa_idx = self.curr_sa_idx
        sa = scene.actors[sa_idx]

        popup = tk.Toplevel(self)
        popup.title("Edit Actor")

        start_x_entry = IntEntryFrame(popup, "Start X Coord", sa.start_x)
        start_x_entry.pack(side="top", fill="x", pady=1)
        start_y_entry = IntEntryFrame(popup, "Start Y Coord", sa.start_y)
        start_y_entry.pack(side="top", fill="x", pady=1)

        def edit_and_close():
            start_x, start_y = start_x_entry.get(), start_y_entry.get()
            if start_x is None or start_y is None:
                return
            sa.start_x = start_x
            sa.start_y = start_y
            self.unsaved_scene(scene_idx)
            self.set_scene(scene_idx)
            self.set_scene_actor(sa_idx)
            popup.destroy()

        tk.Button(popup, text="Edit", command=edit_and_close).pack(side="bottom", pady=10)

    def delete_scene_actor(self):
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        sa_idx = self.curr_sa_idx

        scene.actors.pop(sa_idx)
        self.clean_scene_actor()
        self.unsaved_scene(scene_idx)
        self.set_scene(scene_idx)

    def select_scene_actor(self, event, treeview):
        if self.curr_scene_idx is None:
            return

        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_sa_idx:
                self.set_scene_actor(idx)

    def move_scene_actor(self, delta: int):
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        sa_idx = self.curr_sa_idx

        n_idx = max(0, min(sa_idx + delta, len(scene.actors) - 1))
        if n_idx == sa_idx:
            return
        actor = scene.actors.pop(sa_idx)
        scene.actors.insert(n_idx, actor)
        self.unsaved_scene(scene_idx)
        self.set_scene(scene_idx)
        self.set_scene_actor(n_idx, clean=False)

    def clean_scheduled_action(self):
        self.sched_listbox.select_clear()
        self.curr_sched_idx = None

    def set_scheduled_action(self, sched_idx: int):
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        self.curr_sched_idx = sched_idx
        self.sched_listbox.select(sched_idx)

    def add_or_edit_scheduled_action(self, new: bool):
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        sa_idx = self.curr_sa_idx
        sa = scene.actors[sa_idx]

        sched = None
        idx = len(sa.scheduled_actions)
        if not new:
            if self.curr_sched_idx is None:
                return
            idx = self.curr_sched_idx
            sched = sa.scheduled_actions[idx]

        action_names = [action.name for action in sa.actor.actions]

        def get_popup_content(popup) -> tuple[dict, list[str]]:
            toggle = ToggleFrame(
                parent=popup,
                toggle_label="Is Idle",
                toggle_default=sched.action.name == "Idle" if sched else False,
            )
            false_frame = toggle.frame_false
            true_frame = toggle.frame_true
            is_visible_var = tk.BooleanVar(value=sched.is_visible if sched else True)

            entries = {
                "toggle": toggle,
                "idle_sprite": ImageFileEntry(
                    parent=true_frame,
                    label="Sprite",
                    default=sched.action.components[0].sprite if sched and sched.action.name == "Idle" else None,
                ),
                "action_name": DropdownEntry(
                    parent=false_frame,
                    label="Action",
                    options=action_names,
                    default=sched.action.name if sched else None,
                ),
                "duration": FloatEntryFrame(
                    parent=popup,
                    label="Duration (s)",
                    default=sched.duration_sec if sched else 1.0,
                ),
                "start_offset": FloatEntryFrame(
                    parent=popup,
                    label="Start Offset (s):",
                    default=sched.start_offset_sec if sched else 0.0,
                ),
                "is_visible": is_visible_var,
                "visible_check": ttk.Checkbutton(
                    popup, text="Is Visible", variable=is_visible_var, onvalue=True, offvalue=False,
                ),
            }
            return entries, ["toggle", "idle_sprite", "action_name", "duration", "start_offset", "visible_check"]

        def save_sched(entries) -> bool:
            duration = entries["duration"].get()
            start_offset = entries["start_offset"].get()
            is_visible = entries["is_visible"].get()
            if duration is None or start_offset is None or is_visible is None:
                return False

            if entries["toggle"].get():
                idle_sprite = entries["idle_sprite"].get()
                if idle_sprite is None:
                    return False
                action = Action("Idle", components=[ActionComponent(idle_sprite, 1.0, 0, 0)])
            else:
                action_name = entries["action_name"].get()
                if action_name is None:
                    return False
                action_idx = action_names.index(action_name)
                action = sa.actor.actions[action_idx]

            new_sched = ScheduledAction(
                action=action,
                duration_sec=duration,
                start_offset_sec=start_offset,
                is_visible=is_visible,
            )

            if new:
                sa.scheduled_actions.append(new_sched)
            else:
                sa.scheduled_actions[idx] = new_sched
            self.unsaved_scene(scene_idx)
            self.set_scene_actor(sa_idx)
            self.set_scheduled_action(idx)
            return True

        create_add_edit_popup(self, "Scheduled Action", new, get_popup_content, save_sched)

    def delete_scheduled_action(self):
        if self.curr_scene_idx is None or self.curr_sa_idx is None or self.curr_sched_idx is None:
            return
        scene_idx = self.curr_scene_idx
        scene = self.scenes[scene_idx]
        sa_idx = self.curr_sa_idx
        sa = scene.actors[sa_idx]
        sched_idx = self.curr_sched_idx

        sa.scheduled_actions.pop(sched_idx)
        self.clean_scheduled_action()
        self.unsaved_scene(scene_idx)
        self.set_scene_actor(sa_idx)

    def select_scheduled_action(self, event, treeview):
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return

        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_sched_idx:
                self.set_scheduled_action(idx)

    def save_scene_as(self):
        if self.curr_scene_idx is None:
            return

        idx = self.curr_scene_idx
        scene = self.scenes[idx]

        path = get_json_save_filepath(scene)
        if not path:
            return
        self.scenes_save_status[idx] = (self.scenes_save_status[idx][0], path)
        self.save_scene()

    def save_scene(self):
        if self.curr_scene_idx is None:
            return

        idx = self.curr_scene_idx
        path = self.scenes_save_status[idx][1]
        if path is None:
            self.save_scene_as()
            return

        scene = self.scenes[idx]
        scene_dict = scene.to_dict()

        with open(path, "w") as f:
            json.dump(scene_dict, f, indent=2)

        self.scenes_save_status[idx] = (True, path)
        self.set_scene_list()

    def window_close(self):
        unsaved_actors = False
        for status in self.actors_save_status:
            if not status[0]:
                unsaved_actors = True
                break

        unsaved_scenes = False
        for status in self.scenes_save_status:
            if not status[0]:
                unsaved_scenes = True
                break

        if not unsaved_actors and not unsaved_scenes:
            self.quit()
            return
        
        unsaved_kind = ""
        if unsaved_actors:
            unsaved_kind += "actors"
            if unsaved_scenes:
                unsaved_kind += " and "
        if unsaved_scenes:
            unsaved_kind += "scenes"
        
        message = f"There are unsaved {unsaved_kind}. Close the window anyway?"

        answer = messagebox.askokcancel(
            title="Confirmation",
            message=message,
            icon=messagebox.WARNING,
        )

        if answer:
            self.quit()