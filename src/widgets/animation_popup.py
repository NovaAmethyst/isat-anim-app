import tkinter as tk
import time
from PIL import ImageTk


class AnimationPopup:
    def __init__(
        self,
        master,
        frames: list[ImageTk],
        fps: int,
        title: str,
    ):
        self.master = master
        self.frames = frames
        self.fps = fps
        self.frame_count = len(frames)
        self.running = True

        self.popup = tk.Toplevel(master)
        self.popup.title(title)
        self.popup.protocol("WM_DELETE_WINDOW", self.close)
        w, h = frames[0].width(), frames[0].height()
        self.popup.geometry(f"{w}x{h}")
        self.popup.resizable(False, False)

        self.label = tk.Label(self.popup)
        self.label.pack()

        self.duration = self.frame_count / fps  # Total duration in seconds

        self.start_time = time.perf_counter()
        self.animate()

    def animate(self):
        if not self.running:
            return
        elapsed = time.perf_counter() - self.start_time

        if elapsed > self.duration:
            self.start_time = time.perf_counter()
            self.animate()
            return

        frame_index = int(elapsed * self.fps)
        frame_index = min(frame_index, self.frame_count - 1)

        self.label.configure(image=self.frames[frame_index])

        self.popup.after(1, self.animate)

    def close(self):
        self.running = False
        self.popup.destroy()