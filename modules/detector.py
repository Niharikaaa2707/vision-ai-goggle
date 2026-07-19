# modules/detector.py
# YOLOv8s object detection wrapper with multi-frame confirmation.
# An object must appear in DETECTION_CONFIRMATION_FRAMES consecutive frames
# before being returned as a confirmed detection - filters phantom detections.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import defaultdict
from ultralytics import YOLO
import config

class Detector:
    def __init__(self, model_path="models/yolov8s.pt", confidence_threshold=None):
        self.confidence_threshold = confidence_threshold or config.CONFIDENCE_THRESHOLD
        self.confirmation_frames = config.DETECTION_CONFIRMATION_FRAMES
        print(f"[Detector] Loading YOLOv8s from {model_path} ...")
        self.model = YOLO(model_path)
        print("[Detector] Model loaded.")
        self._seen_counts = defaultdict(int)
        self._all_classes_seen_last_frame = set()

    def detect(self, frame):
        raw_results = self.model(
            frame,
            conf=self.confidence_threshold,
            verbose=False
        )

        raw_detections = []
        classes_seen_this_frame = set()

        for result in raw_results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                raw_detections.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "box": (int(x1), int(y1), int(x2), int(y2))
                })
                classes_seen_this_frame.add(class_name)

        for cls in classes_seen_this_frame:
            self._seen_counts[cls] += 1

        for cls in self._all_classes_seen_last_frame:
            if cls not in classes_seen_this_frame:
                self._seen_counts[cls] = 0

        self._all_classes_seen_last_frame = classes_seen_this_frame

        confirmed = [
            d for d in raw_detections
            if self._seen_counts[d["class_name"]] >= self.confirmation_frames
        ]
        return confirmed

# ---------- Standalone test ----------
if __name__ == "__main__":
    import cv2
    from camera_manager import CameraManager
    cam = CameraManager(camera_index=0)
    detector = Detector(model_path="../models/yolov8s.pt")
    print(f"Multi-frame confirmation: {detector.confirmation_frames} frames required.")
    print("Press 'q' to quit.")
    while True:
        success, frame = cam.get_frame()
        if not success:
            break
        detections = detector.detect(frame)
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = f'{det["class_name"]} {det["confidence"]:.2f}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, max(y1 - 10, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Detector Test - VISION", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()