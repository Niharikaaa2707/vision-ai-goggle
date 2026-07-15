# config.py
# Shared configuration for VISION - AI Smart Goggle project

# ---------- Camera ----------
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ---------- Detection ----------
YOLO_MODEL_PATH = "models/yolov8s.pt"
CONFIDENCE_THRESHOLD = 0.65      # raised to reduce false positives

# Minimum consecutive frames an object must appear before being announced
# Filters out single-frame ghost detections like phantom cats/dogs
DETECTION_CONFIRMATION_FRAMES = 3

# Minimum box area as fraction of total frame area (filters tiny ghost boxes)
MIN_BOX_AREA_FRACTION = 0.015    # slightly raised from 0.01

# ---------- Direction zones ----------
LEFT_ZONE_MAX = 0.33
RIGHT_ZONE_MIN = 0.66

# ---------- Repeat suppression ----------
REPEAT_SUPPRESSION_SECONDS = 5
DISTANCE_CHANGE_THRESHOLD_M = 0.5

# ---------- Proximity alert tiers (in metres) ----------
CRITICAL_DISTANCE_M = 0.5
WARNING_DISTANCE_M = 1.0
CAUTION_DISTANCE_M = 2.0

# ---------- Alert cooldowns ----------
WARNING_COOLDOWN_SECONDS = 4.0
CAUTION_COOLDOWN_SECONDS = 5.0

# ---------- TTS ----------
PIPER_MODEL_PATH = "models/piper/en_US-ryan-medium.onnx"

# ---------- Logging ----------
LOG_DIR = "logs"
