# modules/detector.py
# YOLOv8s object detection wrapper.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ultralytics import YOLO
import config

class Detector:
    def __init__(self, model_path="models/yolov8s.pt", confidence_threshold=None):
        self.confidence_threshold = confidence_threshold or config.CONFIDENCE_THRESHOLD
        print(f"[Detector] Loading YOLOv8s from {model_path} ...")
        self.model = YOLO(model_path)
        print("[Detector] Model loaded.")

    def detect(self, frame):
        """
        Runs YOLOv8s on the frame.
        Returns list of dicts:
            { "class_name": str, "confidence": float, "box": (x1,y1,x2,y2) }
        """
        raw_results = self.model(
            frame,
            conf=self.confidence_threshold,
            verbose=False
        )

        detections = []
        for result in raw_results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "box": (int(x1), int(y1), int(x2), int(y2))
                })

        return detections
