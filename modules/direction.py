# modules/direction.py
# Determines direction from bounding box X-center position.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_direction(box, frame_width):
    x1, _, x2, _ = box
    box_center_x = (x1 + x2) / 2
    relative_position = box_center_x / frame_width
    if relative_position < config.LEFT_ZONE_MAX:
        return "left"
    elif relative_position > config.RIGHT_ZONE_MIN:
        return "right"
    else:
        return "centre"

def direction_phrase(direction):
    if direction == "left":
        return "on your left"
    elif direction == "right":
        return "on your right"
    else:
        return "directly ahead"
