# f1/teammate_manager.py

from core.events import EventType


class TeammateManager:
    """
    Handles teammate-related state transitions:
    - teammate detection
    - teammate pit entry
    - teammate DNF
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        self.teammate_index = None
        self.teammate_name = None

        self.last_teammate_position = None
        self.last_teammate_pit_mode = 0
        self.last_teammate_status = None
        self.last_teammate_ahead = None
        self.last_teammate_dnf = False

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, lap_data_all, status_all):
        """
        session: SessionData
        lap_data_all: dict of carIndex → LapData
        status_all: dict of carIndex → CarStatusData
        """

        # -----------------------------------------------------
        # DETECT TEAMMATE
        # -----------------------------------------------------
        if self.teammate_index is None:
            self._detect_teammate(session)

        if self.teammate_index is None:
            return

        teammate_lap = lap_data_all[self.teammate_index]
        teammate_status = status_all[self.teammate_index]

        # -----------------------------------------------------
        # PIT ENTRY
        # -----------------------------------------------------
        pit_mode = getattr(teammate_status, "m_pitMode", 0)

        if pit_mode == 1 and self.last_teammate_pit_mode != 1:
            first_name = self.telemetry_state.get_driver_first_name(
                self.telemetry_state.get_driver_id_for_participant_index(self.teammate_index) or 0
            )
            self._emit(EventType.TEAMMATE_PITTING, first_name=first_name)

        # -----------------------------------------------------
        # TEAMMATE DNF
        # -----------------------------------------------------
        dnf = bool(teammate_status.m_resultStatus in (4, 5, 6))

        if dnf and not self.last_teammate_dnf:
            first_name = self.telemetry_state.get_driver_first_name(
                self.telemetry_state.get_driver_id_for_participant_index(self.teammate_index) or 0
            )
            self._emit(EventType.TEAMMATE_DNF, first_name=first_name)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_teammate_pit_mode = pit_mode
        self.last_teammate_dnf = dnf

    # ---------------------------------------------------------
    # Teammate detection helper
    # Uses ParticipantData to find teammates by teamId
    # ---------------------------------------------------------
    def _detect_teammate(self, session):
        player_index = self.telemetry_state.player_index
        if not self.telemetry_state.participants:
            return

        player_team = None
        for p in self.telemetry_state.participants.m_participants:
            if p.m_raceNumber == player_index + 1:
                player_team = p.m_teamId
                break

        if player_team is None:
            return

        for idx, p in enumerate(self.telemetry_state.participants.m_participants):
            if idx == player_index:
                continue
            if p.m_teamId == player_team:
                self.teammate_index = idx
                self.teammate_name = self.telemetry_state.get_driver_name(p.m_driverId)
                return
