# telemetry/car_status_tracker.py

from udp.packet_definitions import PacketCarStatusData

class CarStatusTracker:
    def __init__(self, state):
        self.state = state

        self._last_drs_allowed = None
        self._last_ers_store = None
        self._last_flag = None
        self._last_pit_limiter = None

    def on_packet(self, packet):

        # Only react to CarStatus packets
        if not isinstance(packet, PacketCarStatusData):
            return

        car = packet.car_status_data[self.state.player_index]

        # ------------------------------
        # DRS Allowed Change
        # ------------------------------
        if car.m_drsAllowed != self._last_drs_allowed:
            self._last_drs_allowed = car.m_drsAllowed

            if car.m_drsAllowed == 1:
                print("[Tracker] DRS now allowed")
            else:
                print("[Tracker] DRS no longer allowed")

        # ------------------------------
        # ERS Store Low Warning
        # ------------------------------
        if self._last_ers_store is None or car.m_ersStoreEnergy != self._last_ers_store:
            self._last_ers_store = car.m_ersStoreEnergy

            if car.m_ersStoreEnergy < 200000:  # 200 kJ
                print("[Tracker] ERS critically low")

        # ------------------------------
        # FIA Flag Change
        # ------------------------------
        if car.m_vehicleFiaFlags != self._last_flag:
            self._last_flag = car.m_vehicleFiaFlags
            print(f"[Tracker] FIA Flag changed to {car.m_vehicleFiaFlags}")

        # ------------------------------
        # Pit Limiter Change
        # ------------------------------
        if car.m_pitLimiterStatus != self._last_pit_limiter:
            self._last_pit_limiter = car.m_pitLimiterStatus

            if car.m_pitLimiterStatus == 1:
                print("[Tracker] Pit limiter ON")
            else:
                print("[Tracker] Pit limiter OFF")
