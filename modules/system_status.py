# modules/system_status.py
# Monitors laptop battery status (stand-in for the board's 5V rail monitor).
# On real hardware, this hook would be replaced with actual battery telemetry
# from the board, but the interface (check_battery / should_alert) stays the same.

import psutil
import time


class SystemStatus:
    def __init__(self, low_threshold=15, critical_threshold=5, check_interval_seconds=60):
        """
        low_threshold: % battery at which to give a "low battery" warning
        critical_threshold: % battery at which to give a more urgent alert
        check_interval_seconds: how often to actually check (avoid checking every frame)
        """
        self.low_threshold = low_threshold
        self.critical_threshold = critical_threshold
        self.check_interval = check_interval_seconds

        self._last_check_time = 0
        self._low_alert_given = False
        self._critical_alert_given = False

    def get_battery_info(self):
        """
        Returns (percent, plugged_in) or (None, None) if no battery detected
        (e.g. desktop PC, or info unavailable).
        """
        battery = psutil.sensors_battery()
        if battery is None:
            return None, None
        return battery.percent, battery.power_plugged

    def check_and_get_alert(self):
        """
        Call this periodically (e.g. once per main loop iteration).
        Internally throttles actual checks to check_interval_seconds.

        Returns a string alert message if an alert should be spoken now,
        otherwise None.
        """
        now = time.time()
        if now - self._last_check_time < self.check_interval:
            return None

        self._last_check_time = now
        percent, plugged_in = self.get_battery_info()

        if percent is None:
            return None  # no battery info available (e.g. desktop)

        if plugged_in:
            # reset alert flags once charging resumes
            self._low_alert_given = False
            self._critical_alert_given = False
            return None

        if percent <= self.critical_threshold and not self._critical_alert_given:
            self._critical_alert_given = True
            return f"Battery critical, {percent} percent remaining. Please charge immediately."

        if percent <= self.low_threshold and not self._low_alert_given:
            self._low_alert_given = True
            return f"Battery low, {percent} percent remaining. Please charge soon."

        return None


# ---------- Standalone test ----------
if __name__ == "__main__":
    status = SystemStatus(low_threshold=95, critical_threshold=2, check_interval_seconds=0)
    # low_threshold set artificially high here just to demo triggering on most laptops

    percent, plugged = status.get_battery_info()
    print(f"Battery: {percent}% | Plugged in: {plugged}")

    alert = status.check_and_get_alert()
    print(f"Alert: {alert}")
