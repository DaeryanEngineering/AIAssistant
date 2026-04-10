# f1/ontrack_manager.py

from core.events import EventType


class OnTrackManager:
    """
    Detects on-track state transitions:
    - leaving garage
    - entering track
    - pit entry / pit exit
    - pit limiter (voice-only)
    - out lap / flying lap / in lap
    - invalid lap
    - yellow flags
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_on_track = False
        self.last_pit_limiter = False   # voice-only
        self.last_pit_mode = 0
        self.last_lap_invalid = False
        self.last_yellow_flag = 0

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, lap_data, status):
        """
        session: SessionData
        lap_data: LapData for player
        status: CarStatusData for player
        """

        # -----------------------------------------------------
        # ON TRACK / OFF TRACK
        # -----------------------------------------------------
        if lap_data is None:
            return
        on_track = lap_data.m_carPosition > 0  # placeholder logic

        if on_track and not self.last_on_track:
            self._emit(EventType.ON_TRACK_ENTERED)

        if not on_track and self.last_on_track:
            self._emit(EventType.ON_TRACK_EXITED)

        if status is None:
            return

        if session is None:
            return

        # -----------------------------------------------------
        # PIT LIMITER (VOICE ONLY)
        # -----------------------------------------------------
        pit_limiter = bool(status.m_pitLimiterStatus == 1)

        if pit_limiter and not self.last_pit_limiter:
            # purely for radio lines
            self._emit(EventType.PIT_LIMITER_ON)

        if not pit_limiter and self.last_pit_limiter:
            # purely for radio lines
            self._emit(EventType.PIT_LIMITER_OFF)

        # -----------------------------------------------------
        # PIT ENTRY / PIT EXIT
        # -----------------------------------------------------
        pit_mode = getattr(status, "m_pitMode", 0)

        # 1 = pit entry
        if pit_mode == 1 and self.last_pit_mode != 1:
            self._emit(EventType.PIT_ENTRY)

        # 2 = pit exit
        if pit_mode == 2 and self.last_pit_mode != 2:
            self._emit(EventType.PIT_EXIT)

        # -----------------------------------------------------
        # INVALID LAP
        # -----------------------------------------------------
        invalid = bool(lap_data.m_currentLapInvalid)

        if invalid and not self.last_lap_invalid:
            self._emit(EventType.LAP_INVALIDATED)

        # -----------------------------------------------------
        # YELLOW FLAGS
        # -----------------------------------------------------
        yellow_flag = getattr(session, "m_safetyCarStatus", 0)

        if yellow_flag != self.last_yellow_flag:
            if yellow_flag == 0:
                self._emit(EventType.TRACK_GREEN)
            elif yellow_flag == 1:
                self._emit(EventType.TRACK_YELLOW)
            elif yellow_flag == 2:
                self._emit(EventType.TRACK_DOUBLE_YELLOW)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_on_track = on_track
        self.last_pit_limiter = pit_limiter
        self.last_pit_mode = pit_mode
        self.last_lap_invalid = invalid
        self.last_yellow_flag = yellow_flag
