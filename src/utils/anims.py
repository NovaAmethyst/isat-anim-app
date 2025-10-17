"""
Functions used to compute and create animations.

Functions
---------
compose_frame(PIL.Image.Image, dict, dict, list[SceneActor], Camera, int) -> list[npt.NDArray[np.int64]]:
    Gives the frames of an animation as numpy arrays.
get_action_frames(Action, int) -> dict:
    Creates a dict of lists for sprites and moves on the x and y axes for a given action.
get_camera_pos(Camera, dict, int, int) -> dict:
    Creates a dict of lists for x and y coordinates for the center of the camera.
get_scene_actor_frames(SceneActor, int, int) -> dict:
    Creates a dict of lists for sprites and x and y coordinates for a given scene actor.
make_video_from_frames(list[npt.NDArray[np.int64]], int, str) -> None:
    Creates and saves the given frames as a mp4 video.
"""

import numpy as np
import numpy.typing as npt
from math import ceil
from moviepy import ImageSequenceClip
from PIL import Image

from src.data_models import *


def get_action_frames(action: Action, fps: int) -> dict:
    """
    Creates a dict of lists for sprites and moves on the x and y axes for a given action.

    Parameters
    ----------
    action : Action
        the action from which to extract move distances and sprites
    fps : int
        the number of frames per second

    Returns
    -------
    dict
        the move distances on the x (dx: npt.NDArray[np.int64]) and y (dy: npt.NDArray[np.int64]) axes, and the sprites (sprites: PIL.Image.Image)
    """
    if len(action.components) == 0:
        return {
            "dx": np.array([], dtype=int),
            "dy": np.array([], dtype=int),
            "sprites": [],
        }

    action_sprites: list[Image.Image] = []
    frames_dx: list[npt.NDArray[np.int64]] = []
    frames_dy: list[npt.NDArray[np.int64]] = []

    # Get the moves and sprites for each action component
    for comp in action.components:
        n_comp_frames: int = int(comp.duration_sec * fps)
        comp_dxs: npt.NDArray[np.int64] = np.diff(np.linspace(0, comp.x_offset, num=n_comp_frames + 1).astype(int))
        comp_dys: npt.NDArray[np.int64] = np.diff(np.linspace(0, comp.y_offset, num=n_comp_frames + 1).astype(int))

        frames_dx.append(comp_dxs)
        frames_dy.append(comp_dys)
        action_sprites.extend([comp.sprite] * n_comp_frames)

    return {
        "dx": np.concatenate(frames_dx),
        "dy": np.concatenate(frames_dy),
        "sprites": action_sprites,
    }


