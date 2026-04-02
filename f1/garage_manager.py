# f1/garage_manager.py

from core.events import EventType


class GarageManager:
    """
    Detects garage-related states:
    - player in garage
    - player leaving garage
    - player entering garage
    - setup/strategy screens
    - push-out animation
    - service state
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state to detect transitions
        self.last_in_garage = False
        self.last_setup_open = False
        self.last_strategy_open = False
        self.last_pushout = False
        self.last_service_state = 0

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # Called once per telemetry tick with SessionData + UI flags
    # ---------------------------------------------------------
    def update(self, session, ui_state):
        """
        session: SessionData (from UDP)
            - m_playerCarIndex
            - m_carStatusData[player].m_inGarage (bool)
            - m_carStatusData[player].m_pitLimiterOn (bool)
            - m_carStatusData[player].m_pitMode (0=none,1=pit entry,2=pit exit)

        ui_state: custom struct you maintain for:
            - setup_open
            - strategy_open
            - pushout_animation
            - service_state (0=idle,1=working,2=finishing)
        """

        # -----------------------------------------------------
        # IN GARAGE / OUT OF GARAGE
        # -----------------------------------------------------
        in_garage = bool(ui_state.in_garage)

        if in_garage and not self.last_in_garage:
            self._emit(EventType.GARAGE_ENTERED)

        if not in_garage and self.last_in_garage:
            self._emit(EventType.GARAGE_EXITED)

        # -----------------------------------------------------
        # SETUP SCREEN
        # -----------------------------------------------------
        if ui_state.setup_open and not self.last_setup_open:
            self._emit(EventType.GARAGE_SETUP_OPENED)

        if not ui_state.setup_open and self.last_setup_open:
            self._emit(EventType.GARAGE_SETUP_CLOSED)

        # -----------------------------------------------------
        # STRATEGY SCREEN
        # -----------------------------------------------------
        if ui_state.strategy_open and not self.last_strategy_open:
            self._emit(EventType.GARAGE_STRATEGY_OPENED)

        if not ui_state.strategy_open and self.last_strategy_open:
            self._emit(EventType.GARAGE_STRATEGY_CLOSED)

        # -----------------------------------------------------
        # PUSH-OUT ANIMATION (car being rolled out of garage)
        # -----------------------------------------------------
        if ui_state.pushout_animation and not self.last_pushout:
            self._emit(EventType.GARAGE_PUSHOUT_START)

        if not ui_state.pushout_animation and self.last_pushout:
            self._emit(EventType.GARAGE_PUSHOUT_END)

        # -----------------------------------------------------
        # SERVICE STATE (mechanics working on the car)
        # -----------------------------------------------------
        if ui_state.service_state != self.last_service_state:
            self._emit(EventType.GARAGE_SERVICE_STATE,
                       state=ui_state.service_state)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_in_garage = in_garage
        self.last_setup_open = ui_state.setup_open
        self.last_strategy_open = ui_state.strategy_open
        self.last_pushout = ui_state.pushout_animation
        self.last_service_state = ui_state.service_state
