# f1/safety_manager.py

from core.events import EventType


class SafetyManager:
    """
    Handles detection of Safety Car, Virtual Safety Car, Red Flags,
    and restart conditions. Emits events to TelemetryState, which
    forwards them to the EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state to detect transitions
        self.last_sc_status = 0          # 0 = none, 1 = SC, 2 = VSC
        self.last_red_flag = False
        self.last_restart_ready = False

    # ---------------------------------------------------------
    # Internal helper to emit events cleanly
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # Called once per telemetry tick with the decoded session data
    # ---------------------------------------------------------
    def update(self, session):
        """
        session: object containing F1 23/24/25 session data
        Must include:
            - session.m_safetyCarStatus (0,1,2)
            - session.m_redFlag (bool or int)
            - session.m_restartReady (bool or int)
        """

        sc_status = getattr(session, "m_safetyCarStatus", 0)
        red_flag = bool(getattr(session, "m_redFlag", False))
        restart_ready = bool(getattr(session, "m_restartReady", False))

        # -----------------------------------------------------
        # SAFETY CAR DEPLOYED
        # -----------------------------------------------------
        if sc_status == 1 and self.last_sc_status != 1:
            self._emit(EventType.SAFETY_CAR_DEPLOYED)

        # -----------------------------------------------------
        # SAFETY CAR IN THIS LAP (rolling restart)
        # -----------------------------------------------------
        # Many games expose this as a flag or via delta behavior.
        # Replace this placeholder with your real detection logic.
        if self._detect_sc_in_this_lap(session):
            self._emit(EventType.SAFETY_CAR_IN_THIS_LAP)

        # -----------------------------------------------------
        # VIRTUAL SAFETY CAR DEPLOYED
        # -----------------------------------------------------
        if sc_status == 2 and self.last_sc_status != 2:
            self._emit(EventType.VIRTUAL_SAFETY_CAR_DEPLOYED)

        # -----------------------------------------------------
        # VSC ENDING
        # -----------------------------------------------------
        # Replace this with your real detection logic.
        if self._detect_vsc_ending(session):
            self._emit(EventType.VSC_ENDING)

        # -----------------------------------------------------
        # RED FLAG
        # -----------------------------------------------------
        if red_flag and not self.last_red_flag:
            self._emit(EventType.RED_FLAG)

        # -----------------------------------------------------
        # RESTART GRID READY (after red flag)
        # -----------------------------------------------------
        if restart_ready and not self.last_restart_ready:
            self._emit(EventType.RESTART_GRID_READY)

        # -----------------------------------------------------
        # Update cached state
        # -----------------------------------------------------
        self.last_sc_status = sc_status
        self.last_red_flag = red_flag
        self.last_restart_ready = restart_ready

    # ---------------------------------------------------------
    # Placeholder detection helpers
    # Replace these with your real logic
    # ---------------------------------------------------------

    def _detect_sc_in_this_lap(self, session):
        """
        Detect 'Safety Car in this lap'.
        Replace with your real logic (e.g., packet flag, delta behavior).
        """
        return False

    def _detect_vsc_ending(self, session):
        """
        Detect 'VSC ending'.
        Replace with your real logic (e.g., countdown flag).
        """
        return False
