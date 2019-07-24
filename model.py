"""Gaze tracking model"""

from typing import List, Tuple

from tracking.library import annotate_frames, get_info


class GazeTrackingModel:
    """Stores trained parameters for gaze tracking"""
    def __init__(self, frames: List[Tuple[str, int]]):
        self.frame = None
        self.frame_info = None
        self.parameters = annotate_frames(frames)

    def set_frame(self, frame):
        """Set frame to work on"""
        self.frame = frame
        self.frame_info = get_info(frame, self.parameters)

    def is_blinking(self):
        """Whether person is blinking on the current frame"""
        return self.frame_info['Blinking']

    def get_frame_info(self, frame):
        """Infers frame information"""
        return get_info(frame, self.parameters)
