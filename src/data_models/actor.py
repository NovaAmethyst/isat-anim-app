"""
Defines classes used to represent actors.

Classes
-------
Action
ActionComponent
Actor
Direction
"""

import base64
import io
from dataclasses import dataclass, field
from enum import StrEnum
from PIL import Image


class Direction(StrEnum):
    LEFT = "Left"
    RIGHT = "Right"
    UP = "Up"
    DOWN = "Down"


@dataclass
class ActionComponent:
    """
    A class to represent a component of an action.

    Attributes
    ----------
    sprite : PIL.Image.Image
        the sprite used during the action component
    duration_sec : float
        the duration of the action component in seconds
    x_offset : int
        the amount of pixels moved horizontally during the action component
    y_offset : int
        the amount of pixels moved vertically during the action component
    movement_speed : int | None
        the RPG Maker movement speed associated with the component
    direction : Direction | None
        the direction in which the actor is moving

    Methods
    -------
    to_dict():
        Creates a dictionary representing the ActionComponent object.

    Static Methods
    --------------
    from_dict(d):
        Creates an ActionComponent object using the data stored in a dictionary.
    """
    sprite: Image.Image
    duration_sec: float
    x_offset: int
    y_offset: int
    movement_speed: int | None = None
    direction: Direction | None = None

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the ActionComponent object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the ActionComponent object
        """
        buffer: io.BytesIO = io.BytesIO()
        self.sprite.save(buffer, format="PNG")
        return {
            "sprite": base64.b64encode(buffer.getvalue()).decode("utf-8"),
            "duration_sec": self.duration_sec,
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
            "movement_speed": self.movement_speed,
            "direction": self.direction,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "ActionComponent":
        """
        Creates an ActionComponent object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the ActionComponent object creation

        Returns
        -------
        ActionComponent
            the ActionComponent object corresponding to the given dictionary
        """
        sprite_data: bytes = base64.b64decode(d["sprite"])
        direction_str: str | None = d.get("direction", None)
        return ActionComponent(
            sprite=Image.open(io.BytesIO(sprite_data)),
            duration_sec=d["duration_sec"],
            x_offset=d["x_offset"],
            y_offset=d["y_offset"],
            movement_speed=d.get("movement_speed", None),
            direction=None if direction_str is None else Direction(direction_str),
        )


@dataclass
class Action:
    """
    A class to represent an action.

    Attributes
    ----------
    name : str
        the name of the action
    components : list[ActionComponent] (default [])
        the components if the action

    Methods
    -------
    to_dict():
        Creates a dictionary representing the Action object.

    Static Methods
    --------------
    from_dict(d):
        Creates an Action object using the data stored in a dictionary.
    """
    name: str
    components: list[ActionComponent] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the Action object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the Action object
        """
        return {
            "name": self.name,
            "components": [comp.to_dict() for comp in self.components],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Action":
        """
        Creates an Action object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the Action object creation

        Returns
        -------
        Action
            the Action object corresponding to the given dictionary
        """
        return Action(
            name=d["name"],
            components=[
                ActionComponent.from_dict(comp)
                for comp in d.get("components", [])
            ],
        )


@dataclass
class Actor:
    """
    A class to represent an actor.

    Attributes
    ----------
    name : str
        the name of the actor
    actions : list[Action] (default [])
        the actions available to the actor

    Methods
    -------
    to_dict():
        Creates a dictionary representing the Actor object.

    Static Methods
    --------------
    from_dict(d):
        Creates an Actor object using the data stored in a dictionary.
    """
    name: str
    actions: list[Action] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Creates a dictionary representing the Actor object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            the dictionary representing the Actor object
        """
        return {
            "name": self.name,
            "actions": [act.to_dict() for act in self.actions],
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Actor":
        """
        Creates an Actor object using the data stored in a dictionary.

        Parameters
        ----------
        d : dict
            data to use for the Actor object creation

        Returns
        -------
        Actor
            the Actor object corresponding to the given dictionary
        """
        return Actor(
            name=d["name"],
            actions=[
                Action.from_dict(act)
                for act in d.get("actions", [])
            ],
        )