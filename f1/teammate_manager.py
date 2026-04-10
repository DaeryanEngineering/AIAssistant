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

        if not lap_data_all:
            return

        # Bounds check
        if self.teammate_index >= len(lap_data_all) or self.teammate_index >= len(status_all):
            return

        teammate_lap = lap_data_all[self.teammate_index]
        teammate_status = status_all[self.teammate_index]

        # -----------------------------------------------------
        # PIT ENTRY
        # -----------------------------------------------------
        pit_mode = getattr(teammate_status, "m_pitMode", 0)

        if pit_mode == 1 and self.last_teammate_pit_mode != 1:
            first_name = self.telemetry_state.get_driver_first_name_by_participant_index(self.teammate_index)
            self._emit(EventType.TEAMMATE_PITTING, first_name=first_name)

        # -----------------------------------------------------
        # TEAMMATE DNF
        # -----------------------------------------------------
        result_status = getattr(teammate_status, 'm_resultStatus', 0)
        dnf = bool(result_status in (4, 5, 6))

        if dnf and not self.last_teammate_dnf:
            first_name = self.telemetry_state.get_driver_first_name_by_participant_index(self.teammate_index)
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

        participants = self.telemetry_state.participants.m_participants
        if player_index >= len(participants):
            return

        # Get player's team directly from their index
        player = participants[player_index]
        player_team = player.m_teamId

        # Find teammate (same team, different index)
        for idx, p in enumerate(participants):
            if idx == player_index:
                continue
            if p.m_teamId == player_team:
                self.teammate_index = idx
                self.teammate_name = p.m_name.rstrip('\x00') if isinstance(p.m_name, str) else p.m_name.decode('utf-8', errors='replace').rstrip('\x00') if p.m_name else f"Driver_{idx}"
                return
