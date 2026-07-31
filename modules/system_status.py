# modules/system_status.py
# Monitors laptop battery and CPU status.
# On real hardware, this would be replaced with board telemetry.

import psutil
import time

class SystemStatus:
    def __init__(self, low_threshold=15, critical_threshold=5,
                 check_interval_seconds=60):
        self.low_threshold = low_threshold
        self.critical_threshold = critical_threshold
        self.check_interval = check_interval_seconds
        self._last_check_time = 0
        self._low_alert_given = False
        self._critical_alert_given = False

    def get_battery_info(self):
        battery = psutil.sensors_battery()
        if battery is None:
            return None, None
        return battery.percent, battery.power_plugged

    def get_cpu_usage(self):
        """Returns current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)

    def get_ram_usage(self):
        """Returns current RAM usage percentage."""
        mem = psutil.virtual_memory()
        return round(mem.percent, 1)

    def get_status_dict(self):
        """Returns full system status as dict for dashboard."""
        percent, plugged = self.get_battery_info()
        return {
            "battery": round(percent, 1) if percent else None,
            "plugged": plugged,
            "cpu": self.get_cpu_usage(),
            "ram": self.get_ram_usage()
        }

    def check_and_get_alert(self):
        now = time.time()
        if now - self._last_check_time < self.check_interval:
            return None
        self._last_check_time = now
        percent, plugged_in = self.get_battery_info()
        if percent is None:
            return None
        if plugged_in:
            self._low_alert_given = False
            self._critical_alert_given = False
            return None
        if percent <= self.critical_threshold and not self._critical_alert_given:
            self._critical_alert_given = True
            return (f"Battery critical, {int(percent)} percent remaining. "
                    f"Please charge immediately.")
        if percent <= self.low_threshold and not self._low_alert_given:
            self._low_alert_given = True
            return (f"Battery low, {int(percent)} percent remaining. "
                    f"Please charge soon.")
        return None

# ---------- Standalone test ----------
if __name__ == "__main__":
    status = SystemStatus(low_threshold=95, critical_threshold=2,
                          check_interval_seconds=0)
    percent, plugged = status.get_battery_info()
    print(f"Battery: {percent}% | Plugged in: {plugged}")
    print(f"CPU: {status.get_cpu_usage()}%")
    print(f"RAM: {status.get_ram_usage()}%")
    print(f"Status dict: {status.get_status_dict()}")
    alert = status.check_and_get_alert()
    print(f"Alert: {alert}")