def get_scene_actor_frames(scene_actor: SceneActor, n_frames: int, fps: int) -> dict:
    """
    Creates a dict of lists for sprites and x and y coordinates for a given scene actor.

    Parameters
    ----------
    scene_actor : SceneActor
        the scene actor from which to extract the frames information
    n_frames : int
        the number of frames to extract
    fps : int
        the number of frames per second

    Returns
    -------
    dict
        the x (x: npt.NDArray[np.int64]) and y (y: npt.NDArray[np.int64]) coordinates, and the sprites to display or not (sprites: list[PIL.Image.Image | None])
    """
    curr_frame: int = 0
    curr_time: float = 0.0

    dx: list[npt.NDArray[np.int64]] = []
    dy: list[npt.NDArray[np.int64]] = []
    sprites: list[Image.Image | None] = []
    action_dict: dict = {}

    # Get the moves and sprites of each scheduled action
    for sched in scene_actor.scheduled_actions:
        # Stop if the actions last longer than the set number of frames
        if curr_frame >= n_frames:
            break

        # Add the frames of the action to the cache if they haven't been yet
        if sched.action.name not in action_dict:
            action_dict[sched.action.name] = get_action_frames(sched.action, fps)

        action_data: dict = action_dict[sched.action.name]
        # Get the range to copy for the scheduled action
        action_final_frame: int = int((curr_time + sched.duration_sec) * fps)
        n_action_frames: int = action_final_frame - curr_frame
        n_offset_frames: int = int(fps * sched.start_offset_sec)
        # Compute the number of repeats needed to get the whole range
        n_action_cycles: int = ceil((n_offset_frames + n_action_frames) / len(action_data["dx"]))

        # Get the moves on the x axis for the scheduled action
        action_dx: npt.NDArray[np.int64] = np.concatenate(
            [action_data["dx"]] * n_action_cycles
        )[n_offset_frames:n_offset_frames + n_action_frames]
        dx.append(action_dx)

        # Get the moves on the y axis for the scheduled action
        action_dy: npt.NDArray[np.int64] = np.concatenate(
            [action_data["dy"]] * n_action_cycles
        )[n_offset_frames:n_offset_frames + n_action_frames]
        dy.append(action_dy)

        # Get the sprites if the action is visible, None otherwise
        if sched.is_visible:
            sched_sprites: list[Image.Image | None] = (
                action_data["sprites"] * n_action_cycles
            )[n_offset_frames:n_offset_frames + n_action_frames]
        else:
            sched_sprites: list[Image.Image | None] = [None] * n_action_frames
        sprites.extend(sched_sprites)

        curr_frame += n_action_frames
        curr_time += sched.duration_sec

    if len(dx) == 0:
        return {
            "sprites": [None] * n_frames,
            "x": np.array([scene_actor.start_x] * n_frames),
            "y": np.array([scene_actor.start_y] * n_frames),
        }

    # Get the x and y coordinates of the actor
    x: npt.NDArray[np.int64] = np.concatenate(dx).cumsum() + scene_actor.start_x
    y: npt.NDArray[np.int64] = np.concatenate(dy).cumsum() + scene_actor.start_y

    # Fill if fewer action frames than total frames (idle actor)
    n_missing: int = max(n_frames - len(dx), 0)
    x = np.concatenate([x, np.array([x[-1]] * n_missing).astype(int)])
    y = np.concatenate([y, np.array([y[-1]] * n_missing).astype(int)])
    sprites += [sprites[-1]] * n_missing

    return {
        "sprites": sprites[:n_frames],
        "x": x[:n_frames],
        "y": y[:n_frames],
    }


def get_camera_pos(camera: Camera, actors_frame_info: dict, n_frames: int, fps: int) -> dict:
    """
    Creates a dict of lists for x and y coordinates for the center of the camera.

    Parameters
    ----------
    camera : Camera
        the camera to get coordinates for
    actors_frame_info : dict
        a dictionary containing the coordinates and sprites for each actor in the scene
    n_frames : int
        the number of frames to extract
    fps : int
        the number of frames per second

    Returns
    -------
    dict
        the x (x: npt.NDArray[np.int64]) and y (y: npt.NDArray[np.int64]) coordinates
    """
    x: int = camera.start_x
    y: int = camera.start_y
    x_list: list[npt.NDArray[np.int64]] = []
    y_list: list[npt.NDArray[np.int64]] = []

    curr_frame: int = 0
    curr_time: float = 0.0

    # Get camera center coordinates for each camera movement
    for move in camera.moves:
        # Stop early if camera moves last longer than number of frames
        if curr_frame >= n_frames:
            break
        n_move_frames: int = int((move.duration_sec + curr_time) * fps) - curr_frame

        # Copy actor coords if move is linked to one, otherwise infer from total camera movement and position
        if move.linked_sa is None:
            move_x: npt.NDArray[np.int64] = np.linspace(0, move.x, n_move_frames + 1).astype(int) + x
            move_y: npt.NDArray[np.int64] = np.linspace(0, move.y, n_move_frames + 1).astype(int) + y
        else:
            sa: SceneActor = move.linked_sa
            sa_frame_info: dict = actors_frame_info[str(sa)]
            move_x: npt.NDArray[np.int64] = sa_frame_info["x"][curr_frame:curr_frame + n_move_frames]
            move_y: npt.NDArray[np.int64] = sa_frame_info["y"][curr_frame:curr_frame + n_move_frames]

        x_list.append(move_x)
        y_list.append(move_y)

        if n_move_frames != 0:
            x = move_x[-1]
            y = move_y[-1]

        curr_frame += n_move_frames
        curr_time += move.duration_sec

    if len(x_list) == 0:
        return {
            "x": np.array([x] * n_frames),
            "y": np.array([y] * n_frames),
        }

    cam_x: npt.NDArray[np.int64] = np.concatenate(x_list)
    cam_y: npt.NDArray[np.int64] = np.concatenate(y_list)

    if len(cam_x) == 0:
        return {
            "x": np.array([x] * n_frames),
            "y": np.array([y] * n_frames),
        }

    n_missing: int = max(n_frames - len(cam_x), 0)
    cam_x = np.concatenate([cam_x, np.array([cam_x[-1]] * n_missing).astype(int)])
    cam_y = np.concatenate([cam_y, np.array([cam_y[-1]] * n_missing).astype(int)])

    return {"x": cam_x, "y": cam_y}


