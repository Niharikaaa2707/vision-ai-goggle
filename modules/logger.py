# modules/logger.py
import sys, os, datetime, threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class Logger:
    def __init__(self):
        os.makedirs(config.LOG_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_path = os.path.join(config.LOG_DIR, f"vision_{ts}.log")
        self._lock = threading.Lock()
        self._log("SYSTEM", "VISION system started.")
        print(f"[Logger] Logging to {self._log_path}")

    def _log(self, category, message):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{category}] {message}"
        with self._lock:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    def log_detection(self, class_name, direction, distance):
        self._log("DETECTION", f"{class_name} | {direction} | {distance}m")
    def log_tts(self, text):
        self._log("SPOKEN", text)
    def log_asr(self, text):
        self._log("HEARD", text)
    def log_command(self, intent, target=None):
        self._log("COMMAND", f"intent={intent}" + (f" target={target}" if target else ""))
    def log_alert(self, tier, message):
        self._log("ALERT", f"[{tier.upper()}] {message}")
    def log_system(self, message):
        self._log("SYSTEM", message)
    def log_error(self, message):
        self._log("ERROR", message)

_logger = None
def get_logger():
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger

if __name__ == "__main__":
    log = Logger()
    log.log_system("Test started")
    log.log_detection("person", "centre", 2.5)
    log.log_tts("Person ahead, 2.5 metres")
    log.log_asr("find bottle")
    log.log_command("find", "bottle")
    log.log_alert("warning", "Obstacle very close")
    log.log_system("Test complete")
    print("Log written. Check logs/ folder.")
