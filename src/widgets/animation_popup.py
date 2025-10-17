"""
Defines a class to display an animation inside a popup tab.

Classes
-------
AnimationPopup
"""

import tkinter as tk
import time
from PIL import ImageTk


class AnimationPopup:
    """
    A class to handle displaying an animation in a popup.

    Attributes
    ----------
    frames : list[ImageTk.PhotoImage]
        the images being animated
    fps : int
        the number of frames per second
    frame_count : int
        the total number of frames
    running : bool
        whether the animation is currently running
    popup : tk.Toplevel
        the tkinter element used as a popup
    label : tk.Label
        the tkinter element used to display images
    duration : float
        the duration of the animation in seconds
    start_time : float
        the time at which the animation started

    Methods
    -------
    animate() -> None:
        Runs the next frame of the animation.
    close() -> None:
        Stops the animation and closes popup cleanly.
    """
    def __init__(
        self,
        master: tk.Misc,
        frames: list[ImageTk.PhotoImage],
        fps: int,
        title: str,
    ):
        """
        Constructs all necessary attributes for the animation popup and starts the animation.

        Parameters
        ----------
        master : tk.Misc
            the tkinter element to which the popup is connected
        frames : list[PIL.ImageTk.PhotoImage]
            the frames of the animation
        fps : int
            the number of frames per second to animate
        title : str
            the title of the popup
        """
        # Initiate popup attributes
        self.frames: list[ImageTk.PhotoImage] = frames
        self.fps: int = fps
        self.frame_count: int = len(frames)
        self.running: bool = True

        # Handle popup creation
        self.popup: tk.Toplevel = tk.Toplevel(master)
        self.popup.title(title)
        self.popup.protocol("WM_DELETE_WINDOW", self.close)
        w, h = frames[0].width(), frames[0].height()
        self.popup.geometry(f"{w}x{h}")
        self.popup.resizable(False, False)

        # Create area for image display
        self.label: tk.Label = tk.Label(self.popup)
        self.label.pack()

        self.duration: float = self.frame_count / fps  # Total duration in seconds

        # Start the animation
        self.start_time: float = time.perf_counter()
        self.animate()

    def animate(self) -> None:
        """
        Runs the next frame of the animation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Stop if the animation isn't running
        if not self.running:
            return
        # Get timestamp to animate
        elapsed: float = time.perf_counter() - self.start_time

        # Restart animation if previous anim cycle is over
        if elapsed > self.duration:
            self.start_time = time.perf_counter()
            self.animate()
            return

        # Get the current frame index
        frame_index: int = int(elapsed * self.fps)
        frame_index = min(frame_index, self.frame_count - 1)

        # Update the animation image
        self.label.configure(image=self.frames[frame_index])

        # Animate next frame
        self.popup.after(1, self.animate)

    def close(self) -> None:
        """
        Stops the animation and closes popup cleanly.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.running = False
        self.popup.destroy()