# modules/distance.py
# Distance estimation using per-class bounding box size heuristic.
# Each COCO class has a known approximate real-world height (metres).
# Using known physical size + observed box height ratio gives a much
# better distance estimate than a single generic reference size.

# Formula:
#   distance = (real_height_m * frame_height) / box_height_pixels
# This is the basic pinhole camera model - works well for typical webcam FOV.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------- Per-class real-world heights (metres) ----------
# Approximate average height of each object in real life.
# Used to compute distance from bounding box height in pixels.
CLASS_HEIGHTS_M = {
    # People
    "person":           1.70,
    # Vehicles
    "bicycle":          1.00,
    "car":              1.50,
    "motorcycle":       1.10,
    "bus":              3.00,
    "truck":            2.50,
    # Animals
    "cat":              0.25,
    "dog":              0.40,
    "bird":             0.20,
    "horse":            1.60,
    "cow":              1.40,
    # Furniture
    "chair":            0.90,
    "couch":            0.85,
    "bed":              0.60,
    "dining table":     0.75,
    "toilet":           0.75,
    # Electronics
    "tv":               0.60,
    "laptop":           0.30,
    "cell phone":       0.15,
    "remote":           0.18,
    "keyboard":         0.04,
    # Kitchen
    "bottle":           0.25,
    "cup":              0.12,
    "bowl":             0.10,
    "banana":           0.18,
    "apple":            0.08,
    "orange":           0.08,
    "pizza":            0.30,
    "cake":             0.15,
    # Accessories
    "backpack":         0.50,
    "handbag":          0.30,
    "umbrella":         1.00,
    "suitcase":         0.65,
    "hat":              0.20,
    # Sports
    "sports ball":      0.22,
    "frisbee":          0.27,
    "skateboard":       0.10,
    "surfboard":        1.80,
    "tennis racket":    0.68,
    # Other common objects
    "book":             0.24,
    "clock":            0.30,
    "vase":             0.30,
    "scissors":         0.18,
    "toothbrush":       0.19,
    "hair drier":       0.25,
    "traffic light":    0.80,
    "fire hydrant":     0.60,
    "stop sign":        0.75,
    "bench":            0.90,
    "potted plant":     0.40,
    "sink":             0.25,
    "refrigerator":     1.80,
    "oven":             0.90,
    "microwave":        0.30,
    "toaster":          0.20,
    "wine glass":       0.22,
    "fork":             0.18,
    "knife":            0.20,
    "spoon":            0.18,
}

# Default height for any class not in the lookup table
DEFAULT_HEIGHT_M = 0.40

# Camera approximate vertical field of view in degrees (typical webcam ~60 deg)
# This lets us compute the focal length in pixels for the pinhole model.
CAMERA_VFOV_DEG = 60.0

MIN_DISTANCE_M = 0.2
MAX_DISTANCE_M = 8.0


def estimate_distance(box, frame_height, frame=None):
    """
    Estimates distance to the detected object using the pinhole camera model.

    box: (x1, y1, x2, y2)
    frame_height: height of camera frame in pixels
    frame: unused (kept for API compatibility with depth model version)
    class_name: COCO class name of the detected object

    Returns: estimated distance in metres (float)
    """
    # This signature is called without class_name from main.py,
    # so we provide a separate function below for class-aware estimation.
    return _estimate_with_class(box, frame_height, class_name=None)


def estimate_distance_for_class(box, frame_height, class_name, frame=None):
    """
    Class-aware distance estimation. Use this in main.py for best results.
    """
    return _estimate_with_class(box, frame_height, class_name=class_name)


def _estimate_with_class(box, frame_height, class_name=None):
    import math

    x1, y1, x2, y2 = box
    box_height_px = max(y2 - y1, 1)

    # Get real-world height for this class
    real_height_m = CLASS_HEIGHTS_M.get(class_name, DEFAULT_HEIGHT_M) if class_name else DEFAULT_HEIGHT_M

    # Focal length in pixels from camera vertical FOV
    vfov_rad = math.radians(CAMERA_VFOV_DEG)
    focal_length_px = (frame_height / 2.0) / math.tan(vfov_rad / 2.0)

    # Pinhole camera distance formula
    distance_m = (real_height_m * focal_length_px) / box_height_px

    return round(max(MIN_DISTANCE_M, min(MAX_DISTANCE_M, distance_m)), 1)


# ---------- Standalone test ----------
if __name__ == "__main__":
    frame_height = 480

    tests = [
        ((100, 50,  300, 430), "person"),    # large box, close person
        ((200, 150, 350, 330), "bottle"),    # medium box, bottle
        ((280, 200, 330, 260), "cell phone"),# small box, phone far away
        ((100, 100, 500, 400), "car"),       # large box, car close
        ((250, 220, 350, 300), "cup"),       # small cup
    ]

    for box, cls in tests:
        d = estimate_distance_for_class(box, frame_height, cls)
        print(f"{cls:15s} box={box} -> {d}m")
