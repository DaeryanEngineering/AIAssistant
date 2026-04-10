# f1/qualifying_behavior.py

from core.events import EventType


class QualifyingBehavior:
    """
    Handles qualifying-specific state transitions:
    - session goal (once)
    - flying lap start
    - flying lap end (valid/invalid)
    - position updates after valid laps
    - position loss while in garage
    - provisional pole
    - final pole
    - should we go back out?
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.goal_announced = False
        self.last_lap_number = -1
        self.last_position = None
        self.last_lap_valid = True
        self.last_session_time_left = None
        self.last_in_garage = False
        self.last_session_type = None

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, lap_data, ui_state):
        """
        session: SessionData
        lap_data: LapData for player
        ui_state: contains in_garage flag
        """

        # Skip qualifying behavior for race sessions (including WGP)
        if session.m_sessionType in (11, 15):
            return

        # -----------------------------------------------------
        # QUALIFYING SESSION GOAL (once per session)
        # -----------------------------------------------------
        if not self.goal_announced:
            if session.m_sessionType in (5, 6, 7):  # Q1/Q2/Q3
                self._emit(EventType.QUALI_GOAL)
                self.goal_announced = True

        # -----------------------------------------------------
        # LAP START
        # -----------------------------------------------------
        if lap_data is None:
            return
        lap_number = lap_data.m_currentLapNum

        if lap_number != self.last_lap_number:
            self._emit(EventType.QUALI_LAP_START, lap=lap_number)

        # -----------------------------------------------------
        # LAP END (valid or invalid)
        # -----------------------------------------------------
        lap_valid = not bool(lap_data.m_currentLapInvalid)
        position = lap_data.m_carPosition

        # Lap just finished
        if lap_number != self.last_lap_number and self.last_lap_number != -1:

            if lap_valid:
                self._emit(EventType.QUALI_LAP_COMPLETE_VALID,
                           lap=self.last_lap_number,
                           position=position)
            else:
                self._emit(EventType.QUALI_LAP_COMPLETE_INVALID,
                           lap=self.last_lap_number)

        # -----------------------------------------------------
        # POSITION UPDATE (only after valid laps)
        # -----------------------------------------------------

        if lap_valid:
            if self.last_position is None or position != self.last_position:
                self._emit(EventType.QUALI_POSITION_UPDATE,
                           position=position)

        # -----------------------------------------------------
        # POSITION LOSS WHILE IN GARAGE
        # -----------------------------------------------------
        in_garage = ui_state.in_garage

        if in_garage and self.last_position is not None:
            if position > self.last_position:  # worse position
                self._emit(EventType.QUALI_POSITION_LOST,
                           old_pos=self.last_position,
                           new_pos=position)

                # Should we go back out?
                if self._should_go_back_out(session, position):
                    self._emit(EventType.QUALI_RECOMMEND_GO_BACK_OUT,
                               position=position)

        # -----------------------------------------------------
        # PROVISIONAL POLE
        # -----------------------------------------------------
        if lap_valid and position == 1:
            # Only if session still running
            if session.m_sessionTimeLeft > 0:
                self._emit(EventType.QUALI_PROVISIONAL_POLE)

        # -----------------------------------------------------
        # FINAL POLE (session ended)
        # -----------------------------------------------------
        if session.m_sessionTimeLeft == 0 and position == 1:
            self._emit(EventType.QUALI_FINAL_POLE)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_lap_number = lap_number
        self.last_position = position
        self.last_lap_valid = lap_valid
        self.last_session_type = session.m_sessionType
        self.last_session_time_left = session.m_sessionTimeLeft
        self.last_in_garage = in_garage

    # ---------------------------------------------------------
    # Should we go back out? (cutoff logic)
    # ---------------------------------------------------------
    def _should_go_back_out(self, session, position):
        """
        Returns True if:
        - position is outside cutoff
        - enough time remains for out-lap + flying lap
        """

        # Determine cutoff based on session type
        if session.m_sessionType == 5:      # Q1
            cutoff = 16
        elif session.m_sessionType == 6:    # Q2
            cutoff = 10
        elif session.m_sessionType == 7:    # Q3
            cutoff = 1
        else:
            return False

        # If we're outside cutoff, consider going back out
        if position > cutoff:

            # Estimate time needed for out-lap + flying lap
            est_outlap = 95_000   # ms (placeholder)
            est_flying = 90_000   # ms (placeholder)
            required = est_outlap + est_flying

            return session.m_sessionTimeLeft > required

        return False
