# telemetry/lap_tracker.py

from core.events import EventType
from udp.packet_definitions import PacketLapData


class LapTracker:
    """
    Tracks lap-by-lap position and gap data.
    Emits RACE_GAP events every racing lap (not lap 1, not SC/VSC/Red).
    Uses m_totalDistance to calculate accurate time gaps.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state
        self._last_gap_lap = -1

    def update(self):
        """Called every telemetry tick. Emits RACE_GAP if conditions met."""
        session = self.telemetry_state.session
        lap_data = self.telemetry_state.lap_data
        if not session or not lap_data:
            return

        # Suppress under SC/VSC/Red flag
        sc_status = getattr(session, 'm_safetyCarStatus', 0)
        if sc_status != 0:
            return

        # Get player data
        try:
            player_lap = lap_data.get_player_lap_data()
            current_lap = player_lap.m_currentLapNum
            position = player_lap.m_carPosition
        except Exception:
            return

        # Suppress lap 1
        if current_lap <= 1:
            return

        # Suppress if we already called this lap
        if current_lap == self._last_gap_lap:
            return

        self._last_gap_lap = current_lap

        # Get player speed and track length
        player_speed = self.telemetry_state.speed or 0
        track_length = getattr(session, 'm_trackLength', 0)

        # Find car ahead (position - 1)
        ahead_gap = None
        ahead_lapped = False
        if position > 1:
            ahead_lap = self.telemetry_state.get_lap_data_for_position(position - 1)
            if ahead_lap:
                gap_result = self._calculate_gap(
                    player_lap.m_totalDistance,
                    ahead_lap.m_totalDistance,
                    track_length,
                    player_speed
                )
                ahead_gap = gap_result[0]
                ahead_lapped = gap_result[1]

        # Find car behind (position + 1)
        behind_gap = None
        behind_lapped = False
        behind_lap = self.telemetry_state.get_lap_data_for_position(position + 1)
        if behind_lap:
            gap_result = self._calculate_gap(
                behind_lap.m_totalDistance,
                player_lap.m_totalDistance,
                track_length,
                player_speed
            )
            behind_gap = gap_result[0]
            behind_lapped = gap_result[1]

        # Only emit if we have at least one gap to report
        if ahead_gap is not None or behind_gap is not None:
            self.telemetry_state._emit(
                EventType.RACE_GAP,
                lap=current_lap,
                position=position,
                ahead_gap=ahead_gap,
                ahead_lapped=ahead_lapped,
                behind_gap=behind_gap,
                behind_lapped=behind_lapped,
            )

    def _calculate_gap(self, car_a_distance: float, car_b_distance: float, track_length: float, player_speed: float) -> tuple:
        """
        Calculate gap between two cars using totalDistance.

        Args:
            car_a_distance: m_totalDistance of the car we're measuring from
            car_b_distance: m_totalDistance of the other car
            track_length: Track length in meters
            player_speed: Player speed in km/h

        Returns:
            tuple: (gap_seconds or None, is_lapped: bool)
                   gap_seconds is None if car is lapped or gap < 0.1s
        """
        if track_length <= 0:
            return (None, False)

        delta_distance = abs(car_a_distance - car_b_distance)

        # Check if a full lap separates them
        if delta_distance >= track_length:
            return (None, True)  # is_lapped

        # Calculate time gap using player speed
        if player_speed > 0:
            speed_ms = player_speed / 3.6  # km/h to m/s
            gap_seconds = delta_distance / speed_ms

            # Ignore gaps less than 0.1 seconds
            if gap_seconds < 0.1:
                return (None, False)

            return (round(gap_seconds, 1), False)

        return (None, False)
