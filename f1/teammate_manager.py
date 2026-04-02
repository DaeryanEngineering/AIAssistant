# f1/teammate_manager.py

from core.events import EventType


class TeammateManager:
    """
    Handles teammate-related state transitions:
    - teammate detection
    - teammate pit entry / exit
    - teammate ahead/behind transitions
    - teammate DNF
    - teammate damage alerts
    - teammate blocking / slowing player
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
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
            self._detect_teammate(session, status_all)

        if self.teammate_index is None:
            return  # no teammate found yet

        teammate_lap = lap_data_all[self.teammate_index]
        teammate_status = status_all[self.teammate_index]

        # -----------------------------------------------------
        # PIT ENTRY / EXIT
        # -----------------------------------------------------
        pit_mode = getattr(teammate_status, "m_pitMode", 0)

        if pit_mode == 1 and self.last_teammate_pit_mode != 1:
            self._emit(EventType.TEAMMATE_PIT_ENTRY,
                       name=self.teammate_name)

        # -----------------------------------------------------
        # TEAMMATE DNF
        # -----------------------------------------------------
        dnf = bool(teammate_status.m_resultStatus in (4, 5, 6))  # DNF, DSQ, retired

        if dnf and not self.last_teammate_dnf:
            self._emit(EventType.TEAMMATE_DNF,
                       name=self.teammate_name)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_teammate_pit_mode = pit_mode
        self.last_teammate_dnf = dnf

    # ---------------------------------------------------------
    # Teammate detection helper
    # ---------------------------------------------------------
    def _detect_teammate(self, session, status_all):
        player_index = session.m_playerCarIndex
        player_team = status_all[player_index].m_teamId

        for idx, status in status_all.items():
            if idx == player_index:
                continue
            if status.m_teamId == player_team:
                self.teammate_index = idx
                self.teammate_name = self.telemetry_state.get_driver_name(status.m_driverId)
                return
