# f1/session_manager.py

from core.events import EventType


class SessionManager:
    """
    Detects session-level state transitions:
    - session start / end
    - session type changes (P → Q, Q → R)
    - formation lap
    - safety car / VSC state transitions
    - garage entered / exited (inferred from driver_status)
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_session_type = None
        self.last_session_time_left = None
        self.session_active = False
        self.grid_formed = False
        self.countdown_announced = False
        self.formation_lap_announced = False
        self.formation_sector3_announced = False
        self._last_driver_status = None
        self._in_garage = False

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session):
        """
        session: SessionData
        """
        session_type = session.m_sessionType
        time_left = session.m_sessionTimeLeft

        # Session type names for debug
        type_names = {
            0: "UNKNOWN", 1: "PRACTICE_1", 2: "PRACTICE_2", 3: "PRACTICE_3",
            4: "SHORT_PRACTICE", 5: "QUALIFYING_1", 6: "QUALIFYING_2",
            7: "QUALIFYING_3", 8: "ONE_SHOT_QUALIFYING", 9: "PRACTICE",
            10: "FORMATION_LAP", 11: "RACE", 12: "RACE_2", 13: "TIME_TRIAL",
            15: "WORLD_GRAND_PRIX"
        }
        type_name = type_names.get(session_type, f"UNKNOWN({session_type})")

        # -----------------------------------------------------
        # SESSION START
        # -----------------------------------------------------
        if not self.session_active and time_left > 0:
            # Only emit if participants map is ready
            if getattr(self.telemetry_state, '_participants_ready', False):
                self.session_active = True
                self._emit(EventType.SESSION_START)

        # -----------------------------------------------------
        # SESSION END
        # -----------------------------------------------------
        if self.session_active and time_left == 0:
            self.session_active = False
            self._emit(EventType.SESSION_END)

        # -----------------------------------------------------
        # SESSION TYPE CHANGED (P → Q, Q → R, etc.)
        # -----------------------------------------------------
        if self.last_session_type is not None and session_type != self.last_session_type:
            self._emit(EventType.SESSION_TYPE_CHANGED)

        # -----------------------------------------------------
        # COUNTDOWN (5 seconds before session starts)
        # -----------------------------------------------------
        if time_left == 5 and not self.countdown_announced:
            self.countdown_announced = True

        # -----------------------------------------------------
        # GRID FORMATION (session starting, cars on grid)
        # -----------------------------------------------------
        if (session_type in (5, 6, 7, 10, 11) and
            not self.grid_formed and time_left > 0):
            self.grid_formed = True

        # -----------------------------------------------------
        # FORMATION LAP
        # -----------------------------------------------------
        # Works for both session_type 10 and WGP/race formation detection
        if self.telemetry_state.is_formation_lap:
            if not self.formation_lap_announced:
                print("[SESSION] FORMATION_LAP_START")
                self._emit(EventType.FORMATION_LAP_START)
                self.formation_lap_announced = True

            # Sector 3 of formation lap = "Find your grid slot" (only for session_type 10)
            sector = self.telemetry_state.sector
            session_type = self.telemetry_state.session_type
            if (sector == 2 and 
                session_type == 10 and  # FORMATION_LAP session type only
                not self.formation_sector3_announced):
                print("[SESSION] FORMATION_LAP_SECTOR3")
                self._emit(EventType.FORMATION_LAP_SECTOR3)
                self.formation_sector3_announced = True
        else:
            self.formation_lap_announced = False
            self.formation_sector3_announced = False

        # -----------------------------------------------------
        # GARAGE ENTERED / EXITED (inferred from driver_status)
        # driver_status: 0=garage, 1=flying lap, 2=in lap, 3=out lap, 4=on track
        # -----------------------------------------------------
        driver_status = self.telemetry_state.driver_status
        if driver_status is not None:
            currently_in_garage = (driver_status == 0)

            if currently_in_garage and not self._in_garage:
                print("[SESSION] GARAGE_ENTERED")
                self._emit(EventType.GARAGE_ENTERED)
                self._in_garage = True

            if not currently_in_garage and self._in_garage:
                print("[SESSION] GARAGE_EXITED")
                self._emit(EventType.GARAGE_EXITED)
                self._in_garage = False

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_session_type = session_type
        self.last_session_time_left = time_left
        self._last_driver_status = driver_status
