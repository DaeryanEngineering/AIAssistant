# f1/strategy_manager.py

from core.events import EventType


class StrategyManager:
    """
    Handles season-level and race-level strategic logic:
    - championship math (drivers + constructors)
    - championship clinch / elimination
    - rival tracking
    - pit window strategy
    - risk vs reward decisions
    - race scenario classification
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_driver_points = None
        self.last_team_points = None
        self.last_rival_points = None
        self.last_position = None

        self.championship_clinched = False
        self.constructors_clinched = False
        self.eliminated = False
        self.rival_driver_id = None

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, lap_data):
        """
        session: SessionData
        lap_data: LapData for player
        """

        # -----------------------------------------------------
        # LOAD STANDINGS
        # -----------------------------------------------------
        driver_standings = session.m_driverStandings  # list of (driverId, points)
        team_standings = session.m_teamStandings      # list of (teamId, points)

        # Player info
        player_driver_id = session.m_playerCarIndex
        player_team_id = session.m_playerTeamId

        # Extract player points
        player_points = self._get_driver_points(driver_standings, player_driver_id)
        team_points = self._get_team_points(team_standings, player_team_id)

        # Determine rival (2nd place in standings)
        rival_driver_id, rival_points = self._get_rival(driver_standings, player_driver_id)

        # -----------------------------------------------------
        # DRIVERS' CHAMPIONSHIP CLINCH
        # -----------------------------------------------------
        if not self.championship_clinched:
            if self._drivers_championship_clinched(player_points, rival_points, session):
                self._emit(EventType.CHAMPIONSHIP_DRIVERS_CLINCHED)
                self.championship_clinched = True

        # -----------------------------------------------------
        # CONSTRUCTORS' CHAMPIONSHIP CLINCH
        # -----------------------------------------------------
        if not self.constructors_clinched:
            if self._constructors_championship_clinched(team_standings, player_team_id, session):
                self._emit(EventType.CHAMPIONSHIP_CONSTRUCTORS_CLINCHED)
                self.constructors_clinched = True

        # -----------------------------------------------------
        # CHAMPIONSHIP ELIMINATION
        # -----------------------------------------------------
        if not self.eliminated:
            if self._drivers_eliminated(player_points, rival_points, session):
                self._emit(EventType.CHAMPIONSHIP_ELIMINATED)
                self.eliminated = True

        # -----------------------------------------------------
        # CHAMPIONSHIP DECIDER (THIS RACE)
        # -----------------------------------------------------
        if self._is_title_decider_this_race(player_points, rival_points, session):
            self._emit(EventType.CHAMPIONSHIP_DECIDER_THIS_RACE)

        # -----------------------------------------------------
        # CHAMPIONSHIP DECIDER (NEXT RACE)
        # -----------------------------------------------------
        if self._is_title_decider_next_race(player_points, rival_points, session):
            self._emit(EventType.CHAMPIONSHIP_DECIDER_NEXT_RACE)

        # -----------------------------------------------------
        # RIVAL POSITION UPDATE
        # -----------------------------------------------------
        rival_position = self._get_rival_position(session, rival_driver_id)

        if rival_position is not None:
            self._emit(EventType.CHAMPIONSHIP_RIVAL_UPDATE,
                       rival_driver_id=rival_driver_id,
                       rival_position=rival_position)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_driver_points = player_points
        self.last_team_points = team_points
        self.last_rival_points = rival_points
        self.rival_driver_id = rival_driver_id

    # ---------------------------------------------------------
    # Helper: get driver points
    # ---------------------------------------------------------
    def _get_driver_points(self, standings, driver_id):
        for d_id, pts in standings:
            if d_id == driver_id:
                return pts
        return 0

    # ---------------------------------------------------------
    # Helper: get team points
    # ---------------------------------------------------------
    def _get_team_points(self, standings, team_id):
        for t_id, pts in standings:
            if t_id == team_id:
                return pts
        return 0

    # ---------------------------------------------------------
    # Helper: get rival (2nd place)
    # ---------------------------------------------------------
    def _get_rival(self, standings, player_driver_id):
        sorted_standings = sorted(standings, key=lambda x: x[1], reverse=True)
        if sorted_standings[0][0] == player_driver_id:
            return sorted_standings[1]
        return sorted_standings[0]

    # ---------------------------------------------------------
    # Helper: rival position
    # ---------------------------------------------------------
    def _get_rival_position(self, session, rival_driver_id):
        for idx, driver_id in enumerate(session.m_carPositions):
            if driver_id == rival_driver_id:
                return idx + 1
        return None

    # ---------------------------------------------------------
    # Championship math
    # ---------------------------------------------------------
    def _drivers_championship_clinched(self, player_pts, rival_pts, session):
        max_remaining = session.m_remainingPoints
        return player_pts > rival_pts + max_remaining

    def _constructors_championship_clinched(self, standings, player_team_id, session):
        player_team_pts = self._get_team_points(standings, player_team_id)
        other_team_pts = max(pts for tid, pts in standings if tid != player_team_id)
        max_remaining = session.m_remainingPoints
        return player_team_pts > other_team_pts + max_remaining

    def _drivers_eliminated(self, player_pts, rival_pts, session):
        max_remaining = session.m_remainingPoints
        return player_pts + max_remaining < rival_pts

    def _is_title_decider_this_race(self, player_pts, rival_pts, session):
        max_remaining_after = session.m_remainingPoints - session.m_pointsForWin
        return player_pts > rival_pts + max_remaining_after

    def _is_title_decider_next_race(self, player_pts, rival_pts, session):
        max_remaining_after = session.m_remainingPoints - session.m_pointsForWin * 2
        return player_pts > rival_pts + max_remaining_after
