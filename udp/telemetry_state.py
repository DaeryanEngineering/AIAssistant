# udp/telemetry_state.py

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


class EventListener(Protocol):
    def handle_event(self, event_type: EventType, **payload):
        ...


class TelemetryState:
    """
    Central telemetry state + event emitter.
    This is fed by telemetry_manager / udp_listener.
    """

    def __init__(self):
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
        self._listeners.append(listener)

    def _emit(self, event_type: EventType, **payload):
        for listener in self._listeners:
            listener.handle_event(event_type, **payload)


    # ------------------------------------------------------------
    # Packet routing
    # ------------------------------------------------------------
    def update_from_packet(self, packet):
        """
        Called by telemetry_manager / udp_listener with decoded packet(s).
        """
        self._latest_packet = packet

        # Store packet by type
        if isinstance(packet, PacketMotionData):
            self.motion = packet

        elif isinstance(packet, PacketSessionData):
            self.session = packet
            self.player_index = packet.header.m_playerCarIndex

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

        elif isinstance(packet, PacketCarSetupsData):
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
