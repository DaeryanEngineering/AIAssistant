# telemetry/telemetry_manager.py

import threading
import time

from udp.udp_listener import UDPListener
from udp.packet_decoder import PacketDecoder
from udp.telemetry_state import TelemetryState

from telemetry.car_status_tracker import CarStatusTracker
from telemetry.ui_state import GarageUIState
from telemetry.lap_tracker import LapTracker

from f1.safety_manager import SafetyManager
from f1.session_manager import SessionManager
from f1.race_behavior import RaceBehavior
from f1.qualifying_behavior import QualifyingBehavior
from f1.ontrack_manager import OnTrackManager
from f1.weather_manager import WeatherManager
from f1.pit_behavior import PitBehavior
from f1.teammate_manager import TeammateManager


class TelemetryManager:

    def __init__(self, ip="0.0.0.0", port=20777):
        self.listener = UDPListener(ip, port)
        self.decoder = PacketDecoder()
        self.state = TelemetryState()

        self.garage_ui = GarageUIState()

        self.car_status_tracker = CarStatusTracker(self.state)
        self.lap_tracker = LapTracker(self.state)
        self.safety_manager = SafetyManager(self.state)
        self.session_manager = SessionManager(self.state)
        self.race_behavior = RaceBehavior(self.state)
        self.qualifying_behavior = QualifyingBehavior(self.state)
        self.ontrack_manager = OnTrackManager(self.state)
        self.weather_manager = WeatherManager(self.state)
        self.pit_behavior = PitBehavior(self.state)
        self.teammate_manager = TeammateManager(self.state)

        self._telemetry_thread = None
        self._running = False

    def update(self):
        raw = self.listener.poll()
        if not raw:
            return

        packet = self.decoder.decode(raw)
        if packet is None:
            return

        self.state.update_from_packet(packet)
        self.car_status_tracker.on_packet(packet)

        driver_status = self.state.driver_status
        if driver_status is not None:
            self.garage_ui.in_garage = (driver_status == 0)

        self._update_managers()

    def _update_managers(self):
        session = self.state.session
        lap_data = self.state.lap_data
        car_status = self.state.car_status

        if session is not None:
            self.safety_manager.update(session)
            self.session_manager.update(session)

            player_lap = lap_data.get_player_lap_data() if lap_data else None
            player_status = car_status.get_player_status() if car_status else None

            self.race_behavior.update(session, player_lap, player_status, self.state)
            self.qualifying_behavior.update(session, player_lap, self.garage_ui)
            self.ontrack_manager.update(session, player_lap, player_status)
            self.weather_manager.update(session, player_status, self.state)
            self.pit_behavior.update(player_lap, player_status)
            self.teammate_manager.update(
                session,
                self.state.lap_data.m_lapData if self.state.lap_data else [],
                self.state.car_status.m_carStatusData if self.state.car_status else []
            )

        self.lap_tracker.update()

    def start_threads(self):
        self._running = True

        def _telemetry_loop():
            while self._running:
                self.update()
                time.sleep(0.05)

        self._telemetry_thread = threading.Thread(
            target=_telemetry_loop, daemon=True, name="TelemetryThread"
        )
        self._telemetry_thread.start()

    def stop_threads(self):
        self._running = False
        if self._telemetry_thread:
            self._telemetry_thread.join(timeout=2)

