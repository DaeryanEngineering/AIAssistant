# mode_manager.py

from enum import Enum, auto
import psutil

class SaulMode(Enum):
    AI = auto()          # F1 not running
    F1 = auto()          # F1 running, but not on track
    ENGINEER = auto()    # On track
    PAUSED = auto()      # Game paused

class ModeManager:
    def __init__(self, telemetry_state, on_mode_change=None):
        self.telemetry = telemetry_state
        self.current_mode = SaulMode.AI
        self.on_mode_change = on_mode_change  # callback for SaulBrain
        self._last_session_time = None
        self._pause_detected = False

    # ---------------------------------------------------------
    # PROCESS CHECK
    # ---------------------------------------------------------
    def _is_f1_running(self):
        F1_NAMES = {"f1", "F1", "f12025", "F12025", "f124", "F124", "f123", "F123"}
        for proc in psutil.process_iter(['name']):
            name = proc.info.get('name') or ''
            if any(n in name for n in F1_NAMES):
                return True
        return False

    # ---------------------------------------------------------
    # PAUSE DETECTION
    # ---------------------------------------------------------
    def _is_game_paused(self):
        """
        Detect pause by checking if sessionTimeLeft stops changing.
        """
        session_time = self.telemetry.session_time_left

        # No telemetry yet — can't determine pause state
        if session_time is None:
            return False

        if self._last_session_time is None:
            self._last_session_time = session_time
            return False

        # If time hasn't changed for 0.5 seconds → paused
        paused = (session_time == self._last_session_time)
        self._last_session_time = session_time

        return paused

    # ---------------------------------------------------------
    # TRACK DETECTION
    # ---------------------------------------------------------
    def _is_on_track(self):
        """
        Detect if the player is physically on track.
        """
        ds = self.telemetry.driver_status
        ps = self.telemetry.pit_status
        speed = self.telemetry.speed

        # DriverStatus meanings:
        # 0 = In garage
        # 1 = Flying lap
        # 2 = In lap
        # 3 = Out lap
        # 4 = On track
        # 5 = Not on track

        if ds in [1, 2, 3, 4]:
            return True

        # PitStatus:
        # 0 = None (on track)
        # 1 = Pitting
        # 2 = In pit lane
        if ps is not None and ps == 0:
            return True

        # Movement fallback
        if speed is not None and speed > 1:
            return True

        return False

    # ---------------------------------------------------------
    # GARAGE DETECTION
    # ---------------------------------------------------------
    def _is_in_garage(self):
        ds = self.telemetry.driver_status
        ps = self.telemetry.pit_status
        speed = self.telemetry.speed

        if ds == 0:
            return True

        if ps == 2 and speed is not None and speed == 0:
            return True

        return False

    # ---------------------------------------------------------
    # MODE UPDATE LOOP
    # ---------------------------------------------------------
    def update(self):
        """
        Call this every frame / tick.
        """
        # 1. F1 not running → AI Mode
        if not self._is_f1_running():
            self._set_mode(SaulMode.AI)
            return

        # 2. On track → Engineer Mode
        if self._is_on_track():
            self._set_mode(SaulMode.ENGINEER)
            return

        # 3. Detect pause
        if self._is_game_paused():
            self._set_mode(SaulMode.PAUSED)
            return

        # 4. In garage → F1 Mode
        if self._is_in_garage():
            self._set_mode(SaulMode.F1)
            return

        # Fallback
        self._set_mode(SaulMode.AI)

    # ---------------------------------------------------------
    # MODE SETTER
    # ---------------------------------------------------------
    def _set_mode(self, new_mode):
        if new_mode != self.current_mode:
            old = self.current_mode
            self.current_mode = new_mode
            print(f"[Mode] {old.name} -> {new_mode.name}")
            if self.on_mode_change:
                self.on_mode_change(new_mode)
