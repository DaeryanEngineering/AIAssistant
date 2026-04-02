# f1/pit_behavior.py

from core.events import EventType


class PitBehavior:
    """
    Handles pit-stop related state transitions:
    - pit entry line crossed
    - pit lane active
    - pit box approach
    - pit box stop
    - pit service start/end
    - pit exit line crossed
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_in_pit_lane = False
        self.last_pit_mode = 0
        self.last_pit_service = False
        self.last_pit_release = False

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
        in_pit_lane = bool(lap_data.m_pitLaneTimerInMS > 0)

        if in_pit_lane and not self.last_in_pit_lane:
            self._emit(EventType.PIT_LANE_ENTERED)

        if not in_pit_lane and self.last_in_pit_lane:
            self._emit(EventType.PIT_LANE_EXITED)

        # -----------------------------------------------------
        # PIT MODE (Codemasters enum)
        # 0 = none
        # 1 = pit entry
        # 2 = pit exit
        # -----------------------------------------------------
        pit_mode = getattr(status, "m_pitMode", 0)

        if pit_mode == 1 and self.last_pit_mode != 1:
            self._emit(EventType.PIT_ENTRY_LINE)

        if pit_mode == 2 and self.last_pit_mode != 2:
            self._emit(EventType.PIT_EXIT_LINE)

        # -----------------------------------------------------
        # PIT SERVICE (car stopped in box)
        # -----------------------------------------------------
        pit_service = bool(status.m_pitLimiterOn and in_pit_lane and lap_data.m_carPosition == 0)

        if pit_service and not self.last_pit_service:
            self._emit(EventType.PIT_SERVICE_START)

        if not pit_service and self.last_pit_service:
            self._emit(EventType.PIT_SERVICE_END)

        # -----------------------------------------------------
        # PIT RELEASE (car being dropped from jacks)
        # -----------------------------------------------------
        pit_release = bool(getattr(status, "m_pitReleaseAllowed", False))

        if pit_release and not self.last_pit_release:
            self._emit(EventType.PIT_RELEASE)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_in_pit_lane = in_pit_lane
        self.last_pit_mode = pit_mode
        self.last_pit_service = pit_service
        self.last_pit_release = pit_release
