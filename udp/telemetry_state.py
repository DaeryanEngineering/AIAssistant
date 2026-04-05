# udp/telemetry_state.py

import threading
from typing import Protocol, List, Optional
from core.events import EventType
from udp.packet_definitions import (
    PacketMotionData,
    PacketSessionData,
    PacketLapData,
    PacketEventData,
    PacketParticipantsData,
    PacketCarSetupData,
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketFinalClassificationData,
    PacketLobbyInfoData,
    PacketCarDamageData,
    PacketSessionHistoryData,
    PacketTyreSetsData,
    PacketMotionExData,
    PacketTimeTrialData,
    PacketLapPositionsData,
)


TEAM_NAMES = {
    0: "Mercedes",
    1: "Ferrari",
    2: "Red Bull",
    3: "McLaren",
    4: "Aston Martin",
    5: "Alpine",
    6: "Williams",
    7: "Haas",
    8: "Kick Sauber",
    9: "Racing Bulls",
}


class EventListener(Protocol):
    def handle_event(self, event_type: EventType, **payload):
        ...


class TelemetryState:
    """
    Central telemetry state + event emitter.
    Thread-safe via RLock for multi-threaded access.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._listeners: List[EventListener] = []

        # Cached packets
        self.motion: Optional[PacketMotionData] = None
        self.session: Optional[PacketSessionData] = None
        self.lap_data: Optional[PacketLapData] = None
        self.event: Optional[PacketEventData] = None
        self.participants: Optional[PacketParticipantsData] = None
        self.car_setups: Optional[PacketCarSetupData] = None
        self.car_telemetry: Optional[PacketCarTelemetryData] = None
        self.car_status: Optional[PacketCarStatusData] = None
        self.final_classification: Optional[PacketFinalClassificationData] = None
        self.lobby_info: Optional[PacketLobbyInfoData] = None
        self.car_damage: Optional[PacketCarDamageData] = None
        self.session_history: Optional[PacketSessionHistoryData] = None
        self.tyre_sets: Optional[PacketTyreSetsData] = None
        self.motion_ex: Optional[PacketMotionExData] = None
        self.time_trial: Optional[PacketTimeTrialData] = None
        self.lap_positions: Optional[PacketLapPositionsData] = None

        # Player index (updated when session/participants packets arrive)
        self.player_index: int = 0

        # Lap tracking for LAP_START event
        self._last_lap = None

        # Latest raw packet (for polling)
        self._latest_packet = None

    # ------------------------------------------------------------
    # Listener registration
    # ------------------------------------------------------------
    def register_listener(self, listener: EventListener):
        with self._lock:
            self._listeners.append(listener)

    def _emit(self, event_type: EventType, **payload):
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            listener.handle_event(event_type, **payload)

    # ------------------------------------------------------------
    # Packet routing (thread-safe)
    # ------------------------------------------------------------
    def update_from_packet(self, packet):
        with self._lock:
            self._latest_packet = packet

            # Always sync player_index from the packet header
            if hasattr(packet, 'header') and packet.header is not None:
                self.player_index = packet.header.m_playerCarIndex

            # Store packet by type
            if isinstance(packet, PacketMotionData):
                self.motion = packet

            elif isinstance(packet, PacketSessionData):
                self.session = packet

            elif isinstance(packet, PacketLapData):
                self._handle_lap_data(packet)

            elif isinstance(packet, PacketCarTelemetryData):
                self.car_telemetry = packet

            elif isinstance(packet, PacketCarStatusData):
                self.car_status = packet

            elif isinstance(packet, PacketParticipantsData):
                self.participants = packet

            elif isinstance(packet, PacketEventData):
                self.event = packet

            elif isinstance(packet, PacketCarSetupData):
                self.car_setups = packet

            elif isinstance(packet, PacketFinalClassificationData):
                self.final_classification = packet

            elif isinstance(packet, PacketLobbyInfoData):
                self.lobby_info = packet

            elif isinstance(packet, PacketCarDamageData):
                self.car_damage = packet

            elif isinstance(packet, PacketSessionHistoryData):
                self.session_history = packet

            elif isinstance(packet, PacketTyreSetsData):
                self.tyre_sets = packet

            elif isinstance(packet, PacketMotionExData):
                self.motion_ex = packet

            elif isinstance(packet, PacketTimeTrialData):
                self.time_trial = packet

            elif isinstance(packet, PacketLapPositionsData):
                self.lap_positions = packet

    def get_latest_packet(self):
        with self._lock:
            pkt = self._latest_packet
            self._latest_packet = None
        return pkt

    # ------------------------------------------------------------
    # Lap handling + LAP_START event
    # ------------------------------------------------------------
    def _handle_lap_data(self, packet: PacketLapData):
        self.lap_data = packet

        try:
            player_lap = packet.get_player_lap_data()
            current_lap = player_lap.m_currentLapNum
        except Exception:
            current_lap = None

        if current_lap is not None and current_lap != self._last_lap:
            self._last_lap = current_lap
            self._emit(EventType.LAP_START, lap=current_lap)


    # ------------------------------------------------------------
    # High-level accessors Saul will use
    # ------------------------------------------------------------

    @property
    def session_time_left(self) -> Optional[int]:
        if not self.session:
            return None
        return self.session.m_sessionTimeLeft

    @property
    def driver_status(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_driverStatus
        except Exception:
            return None

    @property
    def pit_status(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_pitStatus
        except Exception:
            return None

    @property
    def current_lap(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_currentLapNum
        except Exception:
            return None

    @property
    def sector(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_sector
        except Exception:
            return None

    @property
    def speed(self) -> Optional[int]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_speed
        except Exception:
            return None

    @property
    def throttle(self) -> Optional[float]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_throttle
        except Exception:
            return None

    @property
    def brake(self) -> Optional[float]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_brake
        except Exception:
            return None

    @property
    def steer(self) -> Optional[float]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_steer
        except Exception:
            return None

    @property
    def drs_allowed(self) -> Optional[int]:
        if not self.car_status:
            return None
        try:
            return self.car_status.get_player_status().m_drsAllowed
        except Exception:
            return None

    @property
    def drs_activation_distance(self) -> Optional[int]:
        if not self.car_status:
            return None
        try:
            return self.car_status.get_player_status().m_drsActivationDistance
        except Exception:
            return None

    # ------------------------------------------------------------
    # Driver name lookup
    # ------------------------------------------------------------

    def get_driver_name(self, driver_id: int) -> str:
        """Look up driver name by driver ID from participants data."""
        if not self.participants:
            return f"Driver_{driver_id}"
        try:
            for p in self.participants.m_participants:
                if p.m_driverId == driver_id:
                    name = p.m_name.decode('utf-8', errors='replace').rstrip('\x00')
                    if name:
                        return name
            return f"Driver_{driver_id}"
        except Exception:
            return f"Driver_{driver_id}"

    # ------------------------------------------------------------
    # Stub properties for fields not in F1 25 UDP spec
    # (safer than AttributeError — returns empty/default values)
    # ------------------------------------------------------------

    @property
    def driver_standings(self) -> list:
        """Driver championship standings (not broadcast in F1 25 UDP)."""
        return []

    @property
    def team_standings(self) -> list:
        """Team championship standings (not broadcast in F1 25 UDP)."""
        return []

    @property
    def remaining_points(self) -> int:
        """Remaining points in championship (not broadcast in F1 25 UDP)."""
        return 0

    @property
    def points_for_win(self) -> int:
        """Points awarded for a race win (standard: 25)."""
        return 25

    @property
    def player_pit_entry_lap(self) -> int:
        """Lap number for pit entry (not in F1 25 UDP spec). Returns 0."""
        return 0

    @property
    def player_pit_exit_lap(self) -> int:
        """Lap number for pit exit (not in F1 25 UDP spec). Returns 0."""
        return 0

    @property
    def pit_release_allowed(self) -> bool:
        """Whether pit release is allowed (not in F1 25 UDP spec)."""
        return False

    @property
    def is_delta_positive(self) -> bool:
        """Whether delta is currently positive (SC/VSC freeze)."""
        return False

    @property
    def track_wetness(self) -> int:
        """Track wetness percentage (not in F1 25 UDP spec). Returns 0 (dry)."""
        return 0

    @property
    def car_damage_wear(self) -> tuple:
        """Player tyre wear from CarDamage packet as (FL, FR, RL, RR)."""
        if not self.car_damage:
            return (0.0, 0.0, 0.0, 0.0)
        try:
            dmg = self.car_damage.get_player_damage()
            return dmg.m_tyresWear
        except Exception:
            return (0.0, 0.0, 0.0, 0.0)

    # ------------------------------------------------------------
    # Driver name lookup helpers
    # ------------------------------------------------------------

    def get_driver_full_name(self, driver_id: int) -> str:
        """Full name e.g. 'Charles Leclerc'."""
        if not self.participants:
            return f"Driver_{driver_id}"
        try:
            for p in self.participants.m_participants:
                if p.m_driverId == driver_id:
                    name = p.m_name.decode('utf-8', errors='replace').rstrip('\x00')
                    if name:
                        return name
            return f"Driver_{driver_id}"
        except Exception:
            return f"Driver_{driver_id}"

    def get_driver_first_name(self, driver_id: int) -> str:
        """First name e.g. 'Charles'. For teammate pitting."""
        full = self.get_driver_full_name(driver_id)
        return full.split()[0] if full else f"Driver_{driver_id}"

    def get_driver_last_name(self, driver_id: int) -> str:
        """Last name e.g. 'Leclerc'. For gap reports."""
        full = self.get_driver_full_name(driver_id)
        parts = full.split()
        return parts[-1] if parts else f"Driver_{driver_id}"

    # ------------------------------------------------------------
    # Team name lookup
    # ------------------------------------------------------------

    def get_team_name(self, team_id: int) -> str:
        """Team name from known team IDs. Falls back to 'your team'."""
        return TEAM_NAMES.get(team_id, "your team")

    # ------------------------------------------------------------
    # Final classification helpers
    # ------------------------------------------------------------

    def get_player_final_classification(self):
        """Get the player's final classification data for race finish."""
        if not self.final_classification:
            return None
        try:
            return self.final_classification.m_classificationData[self.player_index]
        except (IndexError, AttributeError):
            return None

    def get_car_at_position(self, position: int):
        """Get LapData for car at a given position (1-indexed)."""
        if not self.lap_data:
            return None
        try:
            for lap in self.lap_data.m_lapData:
                if lap.m_carPosition == position:
                    return lap
        except Exception:
            pass
        return None

    def get_driver_id_at_position(self, position: int) -> Optional[int]:
        """Get driver ID for car at a given position (1-indexed)."""
        if not self.lap_data or not self.participants:
            return None
        try:
            car = self.get_car_at_position(position)
            if car is None:
                return None
            # Driver ID is participant index (car_index), not m_driverId
            # We need to find the participant whose position matches
            for idx, lap in enumerate(self.lap_data.m_lapData):
                if lap.m_carPosition == position:
                    # The participant at this index has the driver
                    p = self.participants.m_participants[idx]
                    return p.m_driverId
        except Exception:
            pass
        return None

    def get_lap_data_for_position(self, position: int):
        """Get LapData for the car at a given position (1-indexed)."""
        if not self.lap_data:
            return None
        try:
            for lap in self.lap_data.m_lapData:
                if lap.m_carPosition == position:
                    return lap
        except Exception:
            pass
        return None

    def get_driver_id_for_participant_index(self, participant_index: int) -> Optional[int]:
        """Get driver ID from participant index."""
        if not self.participants:
            return None
        try:
            p = self.participants.m_participants[participant_index]
            return p.m_driverId
        except (IndexError, AttributeError):
            return None
