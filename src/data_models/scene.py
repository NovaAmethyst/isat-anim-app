"""
Defines classes used to represent scenes.

Classes
-------
Camera
CameraMove
Scene
SceneActor
ScheduledAction
"""

import base64
import io
from dataclasses import dataclass, field
from PIL import Image
from typing import Optional

from src.data_models.actor import Action, Actor


@dataclass
class ScheduledAction:
    """
    A class to represent a scheduled action.

    Attributes
    ----------
    action : Action
        the action which is scheduled
    duration_sec : float
        the time (in seconds) during which the scheduled action is executed
    start_offset_sec : float (default 0.0)
        the start time (in seconds) of the action animation
    is_visible : bool (default True)
        whether the action is visible in the animation

    Methods
    -------
    to_dict():
        Creates a dictionary representing the ScheduledAction object.

    Static Methods
    --------------
    from_dict(d):
        Creates a ScheduledAction object using the data stored in a dictionary.
    """
    action: Action
    duration_sec: float
    start_offset_sec: float = 0.0
    is_visible: bool = True

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the ScheduledAction object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the ScheduledAction object
        """
        return {
            "action": self.action.to_dict(),
            "duration_sec": self.duration_sec,
            "start_offset_sec": self.start_offset_sec,
            "is_visible": self.is_visible,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "ScheduledAction":
        """
        Creates a ScheduledAction object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the ScheduledAction object creation

        Returns
        -------
        ScheduledAction
            the ScheduledAction object corresponding to the given dictionary
        """
        return ScheduledAction(
            action=Action.from_dict(d["action"]),
            duration_sec=d["duration_sec"],
            start_offset_sec=d.get("start_offset_sec", 0.0),
            is_visible=d.get("is_visible", True),
        )


@dataclass
class SceneActor:
    """
    A class to represent an actor in a scene.

    Attributes
    ----------
    actor : Actor
        the actor represented in the scene
    start_x : int
        the starting coordinates of the actor on the x axis
    start_y : int
        the starting coordinates of the actor on the y axis
    scheduled_actions : list[ScheduledActions] (default [])
        the actions to be executed by the actor

    Methods
    -------
    replace_actor(new_actor) -> None:
        Replaces the current actor with an identical actor, and handles all scheduled actions switches.
    to_dict():
        Creates a dictionary representing the SceneActor object.

    Static Methods
    --------------
    from_dict(d):
        Creates a SceneActor object using the data stored in a dictionary.
    """
    actor: Actor
    start_x: int
    start_y: int
    scheduled_actions: list[ScheduledAction] = field(default_factory=list)

    def replace_actor(self, new_actor: Actor) -> None:
        """
        Replaces the current actor with an identical actor, and handles all scheduled actions switches.

        Parameters
        ----------
        new_actor : Actor
            the actor used as a replacement

        Returns
        -------
        None
        """
        if new_actor != self.actor:
            return
        self.actor = new_actor

        for sched in self.scheduled_actions:
            if sched.action in self.actor.actions:
                i: int = self.actor.actions.index(sched.action)
                sched.action = self.actor.actions[i]

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the SceneActor object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the SceneActor object
        """
        return {
            "actor": self.actor.to_dict(),
            "start_x": self.start_x,
            "start_y": self.start_y,
            "scheduled_actions": [sched.to_dict() for sched in self.scheduled_actions],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "SceneActor":
        """
        Creates a SceneActor object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the SceneActor object creation

        Returns
        -------
        SceneActor
            the SceneActor object corresponding to the given dictionary
        """
        sa: SceneActor = SceneActor(
            actor=Actor.from_dict(d["actor"]),
            start_x=d["start_x"],
            start_y=d["start_y"],
            scheduled_actions=[
                ScheduledAction.from_dict(sched)
                for sched in d.get("scheduled_actions", [])
            ],
        )
        sa.replace_actor(sa.actor)
        return sa


@dataclass
class CameraMove:
    """
    A class to represent a camera move during a scene.

    Attributes
    ----------
    x : int (default 0)
        the amount of pixels moved horizontally if no actor is linked
    y : int (default 0)
        the amount of pixels moved vertically if no actor is linked
    linked_sa : SceneActor | None (default None)
        the optional actor to follow
    duration_sec : float (default 1.0)
        the duration in seconds of the camera move

    Methods
    -------
    to_dict():
        Creates a dictionary representing the CameraMove object.

    Static Methods
    --------------
    from_dict(d):
        Creates a CameraMove object using the data stored in a dictionary.
    """
    x: int = 0
    y: int = 0
    linked_sa: Optional[SceneActor] = None
    duration_sec: float = 1.0

    def to_dict(self) -> str:
        """
        Creates a dictionary representing the CameraMove object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the CameraMove object
        """
        return {
            "x": self.x,
            "y": self.y,
            "linked_sa": self.linked_sa.to_dict() if self.linked_sa else None,
            "duration_sec": self.duration_sec,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "CameraMove":
        """
        Creates a CameraMove object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the CameraMove object creation

        Returns
        -------
        CameraMove
            the CameraMove object corresponding to the given dictionary
        """
        dict_sa = d.get("linked_sa", None)
        return CameraMove(
            x=d.get("x", 0),
            y=d.get("y", 0),
            linked_sa=SceneActor.from_dict(dict_sa) if dict_sa else None,
            duration_sec=d.get("duration_sec", 1.0),
        )


@dataclass
class Camera:
    """
    A class to represent the camera used in a scene.

    Attributes
    ----------
    width : int (default 816)
        the width of the camera in pixels
    height : int (default 624)
        the height of the camera in pixels
    start_x : int (default 0)
        the starting x coordinate of the center of the camera
    start_y : int (default 0)
        the starting y coordinate of the center of the camera
    moves : list[CameraMove] (default [])
        the list of moves done by the camera during a scene

    Methods
    -------
    to_dict():
        Creates a dictionary representing the Camera object.

    Static Methods
    --------------
    from_dict(d):
        Creates a Camera object using the data stored in a dictionary.
    """
    width: int = 816
    height: int = 624
    start_x: int = 0
    start_y: int = 0
    moves: list[CameraMove] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the Camera object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the Camera object
        """
        return {
            "width": self.width,
            "height": self.height,
            "start_x": self.start_x,
            "start_y": self.start_y,
            "moves": [move.to_dict() for move in self.moves],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Camera":
        """
        Creates a Camera object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the Camera object creation

        Returns
        -------
        Camera
            the Camera object corresponding to the given dictionary
        """
        return Camera(
            width=d.get("width", 816),
            height=d.get("height", 624),
            start_x=d.get("start_x", 0),
            start_y=d.get("start_y", 0),
            moves=[
                CameraMove.from_dict(move)
                for move in d.get("moves", [])
            ],
        )


@dataclass
class Scene:
    """
    A class to represent a scene.

    Attributes
    ----------
    name : str
        the name of the scene
    background : PIL.Image.Image | None (default None)
        the optional background used during the scene
    duration_sec : float (default 5.0)
        the duration of the scene in seconds
    actors : list[SceneActor] (default [])
        the actors used in the scene
    camera : Camera (default Camera())
        the camera used in the scene

    Methods
    -------
    to_dict():
        Creates a dictionary representing the Scene object.

    Static Methods
    --------------
    from_dict(d):
        Creates a Scene object using the data stored in a dictionary.
    """
    name: str
    background: Optional[Image.Image] = None
    duration_sec: float = 5.0
    actors: list[SceneActor] = field(default_factory=list)
    camera: Camera = field(default_factory=Camera)

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the Scene object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the Scene object
        """
        buffer = io.BytesIO()
        if self.background is not None:
            self.background.save(buffer, format="PNG")
        return {
            "name": self.name,
            "background": base64.b64encode(buffer.getvalue()).decode("utf-8") if self.background else None,
            "duration_sec": self.duration_sec,
            "actors": [sa.to_dict() for sa in self.actors],
            "camera": self.camera.to_dict(),
        }

    @staticmethod
    def from_dict(d: dict) -> "Scene":
        """
        Creates a Scene object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the Scene object creation

        Returns
        -------
        Scene
            the Scene object corresponding to the given dictionary
        """
        background_bytes = d.get("background", None)
        decoded_background = base64.b64decode(background_bytes) if background_bytes else None
        scene = Scene(
            name=d["name"],
            background=Image.open(io.BytesIO(decoded_background)) if decoded_background else None,
            duration_sec=d.get("duration_sec", 5.0),
            actors=[
                SceneActor.from_dict(sa)
                for sa in d.get("actors", [])
            ],
            camera=Camera.from_dict(d.get("camera", {})),
        )

        seen_actors: list[Actor] = []
        for i in range(len(scene.actors)):
            actor: Actor = scene.actors[i].actor
            if actor in seen_actors:
                continue
            for j in range(i + 1, len(scene.actors)):
                scene.actors[j].replace_actor(actor)

        # Replace camera moves linked to scene actors with instance refs instead of copies
        actors_str = [str(actor.to_dict()) for actor in scene.actors]

        for i in range(len(scene.camera.moves)):
            if scene.camera.moves[i].linked_sa is None:
                continue
            linked_sa_str = str(scene.camera.moves[i].linked_sa.to_dict())
            if linked_sa_str in actors_str:
                actor_idx = actors_str.index(linked_sa_str)
                scene.camera.moves[i].linked_sa = scene.actors[actor_idx]

        return scene