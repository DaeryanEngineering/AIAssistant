# core/objective_manager.py

from enum import Enum, auto
from .radio_lines import RadioLines
from .career_tracker import CareerTracker


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

    def __init__(self, telemetry_state, engineer_brain, career_tracker: CareerTracker):
        self.telemetry = telemetry_state
        self.engineer = engineer_brain
        self.career = career_tracker

        self.state = ObjectiveState.INACTIVE
        self.obj_type = None
        self.description = None
        self.target_value = None

        self._frozen = False
        self._year_5_acknowledged = False
        self._year_10_acknowledged = False
        self._no_pit_stop = False  # Disable pit calls for session

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def start_objective(self, obj_type, description: str, target=None):
        """
        Called when the user types an objective into the text box.
        """
        self.obj_type = obj_type
        self.description = description
        self.target_value = target

        self.state = ObjectiveState.ACTIVE
        self._frozen = False

        line = RadioLines.objective_start(self.career, description, str(obj_type))
        self.engineer._say(line)

    def manual_pass(self):
        if self.state == ObjectiveState.ACTIVE:
            self.state = ObjectiveState.COMPLETED
            line = RadioLines.objective_pass(self.career)
            self.engineer._say(line)
            self._reset()

    def manual_fail(self):
        if self.state == ObjectiveState.ACTIVE:
            self.state = ObjectiveState.FAILED
            line = RadioLines.objective_fail(self.career)
            self.engineer._say(line)
            self._reset()

    def manual_cancel(self):
        if self.state == ObjectiveState.ACTIVE:
            self.state = ObjectiveState.CANCELLED
            line = RadioLines.objective_cancel(self.career)
            self.engineer._say(line)
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
    # CHAMPIONSHIP HANDLING
    # ---------------------------------------------------------

    def record_f2_championship(self):
        """Called when user reports winning F2 title."""
        self.career.record_f2_championship()
        line = RadioLines.f2_championship(self.career)
        self.engineer._say(line)

    def record_f1_championship(self):
        """Called when user reports winning F1 title."""
        is_first = self.career.first_f1_title_year is None
        self.career.record_f1_championship()

        if is_first:
            line = RadioLines.first_f1_title(self.career)
        else:
            line = RadioLines.consecutive_title(self.career)

        self.engineer._say(line)

    def reset_consecutive_titles(self):
        """Called when the title streak is broken."""
        self.career.reset_consecutive()
        self.engineer._say("Title streak broken. We'll start a new one next year.")

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
        Also checks for career milestones.
        """
        if self.state != ObjectiveState.ACTIVE:
            return

        if self._frozen:
            return

        # -----------------------------------------------------
        # Career milestone checks (one-time)
        # -----------------------------------------------------
        if self.career.is_year_5 and not self._year_5_acknowledged:
            self._year_5_acknowledged = True
            line = RadioLines.year_5(self.career)
            self.engineer._say(line)

        if self.career.is_year_10 and not self._year_10_acknowledged:
            self._year_10_acknowledged = True
            line = RadioLines.year_10(self.career)
            self.engineer._say(line)

        # -----------------------------------------------------
        # Objective evaluation is MANUAL ONLY.
        # The user tells Saul "pass" or "fail".
        # -----------------------------------------------------
        pass
