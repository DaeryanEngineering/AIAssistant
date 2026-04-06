# core/keyboard_controller.py

import time
import threading


class KeyboardController:
    """
    Keyboard simulation wrapper for F1 25 input.
    Uses pydirectinput for game-compatible key presses.
    All key presses have 150ms delays for reliability.
    """

    # Key bindings
    KEYS = {
        "drs": "f9",
        "ers_overtake": "f10",
        "ers_cycle_left": "f11",
        "ers_cycle_right": "f8",
        "mfd_up": "num8",
        "mfd_down": "num2",
        "mfd_left": "num4",
        "mfd_right": "num6",
        "mfd_confirm": "enter",
        "mfd_open": "num0",
    }

    PRESS_DELAY = 0.15  # 150ms between presses
    HOLD_DURATION = 0.1  # 100ms key hold

    def __init__(self):
        self._current_ers_mode = 0  # 0=None, 1=Medium, 2=Hotlap, 3=Overtake
        self._lock = threading.Lock()
        self._pydirectinput = None
        self._initialized = False

    def _init(self):
        if not self._initialized:
            import pydirectinput
            self._pydirectinput = pydirectinput
            self._pydirectinput.FAILSAFE = False
            self._initialized = True

    def _press(self, key):
        """Press and release a single key."""
        self._init()
        if self._pydirectinput:
            self._pydirectinput.press(key)
            time.sleep(self.PRESS_DELAY)

    def _hold(self, key, duration=None):
        """Hold a key for a duration."""
        self._init()
        if self._pydirectinput:
            dur = duration or self.HOLD_DURATION
            self._pydirectinput.keyDown(key)
            time.sleep(dur)
            self._pydirectinput.keyUp(key)
            time.sleep(self.PRESS_DELAY)

    # ---------------------------------------------------------
    # DRS
    # ---------------------------------------------------------

    def press_drs(self):
        """Activate DRS via F9."""
        with self._lock:
            self._hold(self.KEYS["drs"])

    # ---------------------------------------------------------
    # ERS
    # ---------------------------------------------------------

    def press_ers_overtake(self):
        """Activate ERS Overtake mode via F10."""
        with self._lock:
            self._hold(self.KEYS["ers_overtake"])
            self._current_ers_mode = 3

    def cycle_ers_to(self, target_mode):
        """
        Cycle ERS mode using D-Pad Left/Right.
        Modes: 0=None, 1=Medium, 2=Hotlap, 3=Overtake
        Calculates shortest path around the ring.
        """
        with self._lock:
            current = self._current_ers_mode
            if current == target_mode:
                return

            # Calculate shortest path (4 modes in a ring)
            diff = (target_mode - current) % 4
            if diff <= 2:
                # Cycle right
                for _ in range(diff):
                    self._press(self.KEYS["ers_cycle_right"])
            else:
                # Cycle left (shorter)
                for _ in range(4 - diff):
                    self._press(self.KEYS["ers_cycle_left"])

            self._current_ers_mode = target_mode

    # ---------------------------------------------------------
    # MFD Navigation
    # ---------------------------------------------------------

    def open_mfd(self):
        """Open MFD menu via Numpad 0."""
        with self._lock:
            self._press(self.KEYS["mfd_open"])

    def mfd_up(self):
        with self._lock:
            self._press(self.KEYS["mfd_up"])

    def mfd_down(self):
        with self._lock:
            self._press(self.KEYS["mfd_down"])

    def mfd_left(self):
        with self._lock:
            self._press(self.KEYS["mfd_left"])

    def mfd_right(self):
        with self._lock:
            self._press(self.KEYS["mfd_right"])

    def mfd_confirm(self):
        """Confirm MFD selection via Enter."""
        with self._lock:
            self._press(self.KEYS["mfd_confirm"])

    def navigate_to_compound(self, target_compound_index):
        """
        Navigate MFD to select a tire compound.
        Compound order in MFD: Soft(0) → Medium(1) → Hard(2) → Inter(3) → Wet(4)
        Assumes MFD pit panel is already open.
        """
        with self._lock:
            # Default to position 0 (leftmost), navigate right to target
            for _ in range(target_compound_index):
                self._press(self.KEYS["mfd_right"])

    def select_pit_compound(self, target_compound_index, prefer_new=True):
        """
        Full MFD flow to select a tire compound for pit stop.
        1. Open MFD
        2. Navigate to pit panel
        3. Select compound
        4. Confirm
        """
        with self._lock:
            # Open MFD
            self._press(self.KEYS["mfd_open"])
            time.sleep(0.3)

            # Navigate to pit panel (typically 2-3 downs from default)
            for _ in range(3):
                self._press(self.KEYS["mfd_down"])
            time.sleep(0.3)

            # Select compound
            self.navigate_to_compound(target_compound_index)
            time.sleep(0.2)

            # Confirm
            self._press(self.KEYS["mfd_confirm"])

    @property
    def current_ers_mode(self):
        return self._current_ers_mode

    def stop_ers(self):
        """
        Cycle ERS to None (mode 0) by pressing F11 repeatedly.
        """
        with self._lock:
            while self._current_ers_mode != 0:
                self._press(self.KEYS["ers_cycle_left"])
