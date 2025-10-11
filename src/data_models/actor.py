import base64
import io
from dataclasses import dataclass, field
from PIL import Image


@dataclass
class ActionComponent:
    sprite: Image
    duration_sec: float
    x_offset: int
    y_offset: int

    def to_dict(self) -> dict:
        buffer = io.BytesIO()
        self.sprite.save(buffer, format="PNG")
        return {
            "sprite": base64.b64encode(buffer.getvalue()).decode("utf-8"),
            "duration_sec": self.duration_sec,
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "ActionComponent":
        sprite_data = base64.b64decode(d["sprite"])
        return ActionComponent(
            sprite=Image.open(io.BytesIO(sprite_data)),
            duration_sec=d["duration_sec"],
            x_offset=d["x_offset"],
            y_offset=d["y_offset"],
        )


@dataclass
class Action:
    name: str
    components: list[ActionComponent] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "components": [comp.to_dict() for comp in self.components],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Action":
        return Action(
            name=d["name"],
            components=[
                ActionComponent.from_dict(comp)
                for comp in d.get("components", [])
            ],
        )


@dataclass
class Actor:
    name: str
    actions: list[Action] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "actions": [act.to_dict() for act in self.actions],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Actor":
        return Actor(
            name=d["name"],
            actions=[
                Action.from_dict(act)
                for act in d.get("actions", [])
            ],
        )