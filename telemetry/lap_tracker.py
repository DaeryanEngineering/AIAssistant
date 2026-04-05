# telemetry/lap_tracker.py

from core.events import EventType
from udp.packet_definitions import PacketLapData


class LapTracker:
    """
    Tracks lap-by-lap position and gap data.
    Emits RACE_GAP events every racing lap (not lap 1, not SC/VSC/Red).
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

        # Get player lap data
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

        # Find car ahead (position - 1)
        ahead_name = None
        ahead_gap = None
        ahead_lap_diff = 0
        if position > 1:
            ahead_lap = self.telemetry_state.get_lap_data_for_position(position - 1)
            if ahead_lap:
                ahead_gap_sec = ahead_lap.delta_to_car_in_front_seconds
                # If gap is negative or zero, use absolute value
                if ahead_gap_sec < 0:
                    ahead_gap_sec = abs(ahead_gap_sec)
                ahead_gap = ahead_gap_sec
                # Check lap difference
                ahead_lap_diff = current_lap - ahead_lap.m_currentLapNum
                if ahead_lap_diff < 0:
                    ahead_lap_diff = abs(ahead_lap_diff)
                # Get driver name
                ahead_driver_id = self.telemetry_state.get_driver_id_for_participant_index(position - 1)
                if ahead_driver_id is not None:
                    ahead_name = self.telemetry_state.get_driver_last_name(ahead_driver_id)

        # Find car behind (position + 1)
        behind_name = None
        behind_gap = None
        behind_lap_diff = 0
        behind_lap = self.telemetry_state.get_lap_data_for_position(position + 1)
        if behind_lap:
            behind_gap_sec = behind_lap.delta_to_car_in_front_seconds
            if behind_gap_sec < 0:
                behind_gap_sec = abs(behind_gap_sec)
            behind_gap = behind_gap_sec
            behind_lap_diff = current_lap - behind_lap.m_currentLapNum
            if behind_lap_diff < 0:
                behind_lap_diff = abs(behind_lap_diff)
            behind_driver_id = self.telemetry_state.get_driver_id_for_participant_index(position)
            if behind_driver_id is not None:
                behind_name = self.telemetry_state.get_driver_last_name(behind_driver_id)

        # Only emit if we have at least one gap to report
        if ahead_name or behind_name:
            self.telemetry_state._emit(
                EventType.RACE_GAP,
                lap=current_lap,
                position=position,
                ahead_name=ahead_name,
                ahead_gap=ahead_gap,
                ahead_lap_diff=ahead_lap_diff,
                behind_name=behind_name,
                behind_gap=behind_gap,
                behind_lap_diff=behind_lap_diff,
            )
