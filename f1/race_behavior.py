# f1/race_behavior.py

from core.events import EventType


class RaceBehavior:
    """
    Handles race-specific state transitions:
    - race start
    - formation lap
    - lap start
    - sector transitions
    - pit window open
    - pit window sector 3
    - in-lap / out-lap detection
    - race win
    - unsafe conditions (safety override)
    - delta freeze (SC/VSC)
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_lap_number = -1
        self.last_sector = -1
        self.pit_window_open_announced = False
        self.pit_window_sector3_announced = False
        self.race_started = False
        self.formation_lap_announced = False
        self.last_delta_freeze = False
        self.last_position = None

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
        # FORMATION LAP
        # -----------------------------------------------------
        if session.m_sessionType == 10:  # formation lap session
            if not self.formation_lap_announced:
                self._emit(EventType.FORMATION_LAP_START)
                self.formation_lap_announced = True

        # -----------------------------------------------------
        # RACE START
        # -----------------------------------------------------
        if session.m_sessionType == 11:  # race
            if not self.race_started and session.m_totalLaps > 0:
                self._emit(EventType.RACE_START_GRID)
                self.race_started = True

        # -----------------------------------------------------
        # LAP START
        # -----------------------------------------------------
        lap_number = lap_data.m_currentLapNum

        if lap_number != self.last_lap_number:
            self._emit(EventType.LAP_START, lap=lap_number)

        # -----------------------------------------------------
        # LAST 5 LAPS / LAST LAP
        # -----------------------------------------------------
        total_laps = session.m_totalLaps
        laps_remaining = total_laps - lap_number

        if laps_remaining == 5:
            self._emit(EventType.LAST_FIVE_LAPS,
                       position=lap_data.m_carPosition)

        if laps_remaining == 1:
            self._emit(EventType.LAST_LAP,
                       position=lap_data.m_carPosition)

        # -----------------------------------------------------
        # SECTOR AWARENESS
        # -----------------------------------------------------
        sector = lap_data.m_sector  # 0,1,2
        
        # -----------------------------------------------------
        # PIT WINDOW OPEN
        # -----------------------------------------------------
        if hasattr(session, "m_pitWindowStartLap"):
            if (not self.pit_window_open_announced and
                lap_number >= session.m_pitWindowStartLap):
                self._emit(EventType.PIT_WINDOW_OPEN)
                self.pit_window_open_announced = True

        # -----------------------------------------------------
        # PIT WINDOW SECTOR 3 REMINDER
        # -----------------------------------------------------
        if (self.pit_window_open_announced and
            not self.pit_window_sector3_announced and
            sector == 2):
            self._emit(EventType.PIT_WINDOW_SECTOR3)
            self.pit_window_sector3_announced = True

        # -----------------------------------------------------
        # IN-LAP / OUT-LAP DETECTION
        # -----------------------------------------------------
        if lap_data.m_currentLapInvalid:
            pass  # ignore invalid laps for in/out logic

        # Out-lap: lap after pit exit
        if lap_data.m_currentLapNum == status.m_pitExitLap:
            self._emit(EventType.OUT_LAP)

        # In-lap: lap before pit entry
        if lap_data.m_currentLapNum == status.m_pitEntryLap:
            self._emit(EventType.IN_LAP)

        # -----------------------------------------------------
        # DELTA FREEZE (SC/VSC)
        # -----------------------------------------------------
        delta_freeze = bool(getattr(session, "m_isDeltaPositive", False))

        if delta_freeze and not self.last_delta_freeze:
            self._emit(EventType.DELTA_FREEZE_START)

        if not delta_freeze and self.last_delta_freeze:
            self._emit(EventType.DELTA_FREEZE_END)

        # -----------------------------------------------------
        # UNSAFE CONDITIONS (Safety Override)
        # -----------------------------------------------------
        unsafe = (
            status.m_tyresWear[0] > 85 or
            status.m_frontLeftWingDamage > 60 or
            status.m_rearWingDamage > 60 or
            session.m_trackTemperature > 65
        )

        if unsafe:
            self._emit(EventType.SAFETY_OVERRIDE_REQUIRED)

        # -----------------------------------------------------
        # RACE WIN
        # -----------------------------------------------------
        position = lap_data.m_carPosition

        if session.m_sessionTimeLeft == 0 and position == 1:
            self._emit(EventType.RACE_WIN)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_lap_number = lap_number
        self.last_sector = sector
        self.last_delta_freeze = delta_freeze
        self.last_position = position
