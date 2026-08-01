# modules/test_phase2_combined.py
# Combines camera + detector + direction + distance to visually verify
# everything works together before adding TTS in Phase 3.

import cv2
from camera_manager import CameraManager
from detector import Detector
from direction import get_direction, direction_phrase
from distance import estimate_distance

cam = CameraManager(camera_index=0)
detector = Detector(model_path="../models/yolov8s.pt", confidence_threshold=0.45)

print("Press 'q' to quit test window.")

while True:
    success, frame = cam.get_frame()
    if not success:
        print("Camera failed. Exiting.")
        break

    frame_height, frame_width = frame.shape[:2]
    detections = detector.detect(frame)

    for det in detections:
        box = det["box"]
        x1, y1, x2, y2 = box

        direction = get_direction(box, frame_width)
        dist = estimate_distance(box, frame_height)

        label = f'{det["class_name"]} | {direction_phrase(direction)} | {dist}m'

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, max(y1 - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    cv2.imshow("Phase 2 Combined Test - VISION", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
