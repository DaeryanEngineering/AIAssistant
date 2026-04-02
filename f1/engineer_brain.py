# f1/engineer_brain.py

from core.events import EventType


class EngineerBrain:
    """
    Saul's race engineer brain.
    Receives high-level events from EventRouter and turns them into
    radio lines via tts_engine.
    """

    def __init__(self, response_brain, tts_engine):
        self.response_brain = response_brain
        self.tts_engine = tts_engine

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _say(self, text: str):
    
        self.tts_engine.speak(
            text,
            radio=True,
            play_beep=True,
            voice_profile="saul_radio"
        )

    # ---------------------------------------------------------
    # Flag / safety events
    # ---------------------------------------------------------
    def handle_red_flag(self, **_):
        self._say("Red flag. Return to the pits.")

    def handle_red_flag_restart(self, **_):
        self._say("Mode launch. Be careful into Turn 1.")

    def handle_sc_start(self, **_):
        self._say("Safety car deployed. Slow down and keep your delta positive.")

    def handle_sc_restart(self, **_):
        self._say("Safety car in this lap. Prepare for restart. No overtaking until the line.")

    def handle_vsc_start(self, **_):
        self._say("Virtual safety car. Reduce pace and keep your delta positive.")

    def handle_vsc_end(self, **_):
        self._say("VSC ending. Get ready.")

    def handle_sc_vsc_pit_recommendation(self, **_):
        self._say("We’re considering a stop under safety car. Confirm if you want to box.")

    def handle_delta_freeze_start(self, **_):
        self._say("Delta active. Keep it positive.")

    def handle_delta_freeze_end(self, **_):
        self._say("Delta ending. Prepare to resume racing.")

    # ---------------------------------------------------------
    # Formation lap / start
    # ---------------------------------------------------------
    def handle_formation_lap(self, **_):
        self._say("Mode formation. Warm the tyres and check the brakes.")

    def handle_find_grid_slot(self, **_):
        self._say("Find your box on the grid.")

    def handle_race_start(self, **_):
        self._say("Mode launch. Be careful into Turn 1.")

    # ---------------------------------------------------------
    # Pit window / strategy
    # ---------------------------------------------------------
    def handle_pit_window(self, **_):
        self._say("Box this lap. Confirm if you’re okay with the stop.")

    def handle_pit_reminder(self, **_):
        self._say("Reminder: box this lap. Confirm if you’re staying out.")

    def handle_extend_stint(self, **_):
        self._say("Understood. Extending the stint by one lap if it’s safe.")

    def handle_safety_override(self, reason: str | None = None, **_):
        if reason == "engine_fault":
            self._say("We’ve got an engine issue. I need you to box. It’s not safe to continue.")
        elif reason == "engine_seized":
            self._say("Engine has seized. Box immediately and stop the car safely.")
        elif reason == "puncture":
            self._say("You’ve got a puncture. Box this lap, please.")
        else:
            self._say("Shawn, I need you to box. It’s not safe to continue.")

    def handle_strategy_update(self, component: str | None = None, value: int | None = None, **_):
        if component:
            self._say(f"We’re adjusting your strategy because of {component} damage.")
        else:
            self._say("We’re changing your strategy because of the damage.")

    def handle_out_lap(self, **_):
        self._say("Out lap. Build the temperature and check the balance.")

    def handle_in_lap(self, **_):
        self._say("In lap. Box this lap. Mind the delta on entry.")

    # ---------------------------------------------------------
    # Teammate / traffic
    # ---------------------------------------------------------
    def handle_teammate_pit(self, first_name: str | None = None, **_):
        if first_name:
            self._say(f"{first_name} is boxing this lap.")
        else:
            self._say("Your teammate is boxing this lap.")

    # ---------------------------------------------------------
    # Qualifying
    # ---------------------------------------------------------
    def handle_quali_push_start(self, **_):
        self._say("Alright, give me everything on this lap.")

    def handle_quali_lap_end(self, position: int | None = None, **_):
        if position is not None:
            self._say(f"Lap complete. That’s P{position}.")
        else:
            self._say("Lap complete. Time is on the board.")

    def handle_quali_position_loss(self, position: int | None = None, **_):
        if position is not None:
            self._say(f"We’ve dropped to P{position}. Might be worth going again.")
        else:
            self._say("We’ve lost a position. Might be worth going again.")

    def handle_quali_target(self, target_position: int | None = None, **_):
        if target_position is not None:
            self._say(f"We need at least P{target_position} to make the cutoff.")
        else:
            self._say("We need a better lap to make the cutoff.")

    # ---------------------------------------------------------
    # Weather
    # ---------------------------------------------------------
    def handle_weather_update(self, minutes: int | None = None,
                              intensity: str | None = None,
                              trend: str | None = None,
                              **_):
        if minutes is not None and intensity:
            self._say(f"{intensity.capitalize()} rain expected in about {minutes} minutes.")
        elif minutes is not None:
            self._say(f"Weather change expected in about {minutes} minutes.")
        else:
            self._say("Track conditions are changing. Keep me updated on the grip.")

    # ---------------------------------------------------------
    # Gap formatting helper (0.7 → "seven-tenths")
    # ---------------------------------------------------------
    def _format_gap(self, gap: float | None) -> str:
        if gap is None:
            return ""

        # Under 1 second → tenths
        if gap < 1.0:
            tenths = int(round(gap * 10))
            return f"{tenths}-tenths"

        # 1.0+ → "## seconds"
        if gap > 1.0:
            return f"{gap:.1f} seconds"

    # ---------------------------------------------------------
    # Gaps / lap start
    # ---------------------------------------------------------
    def handle_gap_report(self, lap: int | None = None,
                          ahead_name: str | None = None,
                          ahead_gap: float | None = None,
                          behind_name: str | None = None,
                          behind_gap: float | None = None,
                          **_):
        parts = []

        if lap is not None:
            parts.append(f"Lap {lap}.")

        if ahead_name and ahead_gap is not None:
            parts.append(f"{ahead_name} ahead. {self._format_gap(ahead_gap)}.")

        if behind_name and behind_gap is not None:
            parts.append(f"{behind_name} behind. {self._format_gap(behind_gap)}.")

        if not parts:
            parts.append("Gaps are stable. Keep doing what you’re doing.")

        self._say(" ".join(parts))

    # ---------------------------------------------------------
    # Weather
    # ---------------------------------------------------------
    def handle_crossover_to_full_wets(self, **_):
        self._say("Conditions are extreme. Full wets are the right tyre now.")

    def handle_crossover_to_inters(self, **_):
        self._say("Track is too wet for slicks. Intermediates are the right tyre now.")

    def handle_crossover_to_slicks(self, **_):
        self._say("Conditions are dry. Inters are costing you time. Come in for slicks.")

    # ---------------------------------------------------------
    # Last 5 laps / Last lap
    # ---------------------------------------------------------
    def handle_last_five_laps(self, position: int | None = None,
                              ahead_name: str | None = None,
                              ahead_gap: float | None = None,
                              behind_name: str | None = None,
                              behind_gap: float | None = None,
                              podium_on_the_line: bool = False,
                              win_on_the_line: bool = False,
                              **_):

        parts = ["Five laps to go."]

        # Contextual race picture
        if ahead_name and ahead_gap is not None:
            parts.append(f"{self._format_gap(ahead_gap)} to {ahead_name} ahead.")

        if behind_name and behind_gap is not None:
            parts.append(f"{self._format_gap(behind_gap)} to {behind_name} behind.")

        # Stakes
        if win_on_the_line:
            parts.append("This is for the win.")
        elif podium_on_the_line:
            parts.append("This is for the podium.")

        # Calm, realistic tone
        parts.append("Keep it tidy.")

        self._say(" ".join(parts))

    def handle_last_lap(self, position: int | None = None,
                        ahead_name: str | None = None,
                        ahead_gap: float | None = None,
                        behind_name: str | None = None,
                        behind_gap: float | None = None,
                        win_on_the_line: bool = False,
                        podium_on_the_line: bool = False,
                        under_threat: bool = False,
                        attacking: bool = False,
                        **_):

        # Opening line
        if win_on_the_line:
            self._say("Last lap. This is for the win. Bring it home.")
            return

        if podium_on_the_line:
            self._say("Last lap. This is for the podium. Keep it clean.")
            return

        # Battle logic
        if under_threat and behind_gap and behind_name is not None:
            self._say(f"Last lap. {self._format_gap(behind_gap)} to {behind_name} behind. Defend the position.")
            return

        if attacking and ahead_gap and ahead_name is not None:
            self._say(f"Last lap. {self._format_gap(ahead_gap)} to {ahead_name} ahead. Push to the line.")
            return

        # Neutral scenario
        self._say("Last lap. Bring it home. No risks.")


    # ---------------------------------------------------------
    # End of race / titles
    # ---------------------------------------------------------
    def handle_race_win(self, **_):
        self._say("That’s the win. Incredible drive.")

    def handle_constructors_title(self, **_):
        self._say("That seals it. We’ve won the Constructors’ Championship.")

    def handle_drivers_title(self, **_):
        self._say("Shawn… you’re World Champion.")
