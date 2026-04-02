# f1/damage_manager.py

from core.events import EventType


class DamageManager:
    """
    Detects car damage changes and emits events to TelemetryState.
    This includes wing damage, floor/diffuser/sidepod damage,
    engine wear/faults, gearbox issues, and tyre failures.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached last-known values to detect transitions
        self.last_front_left_wing = 0
        self.last_front_right_wing = 0
        self.last_rear_wing = 0

        self.last_floor = 0
        self.last_diffuser = 0
        self.last_sidepod = 0

        self.last_gearbox = 0
        self.last_engine = 0

        self.last_engine_fault = False
        self.last_engine_seized = False

        self.last_puncture = [False, False, False, False]  # FL, FR, RL, RR

    # ---------------------------------------------------------
    # Internal helper to emit events cleanly
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # Called once per telemetry tick with CarDamageData
    # ---------------------------------------------------------
    def update(self, damage):
        """
        damage: CarDamageData from the UDP spec
        Fields include:
            - m_frontLeftWingDamage
            - m_frontRightWingDamage
            - m_rearWingDamage
            - m_floorDamage
            - m_diffuserDamage
            - m_sidepodDamage
            - m_gearBoxDamage
            - m_engineDamage
            - m_engineBlown
            - m_engineSeized
            - m_tyresDamage[4]
        """

        # -----------------------------------------------------
        # FRONT WING DAMAGE
        # -----------------------------------------------------
        if damage.m_frontLeftWingDamage != self.last_front_left_wing:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="front_left_wing",
                       value=damage.m_frontLeftWingDamage)

        if damage.m_frontRightWingDamage != self.last_front_right_wing:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="front_right_wing",
                       value=damage.m_frontRightWingDamage)

        # -----------------------------------------------------
        # REAR WING DAMAGE
        # -----------------------------------------------------
        if damage.m_rearWingDamage != self.last_rear_wing:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="rear_wing",
                       value=damage.m_rearWingDamage)

        # -----------------------------------------------------
        # FLOOR / DIFFUSER / SIDEPOD DAMAGE
        # -----------------------------------------------------
        if damage.m_floorDamage != self.last_floor:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="floor",
                       value=damage.m_floorDamage)

        if damage.m_diffuserDamage != self.last_diffuser:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="diffuser",
                       value=damage.m_diffuserDamage)

        if damage.m_sidepodDamage != self.last_sidepod:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="sidepod",
                       value=damage.m_sidepodDamage)

        # -----------------------------------------------------
        # GEARBOX DAMAGE
        # -----------------------------------------------------
        if damage.m_gearBoxDamage != self.last_gearbox:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="gearbox",
                       value=damage.m_gearBoxDamage)

        # -----------------------------------------------------
        # ENGINE DAMAGE
        # -----------------------------------------------------
        if damage.m_engineDamage != self.last_engine:
            self._emit(EventType.STRATEGY_UPDATE_FROM_GAME,
                       component="engine",
                       value=damage.m_engineDamage)

        # -----------------------------------------------------
        # ENGINE FAULTS (blown / seized)
        # -----------------------------------------------------
        engine_fault = bool(damage.m_engineBlown)
        engine_seized = bool(damage.m_engineSeized)

        if engine_fault and not self.last_engine_fault:
            self._emit(EventType.SAFETY_OVERRIDE_REQUIRED,
                       reason="engine_fault")

        if engine_seized and not self.last_engine_seized:
            self._emit(EventType.SAFETY_OVERRIDE_REQUIRED,
                       reason="engine_seized")

        # -----------------------------------------------------
        # TYRE PUNCTURES / DAMAGE SPIKES
        # -----------------------------------------------------
        for i in range(4):
            punctured = damage.m_tyresDamage[i] >= 90  # threshold placeholder
            if punctured and not self.last_puncture[i]:
                self._emit(EventType.SAFETY_OVERRIDE_REQUIRED,
                           reason="puncture",
                           tyre_index=i)

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_front_left_wing = damage.m_frontLeftWingDamage
        self.last_front_right_wing = damage.m_frontRightWingDamage
        self.last_rear_wing = damage.m_rearWingDamage

        self.last_floor = damage.m_floorDamage
        self.last_diffuser = damage.m_diffuserDamage
        self.last_sidepod = damage.m_sidepodDamage

        self.last_gearbox = damage.m_gearBoxDamage
        self.last_engine = damage.m_engineDamage

        self.last_engine_fault = engine_fault
        self.last_engine_seized = engine_seized

        for i in range(4):
            self.last_puncture[i] = damage.m_tyresDamage[i] >= 90
