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

        # -----------------------------------------------------
        # SESSION START
        # -----------------------------------------------------
        if not self.session_active and time_left > 0:
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
        if session_type == 10:
            if not self.formation_lap_announced:
                self._emit(EventType.FORMATION_LAP_START)
                self.formation_lap_announced = True

        # -----------------------------------------------------
        # GARAGE ENTERED / EXITED (inferred from driver_status)
        # driver_status: 0=garage, 1=flying lap, 2=in lap, 3=out lap, 4=on track
        # -----------------------------------------------------
        driver_status = self.telemetry_state.driver_status
        if driver_status is not None:
            currently_in_garage = (driver_status == 0)

            if currently_in_garage and not self._in_garage:
                self._emit(EventType.GARAGE_ENTERED)
                self._in_garage = True

            if not currently_in_garage and self._in_garage:
                self._emit(EventType.GARAGE_EXITED)
                self._in_garage = False

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_session_type = session_type
        self.last_session_time_left = time_left
        self._last_driver_status = driver_status
