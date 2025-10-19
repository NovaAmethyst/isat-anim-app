"""
Defines the main class used for the app.

Classes
-------
AnimationEditorApp
"""

import json
import tkinter as tk
import numpy as np
import numpy.typing as npt
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from src.data_models import *
from src.utils.anims import *
from src.widgets import *
from src.widgets.utils import create_renaming_entry


class AnimationEditorApp(tk.Tk):
    """
    The class used to run the animation app

    Attributes
    ----------
    action_listbox: EditableListFrame
        the list of actions of the selected actor
    actor_frame : tk.Frame
        the tkinter frame displaying info in the actors tab
    actor_listbox : EditableListFrame
        the list of actors accessible to the user
    actor_name_label : tk.Label
        the tkinter label to display the name of the selected actor
    actors : list[Actor]
        the actors accessible in the Actors tab
    actors_save_status : list[tuple[bool, str | None]]
        the save status and save file path of each actor
    background_image : ImageFrame
        the frame to display the scene background
    cam_height_entry : IntEntryFrame
        the entry to define the camera height
    cam_listbox : EditableTreeFrame
        the treeview to display camera movements
    cam_start_x_entry: IntEntryFrame
        the entry to define the camera's starting x coordinate
    cam_start_y_entry : IntEntryFrame
        the entry to define the camera's starting y coordinate
    cam_width_entry : IntEntryFrame
        the entry to define the camera width
    comp_listbox: EditableTreeFrame
        the list of action components of the selected action
    curr_actor_idx : int | None
        the index of the current selected actor
    curr_action_idx : int | None
        the index of the current selected action
    curr_cam_move_idx : int | None
        the index of the current selected camera movement
    curr_comp_idx : int | None
        the index of the current selected action component
    curr_sa_idx : int | None
        the index of the current selected scene actor
    curr_scene_idx : int | None
        the index of the current selected scene
    curr_sched_idx : int | None
        the index of the current selected scheduled action
    sa_listbox : EditableTreeFrame
        the treeview to display scene actors
    scene_frame : tk.Frame
        the tkinter frame displaying info on the scenes tab
    scene_len_entry : FloatEntryFrame
        the entry to input the duration of the scene
    scene_listbox : EditableListFrame
        the list of scenes accessible to the user
    scene_name_label : tk.Label
        the tkinter label to display the name of the selected scene
    scene_notebook : ttk.Notebook
        the notebook to display scene camera and actors tabs
    scene_setting_frame : tk.Frame
        the frame to display global scene settings
    scenes : list[Scene]
        the scenes accessible in the Scenes tab
    scenes_save_status : list[tuple[bool, str | None]]
        the save status and save file path of each scene
    sched_listbox : EditableTreeFrame
        the treeview to display scheduled actions
    """
    def __init__(self):
        """Setups the application."""
        super().__init__()
        # Set app title and clean closing
        self.title("Animation Editor")
        self.protocol("WM_DELETE_WINDOW", self.window_close)

        # Initialize actor tab variables
        self.actors: list[Actor] = []
        self.actors_save_status: list[tuple[bool, str | None]] = []
        self.curr_actor_idx: Optional[int] = None
        self.curr_action_idx: Optional[int] = None
        self.curr_comp_idx: Optional[int] = None

        # Initialize scene tab variables
        self.scenes: list[Scene] = []
        self.scenes_save_status: list[tuple[bool, str | None]] = []
        self.curr_scene_idx: Optional[int] = None
        self.curr_cam_move_idx: Optional[int] = None
        self.curr_sa_idx: Optional[int] = None
        self.curr_sched_idx: Optional[int] = None

        # Create scene and actor tabs
        self.create_tabs()
    
    def create_tabs(self) -> None:
        """Creates and sets up the actors/scenes tab system."""
        # Create the tab system
        tab_notebook: ttk.Notebook = ttk.Notebook(self)
        tab_notebook.pack(fill="both", expand=True)

        # Setup the Actors tab
        self.actor_frame: tk.Frame = tk.Frame(tab_notebook)
        tab_notebook.add(self.actor_frame, text="Actors")
        self.init_actor_tab()

        # Setup the Scenes tab
        self.scene_frame: tk.Frame = tk.Frame(tab_notebook)
        tab_notebook.add(self.scene_frame, text="Scenes")
        self.init_scene_tab()

        # Define re-actualisation function for scene tab
        def on_tab_change(event: tk.Event):
            notebook: tk.Misc = event.widget
            tab_id = notebook.select()
            tab_text: str = notebook.tab(tab_id, "text")

            if tab_text == "Scenes":
                self.setup_scene_tab()

        # Bind scenes re-actualisation to tab change
        tab_notebook.bind(
            "<<NotebookTabChanged>>", on_tab_change,
        )
    
    def init_actor_tab(self) -> None:
        """Sets up all widgets and events for the Actors tab."""
        # Left: actor list
        def display_actor(actor: Actor) -> str:
            idx: int = self.actors.index(actor)
            name: str = actor.name
            # Display whether the actor is saved
            if not self.actors_save_status[idx][0]:
                name = '*' + name
            return name

        self.actor_listbox: EditableListFrame = EditableListFrame(
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
        actor_detail_frame: tk.Frame = tk.Frame(self.actor_frame)
        actor_detail_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Top right: name display and save buttons
        actor_name_frame: tk.Frame = tk.Frame(actor_detail_frame)
        actor_name_frame.pack(side="top", fill="x")
        self.actor_name_label: tk.Label = tk.Label(actor_name_frame, text="")
        self.actor_name_label.pack(side="left", fill="x")
        tk.Button(actor_name_frame, text="Save As", command=self.save_actor_as).pack(side="right", padx=2)
        tk.Button(actor_name_frame, text="Save", command=self.save_actor).pack(side="right", padx=2)

        # Middle right: action list
        def display_action(action: Action) -> str:
            return action.name

        self.action_listbox: EditableListFrame = EditableListFrame(
            parent=actor_detail_frame,
            display_func=display_action,
            buttons_info=[
                {"text": "Add Action", "command": self.add_action},
                {"text": "Delete Action", "command": self.delete_action},
                {"text": "Preview Action", "command": self.preview_action},
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

        self.comp_listbox: EditableTreeFrame = EditableTreeFrame(
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

    def set_actor_list(self) -> None:
        """Reactualizes the actor list."""
        self.actor_listbox.set(self.actors)

    def unsaved_actor(self, actor_idx: int) -> None:
        """
        Puts the save status of a given actor to False and reactualizes actor list.

        Parameters
        ----------
        actor_idx : int
            the index of the actor to set as unsaved

        Returns
        -------
        None
        """
        self.actors_save_status[actor_idx] = (
            False, self.actors_save_status[actor_idx][1]
        )
        self.set_actor_list()

    def clean_actor(self) -> None:
        """Resets displays and attributes present due to an actor being selected."""
        self.clean_action()

        # Removes actor selection
        self.actor_listbox.select_clear()
        self.curr_actor_idx = None

        # Cleans all info related to selected actor
        self.actor_name_label["text"] = ""
        self.action_listbox.clean()

    def set_actor(self, actor_idx: int) -> None:
        """
        Handles the selection of an actor in the list.

        Parameters
        ----------
        actor_idx : int
            the index of the selected actor

        Returns
        -------
        None
        """
        # Clean only if there is an index change
        if actor_idx != self.curr_actor_idx:
            self.clean_action()
        self.curr_actor_idx = actor_idx

        # Set all displays for selected actor
        actor: Actor = self.actors[actor_idx]
        self.actor_name_label["text"] = actor.name
        self.action_listbox.set(actor.actions)

        # Select the correct actor in the list
        self.actor_listbox.select(actor_idx)

    def _add_or_replace_actor(self, actor: Actor, path: str | None = None, idx: int | None = None) -> None:
        """
        Either adds an actor at the end of the list or replaces the one at the given index with it.

        Parameters
        ----------
        actor : Actor
            the actor to place in the actors list
        path : str | None
            the optional path the actor was saved in
        idx : int | None
            the index of the actor to replace

        Returns
        -------
        None
        """
        # Set the actor's save status
        save_status: tuple[bool, str] = (path is not None, path)
        if idx is None:
            # Insert actor if no index is given
            idx = len(self.actors)
            self.actors.append(actor)
            self.actors_save_status.append(save_status)
        else:
            # Replace an actor if an index is given
            self.actors[idx] = actor
            self.actors_save_status[idx] = save_status

        # Set the right displays
        self.set_actor_list()
        self.set_actor(idx)
    
    def add_actor(self) -> None:
        """Creates a new actor in the actor list."""
        # Find a non pre-existing actor name
        actor_names: list[str] = [actor.name for actor in self.actors]
        i: int = 1
        while f"Actor {i}" in actor_names:
            i += 1

        # Add new actor to the actor list
        actor: Actor = Actor(name=f"Actor {i}")
        self._add_or_replace_actor(actor)
    
    def open_actor(self) -> None:
        """Asks user for an actor file to open in the actor list."""
        # Ask for and open file
        file_res: tuple[str, dict] | None = open_json_file()
        if file_res is None:
            return
        path, data = file_res

        # Create the opened actor
        actor: Actor = Actor.from_dict(data)
        # TODO add checks and behaviour for opening actor with pre-existing name in register
        # Add opened actor to the actor list
        self._add_or_replace_actor(actor, path=path)
    
    def delete_actor(self) -> None:
        """Removes the selected actor from the actor list."""
        # Skip if no actor is selected
        if self.curr_actor_idx is None:
            return
        idx: int = self.curr_actor_idx

        # Ask user for confirmation if non saved changes are detected
        if not self.actors_save_status[idx][0]:
            answer: bool = messagebox.askokcancel(
                title="Confirmation",
                message=f"The actor '{self.actors[idx].name}' wasn't saved. Delete anyway?",
                icon=messagebox.WARNING,
            )
            if not answer:
                return

        # Remove the actor and stop displaying associated information
        self.actors.pop(idx)
        self.actors_save_status.pop(idx)
        self.clean_actor()
        self.set_actor_list()

    def select_actor(self, event: tk.Event, listbox: tk.Listbox) -> None:
        """
        Handles the selection of an actor in a listbox.

        Parameters
        ----------
        event : tk.Event
            the selection event
        listbox : tk.Listbox
            the listbox the selection happened in

        Returns
        -------
        None
        """
        idx: tuple = listbox.curselection()
        # Change actor display only on index change
        if idx and idx[0] != self.curr_actor_idx:
            self.set_actor(idx[0])
    
    def rename_actor(self, event: tk.Event, listbox: tk.Listbox) -> None:
        """
        Creates a tkinter entry to rename the selected actor.

        Parameters
        ----------
        event : tk.Event
            the double click event
        listbox : tk.Listbox
            the listbox the double clock happened in

        Returns
        -------
        None
        """
        # Skip if no actor selected
        if self.curr_actor_idx is None:
            return

        # Function to update the name of a given actor
        def save_actor_name(idx: int, name: str) -> None:
            self.actors[idx].name = name
            self.unsaved_actor(idx)
            self.set_actor(idx)

        # Create rename entry associated with name update function
        actor_idx: int = self.curr_actor_idx
        old_name: str = self.actors[actor_idx].name
        create_renaming_entry(listbox, actor_idx, old_name, save_actor_name)

    def clean_action(self) -> None:
        """Resets displays and attributes present due to an action being selected."""
        # Removes action selection
        self.clean_component()
        self.action_listbox.select_clear()
        self.curr_action_idx = None

        # Cleans all info related to selected actor
        self.comp_listbox.clean()

    def set_action(self, action_idx: int) -> None:
        """
        Handles the selection of an action in the list.

        Parameters
        ----------
        action_idx : int
            the index of the selected action

        Returns
        -------
        None
        """
        # Skip if no actor is selected
        if self.curr_actor_idx is None:
            return
        # Clean only if there is an index change
        if self.curr_action_idx != action_idx:
            self.clean_component()

        # Set all displays for selected action
        self.curr_action_idx = action_idx
        self.comp_listbox.set(
            self.actors[self.curr_actor_idx].actions[action_idx].components
        )

        # Select the correct action in the list
        self.action_listbox.select(action_idx)

    def add_action(self) -> None:
        """Creates a new action in the action list."""
        # Skip if no actor is selected
        if self.curr_actor_idx is None:
            return
        # Get the selected actor
        actor_idx: int = self.curr_actor_idx
        actor: Actor = self.actors[actor_idx]

        # Loop for a new name in the actor's actions
        action_names: list[str] = [action.name for action in actor.actions]
        i: int = 1
        while f"Action {i}" in action_names:
            i += 1

        # Create and add new action
        action: Action = Action(name=f"Action {i}")
        actor.actions.append(action)
        idx: int = len(actor.actions) - 1

        # Update actor save status and displays
        self.unsaved_actor(actor_idx)
        self.set_actor(actor_idx)
        self.set_action(idx)

    def delete_action(self) -> None:
        """Removes the selected action from the action list."""
        # Skip if no actor or action is selected
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        # Remove selected action from actor
        actor_idx, action_idx = self.curr_actor_idx, self.curr_action_idx
        actor: Actor = self.actors[actor_idx]
        actor.actions.pop(action_idx)

        # Update displays
        self.unsaved_actor(actor_idx)
        self.set_actor(actor_idx)
        self.clean_action()

    def select_action(self, event: tk.Event, listbox: tk.Listbox) -> None:
        """
        Handles the selection of an action in a listbox.

        Parameters
        ----------
        event : tk.Event
            the selection event
        listbox : tk.Listbox
            the listbox the selection happened in

        Returns
        -------
        None
        """
        # Skip if no actor selected
        if self.curr_actor_idx is None:
            return

        idx: tuple = listbox.curselection()
        # Change display if index changed
        if idx and idx[0] != self.curr_action_idx:
            self.set_action(idx[0])

    def rename_action(self, event: tk.Event, listbox: tk.Listbox) -> None:
        """
        Creates a tkinter entry to rename the selected action.

        Parameters
        ----------
        event : tk.Event
            the double click event
        listbox : tk.Listbox
            the listbox the double clock happened in

        Returns
        -------
        None
        """
        # Skip if no actor or action is selected
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        # Get the selected actor
        actor_idx: int = self.curr_actor_idx
        actor: Actor = self.actors[actor_idx]

        # Function to update the name of a given action
        def save_action_name(idx: int, name: str):
            actor.actions[idx].name = name
            self.unsaved_actor(actor_idx)
            self.set_actor(actor_idx)
            self.set_action(idx)

        # Create rename entry associated with name update function
        action_idx: int = self.curr_action_idx
        old_name: str = actor.actions[action_idx].name
        create_renaming_entry(listbox, actor_idx, old_name, save_action_name)

    def preview_action(self) -> None:
        """Shows a preview of the selected action in a popup."""
        # Skip if no actor or action is selected
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return
        # Get selected actor and action
        actor: Actor = self.actors[self.curr_actor_idx]
        action: Action = actor.actions[self.curr_action_idx]

        # Get frames info (dx, dy and sprites)
        frames: dict = get_action_frames(action=action, fps=60)
        # Get x and y coordinates
        x: npt.NDArray[np.int64] = frames["dx"].cumsum()
        y: npt.NDArray[np.int64] = frames["dy"].cumsum()

        # Compute size of the animation
        sprites_width: list[int] = [frame.size[0] for frame in frames["sprites"]]
        sprites_height: list[int] = [frame.size[1] for frame in frames["sprites"]]
        x_min, x_max = x.min(), x.max()
        y_min, y_max = y.min(), y.max()
        max_width, max_height = max(sprites_width), max(sprites_height)
        bg_w: int = x_max - x_min + max_width
        bg_h: int = y_max - y_min + max_height

        # Compute center image coords
        x0: int = max_width // 2 - x_min
        y0: int = max_height // 2 + y_max

        # Create a transparent background
        background: Image.Image = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))

        action_frames: list[Image.Image] = []
        for i in range(len(sprites_width)):
            action_frame: Image.Image = background.copy()
            sprite: Image.Image = frames["sprites"][i]
            sw, sh = sprite.size
            action_frame.paste(
                sprite, (x0 + x[i] - sw // 2, y0 - y[i] - sh // 2), mask=sprite,
            )
            action_frames.append(ImageTk.PhotoImage(action_frame))

        AnimationPopup(
            self,
            action_frames,
            60,
            f"{action.name} Action Preview",
        )

    def clean_component(self) -> None:
        """Resets displays and attributes present due to an action component being selected."""
        # Remove action component selection
        self.comp_listbox.select_clear()
        self.curr_comp_idx = None

    def set_component(self, component_idx: int) -> None:
        """
        Handles the selection of an action component in the list.

        Parameters
        ----------
        action_idx : int
            the index of the selected action component

        Returns
        -------
        None
        """
        # Skip if no actor or action selected
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        # Change component selection
        self.curr_comp_idx = component_idx
        self.comp_listbox.select(component_idx)

    def add_or_edit_component(self, new: bool) -> None:
        """
        Handles the popup to create or edit an action component.

        Parameters
        ----------
        new : bool
            whether the action component is created (True) or edited (False)

        Returns
        -------
        None
        """
        # Skip if no actor or action is selected
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        # Get selected actor and action
        actor_idx: int = self.curr_actor_idx
        actor: Actor = self.actors[actor_idx]
        action_idx: int = self.curr_action_idx
        action: Action = actor.actions[action_idx]

        # Get pre-existing component if edit and component index
        comp: ActionComponent | None = None
        idx: int = len(action.components)
        if not new:
            # Skip if editing and no component is selected
            if self.curr_comp_idx is None:
                return
            # Get correct component and index
            idx = self.curr_comp_idx
            comp = action.components[idx]

        # Function to create component popup
        def get_popup_content(popup) -> tuple[dict, list[str]]:
            entries: dict = {
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

        # Function to save the component
        def save_component(entries) -> bool:
            # Get all user inputs
            sprite: Image.Image = entries["sprite"].get()
            duration: float = entries["duration"].get()
            x_off: int = entries["x_offset"].get()
            y_off: int = entries["y_offset"].get()

            # Do not save if an input is malformed
            if sprite is None or duration is None or x_off is None or y_off is None:
                return False

            # Create the new action component from user input
            new_comp: ActionComponent = ActionComponent(
                sprite=sprite,
                duration_sec=duration,
                x_offset=x_off,
                y_offset=y_off,
            )
            # Place the component accordingly
            if new:
                action.components.append(new_comp)
            else:
                action.components[idx] = new_comp

            # Change actor save status and display
            self.unsaved_actor(actor_idx)
            self.set_action(action_idx)
            self.set_component(idx)
            return True

        # Create the component popup
        create_add_edit_popup(self, "Action Component", new, get_popup_content, save_component)

    def delete_component(self) -> None:
        """Removes the selected action component from the component list."""
        # Skip if no actor, action or action component is selected
        if self.curr_actor_idx is None or self.curr_action_idx is None or self.curr_comp_idx is None:
            return

        # Remove selected component from action
        actor_idx: int = self.curr_actor_idx
        actor: Actor = self.actors[actor_idx]
        action_idx: int = self.curr_action_idx
        action: Action = actor.actions[action_idx]
        action.components.pop(self.curr_comp_idx)

        # Change actor save status and clean display
        self.clean_component()
        self.unsaved_actor(actor_idx)
        self.set_action(action_idx)

    def select_component(self, event, treeview) -> None:
        """
        Handles the selection of an action component in a treeview.

        Parameters
        ----------
        event : tk.Event
            the selection event
        treeview : ttk.Treeview
            the treeview the selection happened in

        Returns
        -------
        None
        """
        # Skip if no actor or action selected
        if self.curr_actor_idx is None or self.curr_action_idx is None:
            return

        # Update display only on index change
        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_comp_idx:
                self.set_component(idx)

    def save_actor_as(self) -> None:
        """Get a filepath to save an actor in."""
        # Skip if no actor selected
        if self.curr_actor_idx is None:
            return

        # Get selected actor
        idx: int = self.curr_actor_idx
        actor: Actor = self.actors[idx]
        # Get path to save the actor file
        path: str | None = get_json_save_filepath(actor)
        if not path:
            return

        # Reference new file path in actor save status
        self.actors_save_status[idx] = (self.actors_save_status[idx][0], path)
        # Save the actor
        self.save_actor()

    def save_actor(self) -> None:
        """Saves the selected actor as a json file."""
        # Skip if no actor is selected
        if self.curr_actor_idx is None:
            return

        # Get path to save file, ask for it if none
        idx: int = self.curr_actor_idx
        path: str | None = self.actors_save_status[idx][1]
        if path is None:
            self.save_actor_as()
            return

        # Get actor data as dict
        actor: Actor = self.actors[idx]
        actor_dict: dict = actor.to_dict()

        # Save the actor as a json file
        with open(path, "w") as f:
            json.dump(actor_dict, f, indent=2)

        # Update actor save status and display
        self.actors_save_status[idx] = (True, path)
        self.set_actor_list()
        self.set_actor(idx)

    def init_scene_tab(self) -> None:
        """Sets up all widgets and events for the Scenes tab."""
        # Left: scene list
        def display_scene(scene: Scene):
            idx: int = self.scenes.index(scene)
            name: str = scene.name
            if not self.scenes_save_status[idx][0]:
                name = "*" + name
            return name

        self.scene_listbox: EditableListFrame = EditableListFrame(
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
        scene_detail_frame: tk.Frame = tk.Frame(self.scene_frame)
        scene_detail_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Top right: name display, save buttons and scene length setting
        scene_name_frame: tk.Frame = tk.Frame(scene_detail_frame)
        scene_name_frame.pack(side="top", fill="x")

        # Name display, save, preview and extract buttons
        name_save_frame: tk.Frame = tk.Frame(scene_name_frame)
        name_save_frame.pack(side="top", fill="x")
        self.scene_name_label: tk.Label = tk.Label(name_save_frame, text="")
        self.scene_name_label.pack(side="left", fill="x")
        tk.Button(name_save_frame, text="Preview", command=self.preview_scene).pack(side="right", padx=2)
        tk.Button(name_save_frame, text="Export", command=self.export_scene).pack(side="right", padx=2)
        tk.Button(name_save_frame, text="Save As", command=self.save_scene_as).pack(side="right", padx=2)
        tk.Button(name_save_frame, text="Save", command=self.save_scene).pack(side="right", padx=2)

        # Entries to edit global scene data (length)
        self.scene_setting_frame: tk.Frame = tk.Frame(scene_name_frame)
        self.scene_len_entry: FloatEntryFrame = FloatEntryFrame(
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
        self.scene_notebook: ttk.Notebook = ttk.Notebook(scene_detail_frame)

        # Scene appearance
        appearance_frame: tk.Frame = tk.Frame(self.scene_notebook)
        self.scene_notebook.add(appearance_frame, text="Appearance")

        # Background
        background_frame: tk.Frame = tk.Frame(appearance_frame)
        background_frame.pack(side="top", fill="x")
        tk.Button(background_frame, text="Set Background", command=self.set_background).pack(side="top", pady=2)
        self.background_image: ImageFrame = ImageFrame(background_frame, 200)
        self.background_image.pack(side="top", fill="both")

        # Camera details
        camera_frame: tk.Frame = tk.Frame(appearance_frame)
        camera_frame.pack(side="bottom", fill="both", expand=True, pady=5)

        # Global camera data
        global_cam_frame: tk.Frame = tk.Frame(camera_frame)
        global_cam_frame.pack(side="left", fill="both", expand=True)
        self.cam_width_entry: IntEntryFrame = IntEntryFrame(global_cam_frame, "Camera Width")
        self.cam_width_entry.pack(side="top", fill="x", pady=2)
        self.cam_height_entry: IntEntryFrame = IntEntryFrame(global_cam_frame, "Camera Height")
        self.cam_height_entry.pack(side="top", fill="x", pady=2)
        self.cam_start_x_entry: IntEntryFrame = IntEntryFrame(global_cam_frame, "Camera Start X")
        self.cam_start_x_entry.pack(side="top", fill="x", pady=2)
        self.cam_start_y_entry: IntEntryFrame = IntEntryFrame(global_cam_frame, "Camera Start Y")
        self.cam_start_y_entry.pack(side="top", fill="x", pady=2)
        tk.Button(global_cam_frame, text="Update Camera", command=self.update_cam_settings).pack(side="bottom")

        # Camera moves
        def display_cam_moves(cam_move: CameraMove) -> list[str | None]:
            return [
                None,
                cam_move.linked_sa.actor.name if cam_move.linked_sa else f"({cam_move.x},{cam_move.y})",
                str(cam_move.duration_sec),
            ]

        self.cam_listbox: EditableTreeFrame = EditableTreeFrame(
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
        scene_actor_frame: tk.Frame = tk.Frame(self.scene_notebook)
        self.scene_notebook.add(scene_actor_frame, text="Actors")

        # Scene actor list
        def display_scene_actor(sa: SceneActor) -> list[None| str]:
            return [None, sa.actor.name, f"({sa.start_x},{sa.start_y})"]

        self.sa_listbox: EditableTreeFrame = EditableTreeFrame(
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

        self.sched_listbox: EditableTreeFrame = EditableTreeFrame(
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

    def setup_scene_tab(self) -> None:
        """Updates all displays in the Scenes tab."""
        # Get all selected scene indexes
        scene_idx: int = self.curr_scene_idx
        cam_idx: int = self.curr_cam_move_idx
        sa_idx: int = self.curr_sa_idx
        sched_idx: int = self.curr_sched_idx

        # Reselect all scene indexes
        self.set_scene_list()
        if scene_idx is not None:
            self.set_scene(scene_idx)
        if cam_idx is not None:
            self.set_cam_move(cam_idx)
        if sa_idx is not None:
            self.set_scene_actor(sa_idx)
        if sched_idx is not None:
            self.set_scheduled_action(sched_idx)

    def unsaved_scene(self, idx: int) -> None:
        """
        Puts the save status of a given scene to False and reactualizes scene list.

        Parameters
        ----------
        idx : int
            the index of the scene to set as unsaved

        Returns
        -------
        None
        """
        self.scenes_save_status[idx] = (False, self.scenes_save_status[idx][1])
        self.set_scene_list()

    def set_scene_list(self) -> None:
        """Reactualizes the scene list."""
        self.scene_listbox.set(self.scenes)

    def clean_scene(self) -> None:
        """Resets displays and attributes present due to a scene being selected."""
        # Clean dependant displays
        self.clean_cam_move()
        self.clean_scene_actor()
        # Unselect in scene listbox
        self.curr_scene_idx = None
        self.scene_listbox.select_clear()
        self.scene_notebook.pack_forget()
        # Reset displays directly connected to scenes
        self.scene_setting_frame.pack_forget()
        self.scene_name_label["text"] = ""
        self.sa_listbox.clean()

    def set_scene(self, scene_idx: int) -> None:
        """
        Handles the selection of a scene in the list.

        Parameters
        ----------
        scene_idx : int
            the index of the selected scene

        Returns
        -------
        None
        """
        # Clean dependant displays only on index change
        if self.curr_scene_idx != scene_idx:
            self.clean_action()
            self.clean_cam_move()

        # Repack unpacked frames is no scene previously selected
        if self.curr_scene_idx is None:
            self.scene_setting_frame.pack(side="top", fill="x")
            self.scene_notebook.pack(side="top", fill="both", expand=True)

        # Change selected index
        self.curr_scene_idx = scene_idx
        scene: Scene = self.scenes[scene_idx]

        # Update global scene data displays
        self.scene_len_entry.set(scene.duration_sec)
        self.scene_name_label["text"] = scene.name
        if scene.background is None:
            self.background_image.clean()
        else:
            self.background_image.set(scene.background)
        # Update available scene actors
        self.sa_listbox.set(scene.actors)

        # Update displays for camera
        cam: Camera = scene.camera
        self.cam_width_entry.set(cam.width)
        self.cam_height_entry.set(cam.height)
        self.cam_start_x_entry.set(cam.start_x)
        self.cam_start_y_entry.set(cam.start_y)
        self.cam_listbox.set(cam.moves)

        # Change selected scene in listbox
        self.scene_listbox.select(scene_idx)

    def add_scene(self) -> None:
        """Creates a new scene in the scene list."""
        # Find an unused scene name
        scene_names: list[str] = [scene.name for scene in self.scenes]
        i: int = 1
        while f"Scene {i}" in scene_names:
            i += 1
        # Create and add scene to list
        scene: Scene = Scene(name=f"Scene {i}")
        self.scenes.append(scene)
        self.scenes_save_status.append((False, None))

        # Change displays accordingly
        self.set_scene_list()
        self.set_scene(len(self.scenes) - 1)

    def open_scene(self) -> None:
        """Asks user for a scene file to open in the scene list."""
        # Ask for and open a json file
        file_res: tuple[str, dict] | None = open_json_file()
        if file_res is None:
            return
        path, data = file_res

        # Create a scene from saved data
        scene: Scene = Scene.from_dict(data)

        # Add the scene to the list
        self.scenes.append(scene)
        self.scenes_save_status.append((True, path))

        # Update displays
        self.set_scene_list()
        self.set_scene(len(self.scenes) - 1)

    def delete_scene(self) -> None:
        """Removes the selected scene from the scene list."""
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return
        idx: int = self.curr_scene_idx

        if not self.scenes_save_status[idx][0]:
            answer: bool = messagebox.askokcancel(
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

    def select_scene(self, event, listbox) -> None:
        """
        Handles the selection of a scene in a listbox.

        Parameters
        ----------
        event : tk.Event
            the selection event
        listbox : tk.Listbox
            the listbox the selection happened in

        Returns
        -------
        None
        """
        idx: tuple = listbox.curselection()
        # Only change selection if the index is different
        if idx and idx[0] != self.curr_scene_idx:
            self.set_scene(idx[0])

    def rename_scene(self, event, listbox) -> None:
        """
        Creates a tkinter entry to rename the selected scene.

        Parameters
        ----------
        event : tk.Event
            the double click event
        listbox : tk.Listbox
            the listbox the double click happened in

        Returns
        -------
        None
        """
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return

        # Function to save the new scene name
        def save_scene_name(idx: int, name: str) -> None:
            self.scenes[idx].name = name
            self.unsaved_scene(idx)
            self.set_scene(idx)

        # Create the renaming entry
        scene_idx: int = self.curr_scene_idx
        old_name: str = self.scenes[scene_idx].name
        create_renaming_entry(listbox, scene_idx, old_name, save_scene_name)

    def get_scene_frames(self) -> list[npt.NDArray[np.int64]] | None:
        """
        Creates and gives the frames used in a scene as numpy arrays.

        Parameters
        ----------
        None

        Returns
        -------
        list[npt.NDArray[np.int64]] | None
            the list of frames as arrays if a scene with a background was selected
        """
        # Skip if no scene was selected
        if self.curr_scene_idx is None:
            return None
        # Get selected scene
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]

        # Give warning and skip if scene has no background
        if scene.background is None:
            messagebox.showinfo(
                "No background",
                "A background is needed to preview a scene."
            )
            return None

        # Get scene fps and number of frames
        fps: int = 60
        n_frames: int = int(scene.duration_sec * fps)

        # Get frames info for every scene actor
        actor_frames: dict[str, dict] = {}
        for sa in scene.actors:
            sa_frames: dict = get_scene_actor_frames(sa, n_frames, fps)
            actor_frames[str(sa)] = sa_frames

        # Get camera coordinates
        cam_pos: dict = get_camera_pos(scene.camera, actor_frames, n_frames, fps)
        # Get complete scene frames
        scene_frames: list[npt.NDArray[np.int64]] = compose_frames(
            scene.background, actor_frames, cam_pos, scene.actors, scene.camera, n_frames
        )
        return scene_frames

    def preview_scene(self) -> None:
        """Shows a preview of the selected scene in a popup."""
        # Get all scene frames
        frames_arr: list[npt.NDArray[np.int64]] | None = self.get_scene_frames()
        # Skip if no frames were given
        if frames_arr is None:
            return
        # Get the selected scene
        scene: Scene = self.scenes[self.curr_scene_idx]
        # Reformat the frames as tkinter images
        frames: list[ImageTk.PhotoImage] = [
            ImageTk.PhotoImage(
                Image.fromarray(frame, mode="RGBA")
            )
            for frame in frames_arr
        ]

        # Create and start the preview popup
        AnimationPopup(
            self,
            frames,
            60,
            f"{scene.name} Action Preview",
        )

    def export_scene(self) -> None:
        """Exports a scene as a mp4 video."""
        # Get the scene frames
        frames_arr: list[npt.NDArray[np.int64]] | None = self.get_scene_frames()
        # Skip if no frames were given
        if frames_arr is None:
            return
        # Get selected scene
        scene: Scene = self.scenes[self.curr_scene_idx]

        # Ask user where to save the exported video
        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Files", "*.mp4")],
            initialfile=scene.name.replace(' ', '_').lower()
        )
        # Cancel export if no path is given
        if not path:
            return
        # Create and save the video
        make_video_from_frames(frames_arr, 60, path)
        # Show a confirmation message for the export
        messagebox.showinfo(message="File saved!")

    def update_scene(self) -> None:
        """Updates global scene parameters."""
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return
        # Get the selected scene
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]

        # Get scene duration user input
        scene_len = self.scene_len_entry.get()
        # Skip if input is malformed
        if scene_len is None:
            return
        # Update scene and display
        scene.duration_sec = scene_len
        self.unsaved_scene(scene_idx)

    def set_background(self) -> None:
        """Changes the background used in the selected scene."""
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return

        # Get selected scene
        idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[idx]

        # Ask user for a new image
        img: Image.Image | None = open_image_file()
        if img is None:
            return

        # Update scene and displays with new background
        scene.background = img
        self.background_image.set(img)
        self.unsaved_scene(idx)

    def update_cam_settings(self) -> None:
        """Updates global camera settings"""
        # Skip if no selected scene
        if self.curr_scene_idx is None:
            return

        # Get selected scene and its camera
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        cam: Camera = scene.camera

        # Get all user inputs
        width: int | None = self.cam_width_entry.get()
        height: int | None = self.cam_height_entry.get()
        start_x: int | None = self.cam_start_x_entry.get()
        start_y: int | None = self.cam_start_y_entry.get()

        # Skip update if an input is malformed
        if width is None or height is None or start_x is None or start_y is None:
            return

        # Update scene and displays
        cam.width = width
        cam.height = height
        cam.start_x = start_x
        cam.start_y = start_y
        self.unsaved_scene(scene_idx)

    def clean_cam_move(self) -> None:
        """Resets displays and attributes present due to a camera movement being selected."""
        self.curr_cam_move_idx = None
        self.cam_listbox.select_clear()

    def set_cam_move(self, move_idx: int) -> None:
        """
        Handles the selection of a camera movement in the list.

        Parameters
        ----------
        move_idx : int
            the index of the selected camera movement

        Returns
        -------
        None
        """
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return
        self.curr_cam_move_idx = move_idx
        self.cam_listbox.select(move_idx)

    def add_or_edit_camera_move(self, new: bool) -> None:
        """
        Handles the popup to create or edit a camera movement.

        Parameters
        ----------
        new : bool
            whether the camera movement is created (True) or edited (False)

        Returns
        -------
        None
        """
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return
        # Get selected scene and its camera
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        cam: Camera = scene.camera

        # Get pre-existing cam movement if edit and its index
        cam_move: CameraMove | None = None
        idx: int = len(cam.moves)
        if not new:
            # Skip if editing and no component is selected
            if self.curr_cam_move_idx is None:
                return
            # Get correct component and index
            idx = self.curr_cam_move_idx
            cam_move = cam.moves[idx]

        # Get names of all actors in the scene
        actor_names = [sa.actor.name for sa in scene.actors]

        # Function to create cam movement popup
        def get_popup_content(popup) -> tuple[dict, list[str]]:
            toggle: ToggleFrame = ToggleFrame(
                parent=popup,
                toggle_label="Is linked",
                toggle_default=(cam_move.linked_sa is not None) if cam_move else False,
            )
            false_frame: tk.Frame = toggle.frame_false
            true_frame: tk.Frame = toggle.frame_true

            entries: dict = {
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

        # Function to save the cam movement
        def save_cam_move(entries) -> bool:
            # Get user input, skip if malformed
            duration: int | None = entries["duration"].get()
            if duration is None:
                return False

            if entries["toggle"].get():
                # Get user input, skip if none
                actor_name: str | None = entries["linked_actor"].get()
                if actor_name is None:
                    return False
                # Create camera movement linked to the selected scene actor
                actor_idx: int = actor_names.index(actor_name)
                actor: SceneActor = scene.actors[actor_idx]
                new_cam_move: CameraMove = CameraMove(linked_sa=actor, duration_sec=duration)
            else:
                # Get user inputs, skip if malformed
                x: int | None = entries["x_coord"].get()
                y: int | None = entries["y_coord"].get()
                if x is None or y is None:
                    return False
                # Create a new camera movement
                new_cam_move: CameraMove = CameraMove(x=x, y=y, duration_sec=duration)

            # Place the camera move accordingly
            if new:
                cam.moves.append(new_cam_move)
            else:
                cam.moves[idx] = new_cam_move

            # Update displays and scene save status
            self.unsaved_scene(scene_idx)
            self.set_scene(scene_idx)
            self.set_cam_move(idx)
            return True

        # Create the cam movement popup
        create_add_edit_popup(self, "Camera Movement", new, get_popup_content, save_cam_move)

    def delete_camera_move(self) -> None:
        """Removes the selected camera movement from the list."""
        # Skip if no scene or camera movement selected
        if self.curr_scene_idx is None or self.curr_cam_move_idx is None:
            return

        # Get selected scene and camera
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        cam: Camera = scene.camera
        # Remove the selected camera movement
        cam.moves.pop(self.curr_cam_move_idx)
        # Update displays
        self.clean_cam_move()
        self.unsaved_scene(scene_idx)
        self.set_scene(scene_idx)

    def select_camera_move(self, event, treeview) -> None:
        """
        Handles the selection of a camera movement in a treeview.

        Parameters
        ----------
        event : tk.Event
            the selection event
        treeview : ttk.Treeview
            the treeview the selection happened in

        Returns
        -------
        None
        """
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return

        # Update display only on index change
        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_cam_move_idx:
                self.set_cam_move(idx)

    def clean_scene_actor(self) -> None:
        """Resets displays and attributes present due to a scene actor being selected."""
        # Clean displays associated with the scene actor
        self.clean_scheduled_action()
        self.curr_sa_idx = None
        self.sched_listbox.clean()
        self.sa_listbox.select_clear()

    def set_scene_actor(self, sa_idx: int, clean: bool = True) -> None:
        """
        Handles the selection of a scene actor in the list.

        Parameters
        ----------
        sa_idx : int
            the index of the selected scene actor
        clean : bool
            whether to reset displays associated with the scene actor on index change

        Returns
        -------
        None
        """
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return
        # Reset displays dependant on scene actor only on index change if authorized
        if self.curr_sa_idx != sa_idx and clean:
            self.clean_scheduled_action()

        # Change selection index and update displays
        self.curr_sa_idx = sa_idx
        sa: SceneActor = self.scenes[self.curr_scene_idx].actors[sa_idx]
        self.sched_listbox.set(sa.scheduled_actions)
        self.sa_listbox.select(sa_idx)

    def add_scene_actor(self) -> None:
        """Generates a popup to create a new scene actor for a scene."""
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return
        # Get the selected scene
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]

        # Send a warning and cancel if no actors are accessible
        if len(self.actors) == 0:
            messagebox.showinfo(
                "No actors",
                "There are no actors defined. Please create at least one actor first."
            )
            return

        # Get all actor names
        actor_names: list[str] = [actor.name for actor in self.actors]

        # Create the popup
        popup: tk.Toplevel = tk.Toplevel(self)
        popup.title("Add Actor to Scene")

        # Create the entries in the popup
        actor_entry: DropdownEntry = DropdownEntry(
            popup, "Actor", actor_names,
        )
        actor_entry.pack(side="top", fill="x", pady=1)
        start_x_entry: IntEntryFrame = IntEntryFrame(popup, "Start X Coord")
        start_x_entry.pack(side="top", pady=1)
        start_y_entry: IntEntryFrame = IntEntryFrame(popup, "Start Y Coord")
        start_y_entry.pack(side="top", pady=1)

        # Function to create the scene actor from user inputs
        def add_and_close():
            # Get user inputs
            actor_name, start_x, start_y = actor_entry.get(), start_x_entry.get(), start_y_entry.get()
            # Cancel if one input is malformed
            if actor_name is None or start_x is None or start_y is None:
                return
            # Create and add the scene actor
            actor_idx: int = actor_names.index(actor_name)
            sa = SceneActor(actor=self.actors[actor_idx], start_x=start_x, start_y=start_y)
            scene.actors.append(sa)
            # Update display
            self.unsaved_scene(scene_idx)
            self.set_scene(scene_idx)
            self.set_scene_actor(len(scene.actors) - 1)
            # Remove popup
            popup.destroy()

        # Create a save button in the popup
        tk.Button(popup, text="Add", command=add_and_close).pack(side="bottom", pady=10)

    def edit_scene_actor(self) -> None:
        """Generates a popup to edit a scene actor for a scene."""
        # Skip if no scene or scene actor is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        # Get selected scene and scene actor
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        sa_idx: int = self.curr_sa_idx
        sa: SceneActor = scene.actors[sa_idx]

        # Create the popup
        popup: tk.Toplevel = tk.Toplevel(self)
        popup.title("Edit Actor")

        # Create the entries in the popup
        start_x_entry: IntEntryFrame = IntEntryFrame(popup, "Start X Coord", sa.start_x)
        start_x_entry.pack(side="top", fill="x", pady=1)
        start_y_entry: IntEntryFrame = IntEntryFrame(popup, "Start Y Coord", sa.start_y)
        start_y_entry.pack(side="top", fill="x", pady=1)

        # Function to update the scene actor from user inputs
        def edit_and_close():
            # Get user inputs
            start_x, start_y = start_x_entry.get(), start_y_entry.get()
            # Cancel edit if an input is malformed
            if start_x is None or start_y is None:
                return
            # Update the scene actor
            sa.start_x = start_x
            sa.start_y = start_y
            # Update the displays
            self.unsaved_scene(scene_idx)
            self.set_scene(scene_idx)
            self.set_scene_actor(sa_idx)
            # Destroy the popup
            popup.destroy()

        # Create a save button in the popup
        tk.Button(popup, text="Edit", command=edit_and_close).pack(side="bottom", pady=10)

    def delete_scene_actor(self) -> None:
        """Deletes the selected scene actor from the scene's actor list."""
        # Skip if no scene or scene actor is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        # Get the selected scene
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        sa_idx: int = self.curr_sa_idx

        # Remove the actor from the list
        scene.actors.pop(sa_idx)
        # Reset displays
        self.clean_scene_actor()
        self.unsaved_scene(scene_idx)
        self.set_scene(scene_idx)

    def select_scene_actor(self, event, treeview) -> None:
        """
        Handles the selection of a scene actor in a treeview.

        Parameters
        ----------
        event : tk.Event
            the selection event
        treeview : ttk.Treeview
            the treeview the selection happened in

        Returns
        -------
        None
        """
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return

        # Update display only on index change
        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_sa_idx:
                self.set_scene_actor(idx)

    def move_scene_actor(self, delta: int) -> None:
        """
        Moves the selected scene actor in the list.

        Parameters
        ----------
        delta : int
            the number of indexes to move the actor in

        Returns
        -------
        None
        """
        # Skip if no scene or scene actor is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        # Get the selected scene and scene actor index
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        sa_idx: int = self.curr_sa_idx

        # Get the new index of the scene actor
        n_idx = max(0, min(sa_idx + delta, len(scene.actors) - 1))
        # Skip if index didn't change
        if n_idx == sa_idx:
            return
        # Move the actor in the list
        actor = scene.actors.pop(sa_idx)
        scene.actors.insert(n_idx, actor)
        # Update displays
        self.unsaved_scene(scene_idx)
        self.set_scene(scene_idx)
        self.set_scene_actor(n_idx, clean=False)

    def clean_scheduled_action(self) -> None:
        """Resets displays and attributes present due to a scheduled action being selected."""
        self.sched_listbox.select_clear()
        self.curr_sched_idx = None

    def set_scheduled_action(self, sched_idx: int) -> None:
        """
        Handles the selection of a scheduled action in the list.

        Parameters
        ----------
        sa_idx : int
            the index of the selected scheduled action

        Returns
        -------
        None
        """
        # Skip if no scene or scene actor is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        # Update index and displays
        self.curr_sched_idx = sched_idx
        self.sched_listbox.select(sched_idx)

    def add_or_edit_scheduled_action(self, new: bool) -> None:
        """
        Handles the popup to create or edit an scheduled action.

        Parameters
        ----------
        new : bool
            whether the scheduled action is created (True) or edited (False)

        Returns
        -------
        None
        """
        # Skip if no scene or scene actor is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return
        # Get the selected scene and scene actor
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        sa_idx: int = self.curr_sa_idx
        sa: SceneActor = scene.actors[sa_idx]

        # Get pre-existing scheduled action if edit and its index
        sched: ScheduledAction | None = None
        idx : int = len(sa.scheduled_actions)
        if not new:
            # Skip if editing and no scheduled action is selected
            if self.curr_sched_idx is None:
                return
            # Get correct scheduled action and index
            idx = self.curr_sched_idx
            sched = sa.scheduled_actions[idx]

        # Get the names of the available actions
        action_names: list[str] = [action.name for action in sa.actor.actions]

        # Function to create scheduled action popup
        def get_popup_content(popup) -> tuple[dict, list[str]]:
            toggle: ToggleFrame = ToggleFrame(
                parent=popup,
                toggle_label="Is Idle",
                toggle_default=sched.action.name == "Idle" if sched else False,
            )
            false_frame: tk.Frame = toggle.frame_false
            true_frame: tk.Frame = toggle.frame_true
            is_visible_var: tk.BooleanVar = tk.BooleanVar(value=sched.is_visible if sched else True)

            entries: dict = {
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

        # Function to save the scheduled action
        def save_sched(entries) -> bool:
            # Get global user inputs
            duration: float | None = entries["duration"].get()
            start_offset: float | None = entries["start_offset"].get()
            is_visible: bool | None = entries["is_visible"].get()
            # Cancel if user inputs are malformed
            if duration is None or start_offset is None or is_visible is None:
                return False

            # Get user inputs with toggle
            if entries["toggle"].get():
                # Get user input
                idle_sprite: Image.Image | None = entries["idle_sprite"].get()
                # Cancel if input is malformed
                if idle_sprite is None:
                    return False
                # Create the new action
                action: Action = Action("Idle", components=[ActionComponent(idle_sprite, 1.0, 0, 0)])
            else:
                # Get user input
                action_name: str | None = entries["action_name"].get()
                # Cancel if user input is malformed
                if action_name is None:
                    return False
                action_idx: int = action_names.index(action_name)
                action: Action = sa.actor.actions[action_idx]

            # Create the new scheduled action
            new_sched: ScheduledAction = ScheduledAction(
                action=action,
                duration_sec=duration,
                start_offset_sec=start_offset,
                is_visible=is_visible,
            )

            # Place the scheduled action accordingly
            if new:
                sa.scheduled_actions.append(new_sched)
            else:
                sa.scheduled_actions[idx] = new_sched
            # Update displays
            self.unsaved_scene(scene_idx)
            self.set_scene_actor(sa_idx)
            self.set_scheduled_action(idx)
            return True

        # Create the scheduled action popup
        create_add_edit_popup(self, "Scheduled Action", new, get_popup_content, save_sched)

    def delete_scheduled_action(self) -> None:
        """Deletes the selected scheduled action from the scene actor's action list."""
        # Skip if no scene, scene actor or scheduled action is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None or self.curr_sched_idx is None:
            return
        # Get selected scene, scene actor and scheduled action index
        scene_idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[scene_idx]
        sa_idx: int = self.curr_sa_idx
        sa: SceneActor = scene.actors[sa_idx]
        sched_idx: int = self.curr_sched_idx

        # Remove action from the list
        sa.scheduled_actions.pop(sched_idx)
        # Update displays
        self.clean_scheduled_action()
        self.unsaved_scene(scene_idx)
        self.set_scene_actor(sa_idx)

    def select_scheduled_action(self, event, treeview) -> None:
        """
        Handles the selection of a scheduled action in a treeview.

        Parameters
        ----------
        event : tk.Event
            the selection event
        treeview : ttk.Treeview
            the treeview the selection happened in

        Returns
        -------
        None
        """
        # Skip if no scene or scene actor is selected
        if self.curr_scene_idx is None or self.curr_sa_idx is None:
            return

        # Update display only on index change
        if treeview.selection():
            idx = int(treeview.selection()[0])
            if idx != self.curr_sched_idx:
                self.set_scheduled_action(idx)

    def save_scene_as(self) -> None:
        """Get a filepath to save a scene in."""
        if self.curr_scene_idx is None:
            return

        # Skip if no scene is selected
        idx: int = self.curr_scene_idx
        scene: Scene = self.scenes[idx]

        # Get path to save the actor file
        path: str | None = get_json_save_filepath(scene)
        if not path:
            return
        # Reference new file path in actor save status
        self.scenes_save_status[idx] = (self.scenes_save_status[idx][0], path)
        # Save the scene
        self.save_scene()

    def save_scene(self) -> None:
        """Saves the selected scene as a json file."""
        # Skip if no scene is selected
        if self.curr_scene_idx is None:
            return

        # Get path to save file, ask for it if none
        idx: int = self.curr_scene_idx
        path: str | None = self.scenes_save_status[idx][1]
        if path is None:
            self.save_scene_as()
            return

        # Get scene data as dict
        scene: Scene = self.scenes[idx]
        scene_dict: dict = scene.to_dict()

        # Save the scene as a json file
        with open(path, "w") as f:
            json.dump(scene_dict, f, indent=2)

        # Update scene save status and display
        self.scenes_save_status[idx] = (True, path)
        self.set_scene_list()

    def window_close(self) -> None:
        """Closes the app window with a confirmation popup if unsaved changes are detected."""
        # Check whether some actors have unsaved changes
        unsaved_actors = False
        for status in self.actors_save_status:
            if not status[0]:
                unsaved_actors = True
                break

        # Check whether some scenes have unsaved changes
        unsaved_scenes = False
        for status in self.scenes_save_status:
            if not status[0]:
                unsaved_scenes = True
                break

        # Close window if no unsaved changes were found
        if not unsaved_actors and not unsaved_scenes:
            self.quit()
            return

        # Create the warning message
        unsaved_kind = ""
        if unsaved_actors:
            unsaved_kind += "actors"
            if unsaved_scenes:
                unsaved_kind += " and "
        if unsaved_scenes:
            unsaved_kind += "scenes"
        message = f"There are unsaved {unsaved_kind}. Close the window anyway?"

        # Ask for user confirmation
        answer = messagebox.askokcancel(
            title="Confirmation",
            message=message,
            icon=messagebox.WARNING,
        )

        # Close the window if action confirmed by user
        if answer:
            self.quit()