def compose_frames(
    background: Image.Image,
    actors_frame_info: dict,
    cam_pos: dict,
    actors: list[SceneActor],
    camera: Camera,
    n_frames: int,
) -> list[npt.NDArray[np.int64]]:
    """
    Gives the frames of an animation as numpy arrays.

    Parameters
    ----------
    background : PIL.Image.Image
        the background to use in the animation
    actors_frame_info : dict
        the coordinates and sprites to use for each scene actor
    cam_pos : dict
        the coordinates of the center of the camera
    actors : list[SceneActor]
        the actors present in the scene in order (foreground to background)
    camera : Camera
        the camera used for the scene
    n_frames : int
        the number of frames in the animation

    Returns
    -------
    list[npt.NDArray[np.int64]]
        the list of images stored as numpy arrays
    """
    frames = []

    bg_w, bg_h = background.size
    x0, y0 = bg_w // 2, bg_h // 2
    cam_w, cam_h = camera.width, camera.height

    for i in range(n_frames):
        frame = background.copy()
        # Paste every visible actor sprite at the correct spot
        for sa in reversed(actors):
            actor_frame_info = actors_frame_info[str(sa)]
            sprite = actor_frame_info["sprites"][i]
            # Skip actor if sprite isn't visible
            if sprite is None:
                continue

            # find coords of upper left instead of center of sprite for paste func
            sw, sh = sprite.size
            x = int(actor_frame_info["x"][i] - sw / 2)
            y = int(actor_frame_info["y"][i])# - sh / 2)
            # paste using image index instead of x y coords
            frame.paste(sprite, (x0 + x, y0 - y), sprite)

        # Move camera x pos to not go beyond the background boundaries
        if cam_w >= bg_w:
            cam_l = 0
            cam_r = bg_w
        else:
            cam_x = x0 + cam_pos["x"][i]
            cam_l = max(cam_x - cam_w // 2, 0)

            cam_r = cam_l + cam_w
            if cam_r > bg_w:
                diff = cam_r - bg_w
                cam_r = bg_w
                cam_l -= diff

        # Move camera y pos to not go beyond the backgroudn boundaries
        if cam_h >= bg_h:
            cam_t = 0
            cam_b = bg_h
        else:
            cam_y = y0 - cam_pos["y"][i]
            cam_t = max(cam_y - cam_h // 2, 0)

            cam_b = cam_t + cam_h
            if cam_b > bg_h:
                diff = cam_b - bg_h
                cam_b = bg_h
                cam_t -= diff

        # Get data inside of camera only
        frames.append(np.array(frame)[cam_t:cam_b, cam_l:cam_r])

    return frames


def make_video_from_frames(frames: list[npt.NDArray[np.int64]], fps: int, output_path: str) -> None:
    """
    Creates and saves the given frames as a mp4 video.

    Parameters
    ----------
    frames : list[npt.NDArray[np.int64]]
        the frames stored as numpy arrays to turn into a video
    fps : int
        the number of frames per second to use
    output_path : str
        the path where to save the new video

    Returns
    -------
    None
    """
    clip = ImageSequenceClip(frames, fps)
    clip.write_videofile(output_path, codec="libx264")