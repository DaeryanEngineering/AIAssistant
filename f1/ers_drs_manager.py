# f1/ers_drs_manager.py

from core.events import EventType


class ERSDRSManager:
    """
    Handles ERS deployment logic, DRS availability, and DRS activation.
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state to detect transitions
        self.last_ers_mode = None
        self.last_overtake_active = False
        self.last_drs_allowed = False
        self.last_drs_active = False
        self.last_battery_percent = 100

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # Called once per telemetry tick with CarStatusData
    # ---------------------------------------------------------
    def update(self, status):
        """
        status: CarStatusData from the UDP spec
        Fields include:
            - m_ersDeployMode
            - m_ersStoreEnergy
            - m_drsAllowed
            - m_drsActivationDistance
            - m_drsActive
            - m_overtakeActive
        """

        ers_mode = getattr(status, "m_ersDeployMode", None)
        battery = getattr(status, "m_ersStoreEnergy", 0.0)
        drs_allowed = bool(getattr(status, "m_drsAllowed", False))
        drs_active = bool(getattr(status, "m_drsActive", False))
        overtake_active = bool(getattr(status, "m_overtakeActive", False))

        # -----------------------------------------------------
        # ERS MODE CHANGES
        # -----------------------------------------------------
        if ers_mode != self.last_ers_mode:
            self._handle_ers_mode_change(ers_mode)

        # -----------------------------------------------------
        # OVERTAKE BUTTON (ERS Overtake)
        # -----------------------------------------------------
        if overtake_active and not self.last_overtake_active:
            self._emit(EventType.START_FLYING_LAP)  # placeholder event
        if not overtake_active and self.last_overtake_active:
            self._emit(EventType.FLYING_LAP_COMPLETED)  # placeholder event

        # -----------------------------------------------------
        # DRS ALLOWED (entering DRS zone)
        # -----------------------------------------------------
        if drs_allowed and not self.last_drs_allowed:
            self._emit(EventType.WEATHER_UPDATE, intensity="drs_available")

        # -----------------------------------------------------
        # DRS ACTIVE (wing open)
        # -----------------------------------------------------
        if drs_active and not self.last_drs_active:
            self._emit(EventType.WEATHER_UPDATE, intensity="drs_open")

        # -----------------------------------------------------
        # BATTERY WARNINGS
        # -----------------------------------------------------
        battery_percent = battery * 100.0

        if battery_percent < 10 <= self.last_battery_percent:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="battery_low",
                       value=battery_percent)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_ers_mode = ers_mode
        self.last_overtake_active = overtake_active
        self.last_drs_allowed = drs_allowed
        self.last_drs_active = drs_active
        self.last_battery_percent = battery_percent

    # ---------------------------------------------------------
    # ERS mode change handler
    # ---------------------------------------------------------
    def _handle_ers_mode_change(self, mode):
        """
        ERS modes vary by game version:
            0 = None
            1 = Medium
            2 = Hotlap
            3 = Overtake
        Replace with your real mapping.
        """

        if mode == 0:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="ers_mode",
                       value="none")

        elif mode == 1:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="ers_mode",
                       value="medium")

        elif mode == 2:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="ers_mode",
                       value="hotlap")

        elif mode == 3:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="ers_mode",
                       value="overtake")

        else:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="ers_mode",
                       value=f"unknown({mode})")
