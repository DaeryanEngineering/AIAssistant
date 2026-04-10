# f1/pit_behavior.py

import time
from core.events import EventType


class PitBehavior:
    """
    Handles pit-stop related state transitions:
    - pit lane entered/exited
    - pit entry/exit line crossed
    - pit service start/end
    - pit limiter reminder (speed > 40, pit mode == 1, limiter not on)
    - pit stop quality (good/acceptable/slow based on duration)
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_in_pit_lane = False
        self.last_pit_mode = 0
        self.last_pit_service = False
        self.last_pit_release = False
        self._limiter_reminder_done = False
        self._pit_entry_time = None

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, lap_data, status):
        """
        lap_data: LapData for player
        status: CarStatusData for player
        """

        # -----------------------------------------------------
        # PIT LANE DETECTION
        # -----------------------------------------------------
        if lap_data is None:
            return
        in_pit_lane = bool(lap_data.m_pitLaneTimeInLaneInMS > 0)

        if in_pit_lane and not self.last_in_pit_lane:
            self._pit_entry_time = time.monotonic()
            self._emit(EventType.PIT_LANE_ENTERED)

        if not in_pit_lane and self.last_in_pit_lane:
            # Calculate pit stop duration
            if self._pit_entry_time is not None:
                duration = time.monotonic() - self._pit_entry_time
                if duration < 3.0:
                    quality = "good"
                elif duration < 4.5:
                    quality = "acceptable"
                else:
                    quality = "slow"
                self._emit(EventType.PIT_STOP_QUALITY, quality=quality, duration=duration)
                self._pit_entry_time = None

            self._emit(EventType.PIT_LANE_EXITED)
            # Reset limiter reminder for next pit entry
            self._limiter_reminder_done = False

        # -----------------------------------------------------
        # PIT MODE (Codemasters enum)
        # 0 = none, 1 = pit entry, 2 = pit exit
        # -----------------------------------------------------
        pit_mode = getattr(status, "m_pitMode", 0)

        if pit_mode == 1 and self.last_pit_mode != 1:
            self._emit(EventType.PIT_ENTRY_LINE)

        if pit_mode == 2 and self.last_pit_mode != 2:
            self._emit(EventType.PIT_EXIT_LINE)

        if status is None:
            return

        # -----------------------------------------------------
        # PIT LIMITER REMINDER
        # Fires when: pit_mode == 1 AND speed > 40 AND limiter not on
        # Armed once per pit entry, resets when pit_mode returns to 0
        # -----------------------------------------------------
        pit_limiter = status.m_pitLimiterStatus == 1
        speed = self.telemetry_state.speed or 0

        if pit_mode == 1 and speed > 40 and not pit_limiter and not self._limiter_reminder_done:
            self._emit(EventType.PIT_LIMITER_REMINDER)
            self._limiter_reminder_done = True

        if pit_mode == 0:
            self._limiter_reminder_done = False

        # -----------------------------------------------------
        # PIT SERVICE (car stopped in box)
        # -----------------------------------------------------
        pit_service = bool(pit_limiter and in_pit_lane and lap_data.m_carPosition == 0)

        if pit_service and not self.last_pit_service:
            self._emit(EventType.PIT_SERVICE_START)

        if not pit_service and self.last_pit_service:
            self._emit(EventType.PIT_SERVICE_END)

        # -----------------------------------------------------
        # PIT RELEASE
        # -----------------------------------------------------
        pit_release = self.telemetry_state.pit_release_allowed

        if pit_release and not self.last_pit_release:
            self._emit(EventType.PIT_RELEASE)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_in_pit_lane = in_pit_lane
        self.last_pit_mode = pit_mode
        self.last_pit_service = pit_service
        self.last_pit_release = pit_release
