# udp/telemetry_state.py

from typing import Protocol, List, Optional
from core.events import EventType
from udp.packet_definitions import (
    PacketMotionData,
    PacketSessionData,
    PacketLapData,
    PacketEventData,
    PacketParticipantsData,
    PacketCarSetupsData,
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketFinalClassificationData,
    PacketLobbyInfoData,
    PacketCarDamageData,
    PacketSessionHistoryData,
    PacketTyreSetsData,
    PacketMotionExData,
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
        self.car_setups: Optional[PacketCarSetupsData] = None
        self.car_telemetry: Optional[PacketCarTelemetryData] = None
        self.car_status: Optional[PacketCarStatusData] = None
        self.final_classification: Optional[PacketFinalClassificationData] = None
        self.lobby_info: Optional[PacketLobbyInfoData] = None
        self.car_damage: Optional[PacketCarDamageData] = None
        self.session_history: Optional[PacketSessionHistoryData] = None
        self.tyre_sets: Optional[PacketTyreSetsData] = None
        self.motion_ex: Optional[PacketMotionExData] = None

        # Player index (updated when session/participants packets arrive)
        self.player_index: int = 0

        # Lap tracking for LAP_START event
        self._last_lap = None


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

        # Store packet by type
        if isinstance(packet, PacketMotionData):
            self.motion = packet

        elif isinstance(packet, PacketSessionData):
            self.session = packet
            # TODO: update player index if session packet contains it

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


    # ------------------------------------------------------------
    # Lap handling + LAP_START event
    # ------------------------------------------------------------
    def _handle_lap_data(self, packet: PacketLapData):
        self.lap_data = packet

        # Extract player lap number (placeholder until we fill packet fields)
        try:
            current_lap = packet.lap_data[self.player_index].current_lap_num
        except Exception:
            current_lap = None

        if current_lap is not None and current_lap != self._last_lap:
            self._last_lap = current_lap
            self._emit(EventType.LAP_START, lap=current_lap)


    # ------------------------------------------------------------
    # High-level accessors Saul will use
    # ------------------------------------------------------------
    @property
    def current_lap(self):
        if not self.lap_data:
            return None
        return self.lap_data.lap_data[self.player_index].current_lap_num

    @property
    def sector(self):
        if not self.lap_data:
            return None
        return self.lap_data.lap_data[self.player_index].sector

    @property
    def speed(self):
        if not self.car_telemetry:
            return None
        return self.car_telemetry.car_telemetry_data[self.player_index].speed

    @property
    def throttle(self):
        if not self.car_telemetry:
            return None
        return self.car_telemetry.car_telemetry_data[self.player_index].throttle

    @property
    def brake(self):
        if not self.car_telemetry:
            return None
        return self.car_telemetry.car_telemetry_data[self.player_index].brake

    @property
    def steer(self):
        if not self.car_telemetry:
            return None
        return self.car_telemetry.car_telemetry_data[self.player_index].steer

    @property
    def drs_allowed(self):
        if not self.car_status:
            return None
        return self.car_status.car_status_data[self.player_index].drs_allowed

    @property
    def drs_activation_distance(self):
        if not self.car_status:
            return None
        return self.car_status.car_status_data[self.player_index].drs_activation_distance
