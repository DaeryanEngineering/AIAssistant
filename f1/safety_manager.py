# f1/safety_manager.py

from core.events import EventType


class SafetyManager:
    """
    Sole emitter for safety car / VSC / red flag events.
    Other managers update state but do NOT emit these events.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state
        self._prev_sc_status = 0
        self._prev_red_flag = False

    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    def update(self, session):
        """
        session: SessionData
        """
        sc_status = getattr(session, 'm_safetyCarStatus', 0)

        # -----------------------------------------------------
        # SAFETY CAR DEPLOYED
        # -----------------------------------------------------
        if sc_status == 1 and self._prev_sc_status != 1:
            self._emit(EventType.SAFETY_CAR_DEPLOYED)

        # -----------------------------------------------------
        # SAFETY CAR IN THIS LAP (rolling restart)
        # -----------------------------------------------------
        if sc_status == 3 and self._prev_sc_status == 1:
            self._emit(EventType.SAFETY_CAR_IN_THIS_LAP)

        # -----------------------------------------------------
        # VSC DEPLOYED
        # -----------------------------------------------------
        if sc_status == 2 and self._prev_sc_status != 2:
            self._emit(EventType.VIRTUAL_SAFETY_CAR_DEPLOYED)

        # -----------------------------------------------------
        # VSC ENDING
        # -----------------------------------------------------
        if self._prev_sc_status == 2 and sc_status == 0:
            self._emit(EventType.VSC_END)

        # -----------------------------------------------------
        # SAFETY CAR END (green flag)
        # -----------------------------------------------------
        if self._prev_sc_status == 1 and sc_status == 0:
            self._emit(EventType.SAFETY_CAR_END)

        # -----------------------------------------------------
        # RED FLAG
        # -----------------------------------------------------
        event_code = getattr(session, 'm_sessionType', 0)
        # Red flag is typically detected via event packet or session state
        # For now, check if session time left is 0 unexpectedly
        if session.m_sessionTimeLeft == 0 and session.m_totalLaps > 0:
            if not self._prev_red_flag:
                # Could be red flag or race end — handled by RaceBehavior for race end
                pass

        self._prev_sc_status = sc_status
