import base64
import io
from dataclasses import dataclass, field
from PIL import Image
from typing import Optional

from src.data_models.actor import Action, Actor


@dataclass
class ScheduledAction:
    action: Action
    duration_sec: float
    start_offset_sec: float = 0.0
    is_visible: bool = True

    def to_dict(self) -> dict:
        return {
            "action": self.action.to_dict(),
            "duration_sec": self.duration_sec,
            "start_offset_sec": self.start_offset_sec,
            "is_visible": self.is_visible,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "ScheduledAction":
        return ScheduledAction(
            action=Action.from_dict(d["action"]),
            duration_sec=d["duration_sec"],
            start_offset_sec=d.get("start_offset_sec", 0.0),
            is_visible=d.get("is_visible", True),
        )


@dataclass
class SceneActor:
    actor: Actor
    start_x: int
    start_y: int
    scheduled_actions: list[ScheduledAction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "actor": self.actor.to_dict(),
            "start_x": self.start_x,
            "start_y": self.start_y,
            "scheduled_actions": [sched.to_dict() for sched in self.scheduled_actions],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "SceneActor":
        return SceneActor(
            actor=Actor.from_dict(d["actor"]),
            start_x=d["start_x"],
            start_y=d["start_y"],
            scheduled_actions=[
                ScheduledAction.from_dict(sched)
                for sched in d.get("scheduled_actions", [])
            ],
        )


@dataclass
class CameraMove:
    x: int = 0
    y: int = 0
    linked_sa: Optional[SceneActor] = None
    duration_sec: float = 1.0

    def to_dict(self) -> str:
        return {
            "x": self.x,
            "y": self.y,
            "linked_sa": self.linked_sa.to_dict() if self.linked_sa else None,
            "duration_sec": self.duration_sec,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "CameraMove":
        dict_sa = d.get("linked_sa", None)
        return CameraMove(
            x=d.get("x", 0),
            y=d.get("y", 0),
            linked_sa=SceneActor.from_dict(dict_sa) if dict_sa else None,
            duration_sec=d.get("duration_sec", 1.0),
        )


@dataclass
class Camera:
    width: int = 816
    height: int = 624
    start_x: int = 0
    start_y: int = 0
    moves: list[CameraMove] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "start_x": self.start_x,
            "start_y": self.start_y,
            "moves": [move.to_dict() for move in self.moves],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Camera":
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
    name: str
    background: Optional[Image] = None
    duration_sec: float = 5.0
    actors: list[SceneActor] = field(default_factory=list)
    camera: Camera = field(default_factory=Camera)

    def to_dict(self) -> dict:
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

        actors_str = [str(actor.to_dict()) for actor in scene.actors]

        for i in range(len(scene.camera.moves)):
            if scene.camera.moves[i].linked_sa is None:
                continue
            linked_sa_str = str(scene.camera.moves[i].linked_sa.to_dict())
            if linked_sa_str in actors_str:
                actor_idx = actors_str.index(linked_sa_str)
                scene.camera.moves[i].linked_sa = scene.actors[actor_idx]

        return scene