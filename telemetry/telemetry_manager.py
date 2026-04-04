# telemetry/telemetry_manager.py

from udp.udp_listener import UDPListener
from udp.packet_decoder import PacketDecoder
from udp.telemetry_state import TelemetryState

from telemetry.lap_tracker import LapTracker
from telemetry.session_tracker import SessionTracker
from telemetry.position_tracker import PositionTracker
from telemetry.event_tracker import EventTracker
from telemetry.driver_map import DriverMap
from telemetry.car_status_tracker import CarStatusTracker


class TelemetryManager:

    def __init__(self, ip="0.0.0.0", port=20777):
        self.listener = UDPListener(ip, port)
        self.decoder = PacketDecoder()
        self.state = TelemetryState()

        # Trackers that react to packets/state
        self.trackers = [
            LapTracker(self.state),
            SessionTracker(self.state),
            PositionTracker(self.state),
            EventTracker(self.state),
            DriverMap(self.state),
            CarStatusTracker(self.state),
        ]

    def update(self):
        raw = self.listener.poll()
        if not raw:
            return

        packet = self.decoder.decode(raw)
        if packet is None:
            return

        # Update central state
        self.state.update_from_packet(packet)

        # Notify trackers
        for tracker in self.trackers:
            on_packet = getattr(tracker, "on_packet", None)
            if callable(on_packet):
                on_packet(packet)
