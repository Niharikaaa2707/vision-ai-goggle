# modules/camera_manager.py
# Handles camera capture and basic disconnect detection.

import cv2

class CameraManager:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self._open_camera()

    def _open_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if not self.cap.isOpened():
            print("[CameraManager] ERROR: Could not open camera.")
            return False
        print("[CameraManager] Camera opened successfully.")
        return True

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        ret, frame = self.cap.read()
        if not ret:
            print("[CameraManager] WARNING: Frame read failed.")
            return False, None
        return True, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
