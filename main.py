# main.py
# VISION - AI Smart Goggle for the Visually Impaired
# Main application loop with full voice command support.

import sys
import os
import time
import traceback
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.camera_manager import CameraManager
from modules.detector import Detector
from modules.direction import get_direction, direction_phrase
from modules.distance import estimate_distance_for_class
from modules.scene_describer import SceneDescriber
from modules.speech_output import SpeechOutput
from modules.speech_input import SpeechInput
from modules.command_matcher import CommandMatcher
from modules.alert_system import AlertSystem
from modules.system_status import SystemStatus
from modules.scene_vlm import get_vlm
import config

tts = None
running = True

# ---------- App state ----------
search_mode = False
search_target = None
search_start_time = None
last_spoken = None
did_you_mean_pending = None

# Quiet mode: suppresses continuous narration after a command
# for a few seconds so the answer can be heard clearly
quiet_mode_until = 0
QUIET_MODE_DURATION = 12.0  # seconds of silence after command response


def set_quiet_mode():
    """Call this after speaking a command response."""
    global quiet_mode_until
    quiet_mode_until = time.time() + QUIET_MODE_DURATION


def is_quiet_mode():
    tts_speaking = tts is not None and tts.is_speaking
    return time.time() < quiet_mode_until or tts_speaking


def speak_command_response(text):
    """Speak a command response and activate quiet mode."""
    global last_spoken
    tts.speak_now(text)
    last_spoken = text
    set_quiet_mode()


def handle_command(intent, target, raw, did_you_mean,
                   detections_with_dist, frame,
                   frame_width, frame_height, status):
    global search_mode, search_target, search_start_time
    global did_you_mean_pending

    # --- Did you mean? ---
    if intent is None and did_you_mean:
        speak_command_response(f"Did you mean {did_you_mean}?")
        did_you_mean_pending = did_you_mean
        return True

    # --- Confirm "did you mean" ---
    if did_you_mean_pending and raw in ["yes", "yeah", "correct", "right"]:
        speak_command_response(f"Okay, {did_you_mean_pending}")
        did_you_mean_pending = None
        return True

    did_you_mean_pending = None

    if intent is None:
        speak_command_response(
            "Sorry, I didn't understand. Say help for available commands."
        )
        return False

    # --- Stop ---
    if intent == "stop":
        search_mode = False
        search_target = None
        speak_command_response("Returning to normal detection mode.")
        return True

    # --- Help ---
    if intent == "help":
        from modules.command_matcher import HELP_TEXT
        speak_command_response(HELP_TEXT)
        return True

    # --- Describe ---
    if intent == "describe":
        speak_command_response("Describing the scene, please wait.")
        result = get_vlm().describe(frame)
        speak_command_response(result)
        return True

    # --- Distance ---
    if intent == "distance":
        if not detections_with_dist:
            speak_command_response("No objects detected ahead right now.")
        else:
            det, dist = detections_with_dist[0]
            d = get_direction(det["box"], frame_width)
            speak_command_response(
                f"{det['class_name']} {direction_phrase(d)}, {dist} metres."
            )
        return True

    # --- Closest ---
    if intent == "closest":
        if not detections_with_dist:
            speak_command_response("No objects detected right now.")
        else:
            det, dist = detections_with_dist[0]
            d = get_direction(det["box"], frame_width)
            speak_command_response(
                f"Closest object is {det['class_name']}, "
                f"{direction_phrase(d)}, {dist} metres."
            )
        return True

    # --- Path clear ---
    if intent == "path_clear":
        obstacles = [
            (det, dist) for det, dist in detections_with_dist
            if dist < config.CAUTION_DISTANCE_M
            and get_direction(det["box"], frame_width) == "centre"
        ]
        if not obstacles:
            speak_command_response("Path looks clear ahead.")
        else:
            det, dist = obstacles[0]
            speak_command_response(
                f"No, {det['class_name']} ahead, {dist} metres. Be careful."
            )
        return True

    # --- Left / Right ---
    if intent in ("left", "right"):
        zone_detections = [
            (det, dist) for det, dist in detections_with_dist
            if get_direction(det["box"], frame_width) == intent
        ]
        if not zone_detections:
            speak_command_response(f"Nothing detected on your {intent}.")
        else:
            det, dist = zone_detections[0]
            speak_command_response(
                f"{det['class_name']} on your {intent}, {dist} metres."
            )
        return True

    # --- Count ---
    if intent == "count":
        if target:
            matches = [d for d, _ in detections_with_dist
                       if d["class_name"] == target]
            count = len(matches)
            if count == 0:
                speak_command_response(f"No {target} detected in frame.")
            elif count == 1:
                speak_command_response(f"One {target} detected.")
            else:
                speak_command_response(f"{count} {target}s detected.")
        else:
            count = len(detections_with_dist)
            speak_command_response(
                f"{count} objects detected." if count else "No objects detected."
            )
        return True

    # --- Read ---
    if intent == "read":
        speak_command_response("Reading text in view, please wait.")
        result = get_vlm().read_text(frame)
        speak_command_response(result)
        return True

    # --- Battery ---
    if intent == "battery":
        percent, plugged = status.get_battery_info()
        if percent is None:
            speak_command_response("Battery information not available.")
        else:
            state = "charging" if plugged else "on battery"
            speak_command_response(
                f"Battery is at {int(percent)} percent, {state}."
            )
        return True

    # --- Repeat ---
    if intent == "repeat":
        if last_spoken:
            speak_command_response(last_spoken)
        else:
            speak_command_response("Nothing to repeat yet.")
        return True

    # --- Find ---
    if intent == "find":
        search_mode = True
        search_target = target
        search_start_time = time.time()
        speak_command_response(
            f"Searching for {target}. Turn around slowly."
        )
        return True

    return False


