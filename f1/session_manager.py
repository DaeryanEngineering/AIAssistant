# f1/session_manager.py

from core.events import EventType


class SessionManager:
    """
    Handles session-level transitions and metadata:
    - session start
    - session end
    - session type changes (P/Q/R)
    - formation lap detection
    - grid formation
    - race countdown
    - safety car session transitions
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
            self._emit(EventType.SESSION_START,
                       session_type=session_type)
            self.session_active = True

        # -----------------------------------------------------
        # SESSION END
        # -----------------------------------------------------
        if self.session_active and time_left == 0:
            self._emit(EventType.SESSION_END,
                       session_type=session_type)
            self.session_active = False

        # -----------------------------------------------------
        # SESSION TYPE CHANGE (P → Q → R)
        # -----------------------------------------------------
        if self.last_session_type is not None:
            if session_type != self.last_session_type:
                self._emit(EventType.SESSION_TYPE_CHANGED,
                           old=self.last_session_type,
                           new=session_type)

        # -----------------------------------------------------
        # FORMATION LAP DETECTION
        # -----------------------------------------------------
        if session_type == 10 and not self.formation_lap_announced:
            self._emit(EventType.FORMATION_LAP_START)
            self.formation_lap_announced = True

        # -----------------------------------------------------
        # GRID FORMATION (pre-race)
        # -----------------------------------------------------
        if session_type == 11:  # race
            if not self.grid_formed and time_left > 0:
                # Grid is formed when session is race and countdown hasn't started
                self._emit(EventType.GRID_FORMATION)
                self.grid_formed = True

        # -----------------------------------------------------
        # RACE COUNTDOWN (lights sequence)
        # -----------------------------------------------------
        if session_type == 11 and not self.countdown_announced:
            # Countdown begins when session time starts decreasing
            if (self.last_session_time_left is not None and
                time_left < self.last_session_time_left):
                self._emit(EventType.RACE_COUNTDOWN)
                self.countdown_announced = True

        # -----------------------------------------------------
        # SAFETY CAR SESSION TRANSITIONS
        # -----------------------------------------------------
        sc_status = session.m_safetyCarStatus  # 0=none,1=SC,2=VSC,3=Formation

        if sc_status == 1:
            self._emit(EventType.SAFETY_CAR_DEPLOYED)

        elif sc_status == 2:
            self._emit(EventType.VSC_DEPLOYED)

        elif sc_status == 0:
            # Only emit if previously in SC/VSC
            if self.last_session_type == 1:
                self._emit(EventType.SAFETY_CAR_END)
            if self.last_session_type == 2:
                self._emit(EventType.VSC_END)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_session_type = session_type
        self.last_session_time_left = time_left
