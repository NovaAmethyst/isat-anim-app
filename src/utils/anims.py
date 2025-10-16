import numpy as np
from math import ceil
from moviepy import ImageSequenceClip
from PIL import Image

from src.data_models import *


def get_action_frames(action: Action, fps: int) -> dict:
    if len(action.components) == 0:
        return {
            "dx": np.array([], dtype=int),
            "dy": np.array([], dtype=int),
            "sprites": [],
        }

    action_sprites = []
    frames_dx = []
    frames_dy = []

    for comp in action.components:
        n_comp_frames = int(comp.duration_sec * fps)
        comp_dxs = np.diff(np.linspace(0, comp.x_offset, num=n_comp_frames + 1).astype(int))
        comp_dys = np.diff(np.linspace(0, comp.y_offset, num=n_comp_frames + 1).astype(int))

        frames_dx.append(comp_dxs)
        frames_dy.append(comp_dys)
        action_sprites.extend([comp.sprite] * n_comp_frames)

    return {
        "dx": np.concatenate(frames_dx),
        "dy": np.concatenate(frames_dy),
        "sprites": action_sprites,
    }


def get_scene_actor_frames(scene_actor: SceneActor, n_frames: int, fps: int) -> dict:
    curr_frame = 0
    curr_time = 0.0

    dx = []
    dy = []
    sprites = []
    action_dict = {}

    for sched in scene_actor.scheduled_actions:
        if curr_frame >= n_frames:
            break

        if sched.action.name not in action_dict:
            action_dict[sched.action.name] = get_action_frames(sched.action, fps)

        action_data = action_dict[sched.action.name]
        action_final_frame = int((curr_time + sched.duration_sec) * fps)
        n_action_frames = action_final_frame - curr_frame
        n_offset_frames = int(fps * sched.start_offset_sec)
        n_action_cycles = ceil((n_offset_frames + n_action_frames) / len(action_data["dx"]))

        action_dx = np.concatenate(
            [action_data["dx"]] * n_action_cycles
        )[n_offset_frames:n_offset_frames + n_action_frames]
        dx.append(action_dx)

        action_dy = np.concatenate(
            [action_data["dy"]] * n_action_cycles
        )[n_offset_frames:n_offset_frames + n_action_frames]
        dy.append(action_dy)

        if sched.is_visible:
            sched_sprites = (
                action_data["sprites"] * n_action_cycles
            )[n_offset_frames:n_offset_frames + n_action_frames]
        else:
            sched_sprites = [None] * n_action_frames
        sprites.extend(sched_sprites)

        curr_frame += n_action_frames
        curr_time += sched.duration_sec

    if len(dx) == 0:
        return {
            "sprites": [None] * n_frames,
            "x": np.array([scene_actor.start_x] * n_frames),
            "y": np.array([scene_actor.start_y] * n_frames),
        }

    x = np.concatenate(dx).cumsum() + scene_actor.start_x
    y = np.concatenate(dy).cumsum() + scene_actor.start_y

    n_missing = max(n_frames - len(dx), 0)
    x = np.concatenate([x, np.array([x[-1]] * n_missing).astype(int)])
    y = np.concatenate([y, np.array([y[-1]] * n_missing).astype(int)])
    sprites += [sprites[-1]] * n_missing

    return {
        "sprites": sprites[:n_frames],
        "x": x[:n_frames],
        "y": y[:n_frames],
    }


def get_camera_pos(camera: Camera, actors_frame_info: dict, n_frames: int, fps: int) -> dict:
    x = camera.start_x
    y = camera.start_y
    x_list = []
    y_list = []

    curr_frame = 0
    curr_time = 0.0

    for move in camera.moves:
        if curr_frame >= n_frames:
            break
        n_move_frames = int((move.duration_sec + curr_time) * fps) - curr_frame

        if move.linked_sa is None:
            move_x = np.linspace(0, move.x, n_move_frames + 1).astype(int) + x
            move_y = np.linspace(0, move.y, n_move_frames + 1).astype(int) + y
        else:
            sa = move.linked_sa
            sa_frame_info = actors_frame_info[str(sa)]
            move_x = sa_frame_info["x"][curr_frame:curr_frame + n_move_frames]
            move_y = sa_frame_info["y"][curr_frame:curr_frame + n_move_frames]

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

    cam_x = np.concatenate(x_list)
    cam_y = np.concatenate(y_list)

    if len(cam_x) == 0:
        return {
            "x": np.array([x] * n_frames),
            "y": np.array([y] * n_frames),
        }

    n_missing = max(n_frames - len(cam_x), 0)
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
) -> list[np.array]:
    frames = []

    bg_w, bg_h = background.size
    x0, y0 = bg_w // 2, bg_h // 2
    cam_w, cam_h = camera.width, camera.height

    for i in range(n_frames):
        frame = background.copy()
        for sa in actors:
            actor_frame_info = actors_frame_info[str(sa)]
            sprite = actor_frame_info["sprites"][i]
            if sprite is None:
                continue

            sw, sh = sprite.size
            x = int(actor_frame_info["x"][i] - sw / 2)
            y = int(actor_frame_info["y"][i] - sh / 2)
            frame.paste(sprite, (x0 + x, y0 - y), sprite)

        if cam_w >= bg_w:
            cam_l = 0
            cam_r = bg_w
        else:
            cam_x = x0 + cam_pos["x"][i]
            cam_l = cam_x - cam_w // 2
            if cam_l < 0:
                cam_l = 0

            cam_r = cam_l + cam_w
            if cam_r > bg_w:
                diff = cam_r - bg_w
                cam_r = bg_w
                cam_l -= diff

        if cam_h >= bg_h:
            cam_t = 0
            cam_b = bg_h
        else:
            cam_y = y0 - cam_pos["y"][i]
            cam_t = cam_y - cam_h // 2
            if cam_t < 0:
                cam_t = 0

            cam_b = cam_t + cam_h
            if cam_b > bg_h:
                diff = cam_b - bg_h
                cam_b = bg_h
                cam_t -= diff

        frames.append(np.array(frame)[cam_t:cam_b, cam_l:cam_r])

    return frames


def make_video_from_frames(frames, fps: int, output_path: str) -> None:
    clip = ImageSequenceClip(frames, fps)
    clip.write_videofile(output_path, codec="libx264")