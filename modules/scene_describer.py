# modules/scene_describer.py
# Turns a detection (class + direction + distance) into a natural sentence,
# and applies repeat-suppression logic per spec 5.1:
# "Same object class not re-announced within 3 seconds unless distance changes >0.5m"

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.direction import direction_phrase


class SceneDescriber:
    def __init__(self):
        # Tracks last announcement per class: { class_name: (timestamp, distance) }
        self._last_announced = {}

    def should_announce(self, class_name, distance):
        """
        Returns True if this detection should be announced now,
        based on repeat-suppression rules.
        """
        now = time.time()

        if class_name not in self._last_announced:
            return True

        last_time, last_distance = self._last_announced[class_name]
        time_elapsed = now - last_time
        distance_changed = abs(distance - last_distance) > config.DISTANCE_CHANGE_THRESHOLD_M

        if time_elapsed >= config.REPEAT_SUPPRESSION_SECONDS or distance_changed:
            return True

        return False

    def mark_announced(self, class_name, distance):
        self._last_announced[class_name] = (time.time(), distance)

    def build_sentence(self, class_name, direction, distance):
        """
        Builds a natural sentence, e.g.:
        "Person ahead, 2 metres" / "Bottle on your right, 1.5 metres" / "Bicycle on your left"
        """
        phrase = direction_phrase(direction)

        if phrase == "directly ahead":
            return f"{class_name.capitalize()} ahead, {distance} metres"
        else:
            return f"{class_name.capitalize()} {phrase}, {distance} metres"

    def process_detection(self, class_name, direction, distance):
        """
        Combines suppression check + sentence building.
        Returns sentence (str) if it should be announced, else None.
        """
        if self.should_announce(class_name, distance):
            self.mark_announced(class_name, distance)
            return self.build_sentence(class_name, direction, distance)
        return None


# ---------- Standalone test ----------
if __name__ == "__main__":
    describer = SceneDescriber()

    print("Test 1: first detection of 'person' -> should announce")
    s = describer.process_detection("person", "centre", 2.0)
    print(s)

    print("\nTest 2: same 'person', same distance, immediately again -> should be suppressed")
    s = describer.process_detection("person", "centre", 2.0)
    print(s)  # expected: None

    print("\nTest 3: same 'person', distance changed by > 0.5m -> should announce")
    s = describer.process_detection("person", "centre", 1.2)
    print(s)

    print("\nTest 4: different class 'bottle' -> should announce")
    s = describer.process_detection("bottle", "right", 1.5)
    print(s)
