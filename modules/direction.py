# modules/direction.py
# Determines direction (left / centre / right) from a bounding box's
# X-center position relative to frame width, per spec 5.6.

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

# ---------- Standalone test ----------
if __name__ == "__main__":
    test_frame_width = 640
    test_boxes = {
        "Left object":   (10, 100, 100, 200),
        "Centre object": (280, 100, 360, 200),
        "Right object":  (550, 100, 630, 200),
    }
    for label, box in test_boxes.items():
        d = get_direction(box, test_frame_width)
        print(f"{label}: box={box} -> direction={d} ({direction_phrase(d)})")