def run_main_loop():
    global tts, running, search_mode, search_target
    global search_start_time, last_spoken, did_you_mean_pending

    print("[main] Loading subsystems...")

    cam = CameraManager(
        camera_index=config.CAMERA_INDEX,
        width=config.FRAME_WIDTH,
        height=config.FRAME_HEIGHT
    )
    detector = Detector(
        model_path=config.YOLO_MODEL_PATH,
        confidence_threshold=config.CONFIDENCE_THRESHOLD
    )
    describer = SceneDescriber()
    alerts = AlertSystem()
    status = SystemStatus(
        low_threshold=15, critical_threshold=5,
        check_interval_seconds=60
    )
    asr = SpeechInput()
    matcher = CommandMatcher()

    asr.start()

    print("[main] All subsystems ready.")
    print("[main] Press 'q' in camera window or Ctrl+C to stop.")
    tts.speak("VISION system ready. Say help for available commands.")

    while running:
        # --- Camera ---
        success, frame = cam.get_frame()
        if not success:
            tts.speak_now("Camera disconnected. Please check connection.")
            time.sleep(2)
            continue

        frame_height, frame_width = frame.shape[:2]

        # --- Detection ---
        detections = detector.detect(frame)
        min_box_area = config.MIN_BOX_AREA_FRACTION * frame_width * frame_height
        detections = [
            d for d in detections
            if (d["box"][2] - d["box"][0]) * (d["box"][3] - d["box"][1])
            > min_box_area
        ]

        detections_with_dist = [
            (d, estimate_distance_for_class(
                d["box"], frame_height, d["class_name"]))
            for d in detections
        ]
        detections_with_dist.sort(key=lambda x: x[1])

        # --- Voice command (highest priority) ---
        raw_text = asr.get_command()
        if raw_text:
            result = matcher.match(raw_text)
            handle_command(
                result["intent"], result["target"],
                result["raw"], result["did_you_mean"],
                detections_with_dist, frame,
                frame_width, frame_height, status
            )

        # --- Search mode ---
        elif search_mode and search_target:
            elapsed = time.time() - search_start_time
            if elapsed > 10:
                speak_command_response(
                    f"{search_target} not found in view. Please turn around."
                )
                search_mode = False
                search_target = None
            else:
                matches = [
                    (det, dist) for det, dist in detections_with_dist
                    if det["class_name"] == search_target
                ]
                if matches:
                    det, dist = matches[0]
                    d = get_direction(det["box"], frame_width)
                    msg = (f"{search_target} found, "
                           f"{direction_phrase(d)}, {dist} metres.")
                    speak_command_response(msg)
                    search_mode = False
                    search_target = None

        # --- Normal narration (suppressed during quiet mode) ---
        elif not search_mode and not is_quiet_mode():

            # Proximity alert
            if detections_with_dist:
                closest_det, closest_dist = detections_with_dist[0]
                tier, alert_msg, immediate = alerts.evaluate(
                    closest_dist,
                    object_name=closest_det["class_name"]
                )
                if alert_msg:
                    if immediate:
                        tts.speak_now(alert_msg)
                    else:
                        tts.speak(alert_msg)
                    last_spoken = alert_msg

            # Scene narration
            for det, dist in detections_with_dist:
                direction = get_direction(det["box"], frame_width)
                sentence = describer.process_detection(
                    det["class_name"], direction, dist
                )
                if sentence:
                    tts.speak(sentence)
                    last_spoken = sentence

        # --- Battery check ---
        battery_alert = status.check_and_get_alert()
        if battery_alert:
            tts.speak(battery_alert)

        # --- Visual overlay ---
        mode_label = f"SEARCH: {search_target}" if search_mode else (
            "QUIET" if is_quiet_mode() else "DETECTING"
        )
        cv2.putText(frame, mode_label, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        for det, dist in detections_with_dist:
            box = det["box"]
            x1, y1, x2, y2 = box
            direction = get_direction(box, frame_width)
            label = (f'{det["class_name"]} | '
                     f'{direction_phrase(direction)} | {dist}m')
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, max(y1 - 10, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        cv2.imshow("VISION - Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[main] Quit key pressed.")
            running = False
            break

    asr.stop()
    cam.release()
    cv2.destroyAllWindows()


def crash_supervisor():
    global tts
    print("[supervisor] Initialising TTS engine...")
    tts = SpeechOutput()

    max_restarts = 5
    restart_count = 0

    while restart_count < max_restarts:
        try:
            run_main_loop()
            break
        except KeyboardInterrupt:
            print("\n[supervisor] Shutting down cleanly.")
            tts.speak_now("VISION system shutting down.")
            time.sleep(3)
            break
        except Exception as e:
            restart_count += 1
            print(f"\n[supervisor] CRASH ({restart_count}/{max_restarts}):")
            traceback.print_exc()
            try:
                tts.speak_now("System error. Restarting in 5 seconds.")
            except Exception:
                pass
            time.sleep(5)

    if restart_count >= max_restarts:
        print("[supervisor] Max restarts reached.")
        try:
            tts.speak_now("System failed. Please restart manually.")
            time.sleep(5)
        except Exception:
            pass


if __name__ == "__main__":
    crash_supervisor()
