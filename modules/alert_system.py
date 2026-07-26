# modules/alert_system.py
# Proximity alert system per spec 5.2.
# Now accepts optional object_name so alerts say "Bottle very close"
# instead of generic "Obstacle very close".

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class AlertSystem:
    def __init__(self):
        self._last_warning_time = 0
        self._last_caution_time = 0

    def beep_critical(self):
        if HAS_WINSOUND:
            for _ in range(3):
                winsound.Beep(2500, 150)
                time.sleep(0.05)
        else:
            print("[AlertSystem] CRITICAL BEEP")

    def evaluate(self, distance_m, object_name=None):
        """
        distance_m: estimated distance
        object_name: class name of the detected object (e.g. "bottle", "person")
                     used to build a specific alert message instead of generic "Obstacle"

        Returns: (tier, message or None, immediate)
        """
        now = time.time()
        name = object_name.capitalize() if object_name else "Obstacle"

        if distance_m < config.CRITICAL_DISTANCE_M:
            self.beep_critical()
            return "critical", None, True

        elif distance_m < config.WARNING_DISTANCE_M:
            if now - self._last_warning_time >= config.WARNING_COOLDOWN_SECONDS:
                self._last_warning_time = now
                return "warning", f"{name} very close", False
            return "warning", None, False

        elif distance_m < config.CAUTION_DISTANCE_M:
            if now - self._last_caution_time >= config.CAUTION_COOLDOWN_SECONDS:
                self._last_caution_time = now
                return "caution", f"{name} ahead, {distance_m} metres", False
            return "caution", None, False

        else:
            return "none", None, False


# ---------- Standalone test ----------
if __name__ == "__main__":
    alerts = AlertSystem()
    tests = [(0.3, "person"), (0.7, "bottle"), (1.5, "chair"), (3.0, None)]
    for d, name in tests:
        tier, msg, immediate = alerts.evaluate(d, object_name=name)
        print(f"Distance {d}m | object={name} -> tier={tier}, message={msg}")
        time.sleep(0.5)
