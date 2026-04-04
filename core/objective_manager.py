# core/objective_manager.py

from enum import Enum, auto


class ObjectiveState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class ObjectiveType(Enum):
    LAP_TIME = auto()
    SECTOR_IMPROVEMENT = auto()
    DELTA_TARGET = auto()
    TYRE_MANAGEMENT = auto()
    FUEL_SAVING = auto()
    ERS_MANAGEMENT = auto()
    RACECRAFT = auto()
    STRATEGY = auto()
    WEATHER = auto()
    FORMATION = auto()
    SAFETY_CAR = auto()


class ObjectiveManager:
    """
    Tracks Codemasters-style objectives that the user manually feeds to Saul.
    Saul does NOT invent objectives. She only tracks what the user gives her.
    """

    def __init__(self, telemetry_state, engineer_brain):
        self.telemetry = telemetry_state
        self.engineer = engineer_brain

        self.state = ObjectiveState.INACTIVE
        self.obj_type = None
        self.description = None
        self.target_value = None  # lap time, delta, sector, etc.

        self._frozen = False

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def start_objective(self, obj_type: ObjectiveType, description: str, target=None):
        """
        Called when the user types an objective into the text box.
        """
        self.obj_type = obj_type
        self.description = description
        self.target_value = target

        self.state = ObjectiveState.ACTIVE
        self._frozen = False

        self.engineer._say(f"Objective received: {description}. Tracking now.")

    def manual_pass(self):
        if self.state == ObjectiveState.ACTIVE:
            self.state = ObjectiveState.COMPLETED
            self.engineer._say("Objective complete. Nice work.")
            self._reset()

    def manual_fail(self):
        if self.state == ObjectiveState.ACTIVE:
            self.state = ObjectiveState.FAILED
            self.engineer._say("Objective failed. Reset when you're ready.")
            self._reset()

    def manual_cancel(self):
        if self.state == ObjectiveState.ACTIVE:
            self.state = ObjectiveState.CANCELLED
            self.engineer._say("Objective cancelled.")
            self._reset()

    def freeze(self):
        if self.state == ObjectiveState.ACTIVE:
            self._frozen = True
            self.state = ObjectiveState.PAUSED

    def resume(self):
        if self.state == ObjectiveState.PAUSED:
            self._frozen = False
            self.state = ObjectiveState.ACTIVE

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------
    def _reset(self):
        self.state = ObjectiveState.INACTIVE
        self.obj_type = None
        self.description = None
        self.target_value = None
        self._frozen = False

    # ---------------------------------------------------------
    # UPDATE LOOP
    # ---------------------------------------------------------
    def update(self):
        """
        Called every frame by AIRoot (but only in Engineer Mode).
        Evaluates the objective if it's active and not frozen.
        """
        if self.state != ObjectiveState.ACTIVE:
            return

        if self._frozen:
            return

        # -----------------------------------------------------
        # Objective evaluation is MANUAL ONLY for now.
        # The user tells Saul "pass" or "fail".
        #
        # Later, we can add:
        # - lap time comparison
        # - sector improvement detection
        # - delta tracking
        # - tyre temp/wear thresholds
        # - ERS usage patterns
        # - gap closing/defending logic
        #
        # But for now, Saul only tracks and waits for your call.
        # -----------------------------------------------------
        pass
