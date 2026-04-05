# f1/race_behavior.py

from core.events import EventType


class RaceBehavior:
    """
    Handles race-specific state transitions:
    - race start
    - formation lap
    - pit window open / sector 3
    - last 5 laps / last lap
    - race win / race finish
    - unsafe conditions (safety override)
    Emits events to TelemetryState → EventRouter → EngineerBrain.

    Note: LAP_START emitted by TelemetryState._handle_lap_data.
    Note: DELTA_FREEZE emitted by SafetyManager.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_lap_number = -1
        self.last_sector = -1
        self.pit_window_open_announced = False
        self.pit_window_sector3_announced = False
        self.race_started = False
        self.last_position = None
        self._finish_announced = False

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, lap_data, status, telemetry_state=None):
        """
        session: SessionData
        lap_data: LapData for player
        status: CarStatusData for player
        telemetry_state: TelemetryState (optional, for damage data)
        """

        # -----------------------------------------------------
        # RACE START
        # -----------------------------------------------------
        if session.m_sessionType == 11:  # race
            if not self.race_started and session.m_totalLaps > 0:
                self._emit(EventType.RACE_START_GRID)
                self.race_started = True

        # -----------------------------------------------------
        # LAST 5 LAPS / LAST LAP
        # -----------------------------------------------------
        lap_number = lap_data.m_currentLapNum
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
        if (not self.pit_window_open_announced and
                lap_number >= session.m_pitStopWindowIdealLap):
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
        # UNSAFE CONDITIONS (Safety Override)
        # -----------------------------------------------------
        unsafe = False

        if telemetry_state:
            tyre_wear = telemetry_state.car_damage_wear
            if tyre_wear and tyre_wear[0] > 85:
                unsafe = True

            dmg = getattr(telemetry_state, 'car_damage', None)
            if dmg:
                try:
                    pd = dmg.get_player_damage()
                    if pd.m_frontLeftWingDamage > 60 or pd.m_rearWingDamage > 60:
                        unsafe = True
                except Exception:
                    pass

        if session.m_trackTemperature > 65:
            unsafe = True

        if unsafe:
            self._emit(EventType.SAFETY_OVERRIDE_REQUIRED)

        # -----------------------------------------------------
        # RACE FINISH DETECTION
        # -----------------------------------------------------
        if session.m_sessionType == 11 and not self._finish_announced:
            if session.m_sessionTimeLeft == 0:
                fc = self.telemetry_state.get_player_final_classification()
                if fc:
                    self._finish_announced = True
                    if fc.m_resultStatus == 3:  # FINISHED
                        if fc.m_position == 1:
                            self._emit(EventType.RACE_WIN)
                        self._emit(EventType.RACE_FINISH,
                                   position=fc.m_position,
                                   points=fc.m_points)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_lap_number = lap_number
        self.last_sector = sector
        self.last_position = lap_data.m_carPosition
