# core/intent_parser.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Command:
    """
    Command Handling
    """
    intent: str
    parameters: dict
    confidence: float


class IntentParser:
    """
    Intent Parser - parses text into commands based on mode.
    """

    def parse(self, text: str, mode: str) -> Command:
        text_lower = text.strip().lower()

        if mode == "F1EngineerMode":
            # Championship commands first (higher priority)
            champ = self._parse_championship(text_lower)
            if champ:
                return champ

            # Race commands (formation, launch, sprint, pit)
            race = self._parse_race_commands(text_lower)
            if race:
                return race

            return self._parse_objective(text_lower)

        return Command(
            intent="unknown",
            parameters={"text": text},
            confidence=0.0
        )

    # ---------------------------------------------------------
    # CHAMPIONSHIP COMMANDS
    # ---------------------------------------------------------

    def _parse_championship(self, text: str) -> Optional[Command]:
        # F2 championship
        f2_triggers = [
            "won f2", "f2 champion", "f2 title", "f2 championship",
            "won the f2", "f2 champ",
        ]
        for trigger in f2_triggers:
            if trigger in text:
                return Command(
                    intent="f2_championship",
                    parameters={},
                    confidence=1.0
                )

        # First F1 title
        first_title_triggers = [
            "first title", "first championship", "first f1 title",
            "first f1 championship", "won my first",
        ]
        for trigger in first_title_triggers:
            if trigger in text:
                return Command(
                    intent="f1_championship",
                    parameters={"is_first": True},
                    confidence=1.0
                )

        # F1 championship (general)
        f1_triggers = [
            "won the championship", "won championship", "won title",
            "won the title", "world champion", "i won", "we won",
            "champion", "title", "f1 champion", "f1 championship",
            "defended", "defended the title", "back to back",
            "back-to-back", "three in a row", "three-peat",
            "four in a row", "five in a row",
        ]
        for trigger in f1_triggers:
            if trigger in text:
                return Command(
                    intent="f1_championship",
                    parameters={"is_first": False},
                    confidence=0.9
                )

        # Reset consecutive streak
        streak_triggers = [
            "streak broken", "lost the title", "didn't win",
            "didn't win the title", "streak ended",
        ]
        for trigger in streak_triggers:
            if trigger in text:
                return Command(
                    intent="reset_streak",
                    parameters={},
                    confidence=0.9
                )

        # Career year set
        if text.startswith("set year") or text.startswith("year "):
            try:
                parts = text.split()
                year = int(parts[-1])
                return Command(
                    intent="set_year",
                    parameters={"year": year},
                    confidence=0.9
                )
            except (ValueError, IndexError):
                pass

        # Series set
        if text.startswith("set series") or text.startswith("series "):
            series = text.split()[-1].upper()
            if series in ("F1", "F2"):
                return Command(
                    intent="set_series",
                    parameters={"series": series},
                    confidence=0.9
                )

        return None

    # ---------------------------------------------------------
    # RACE COMMANDS
    # ---------------------------------------------------------

    def _parse_race_commands(self, text: str) -> Optional[Command]:
        # Formation lap
        formation_triggers = [
            "formation lap", "formation", "warm tyres", "warm brakes",
            "warm the tyres", "warm the brakes",
        ]
        for trigger in formation_triggers:
            if trigger in text:
                return Command(
                    intent="formation_lap",
                    parameters={},
                    confidence=0.9
                )

        # Race start / launch
        launch_triggers = [
            "launch", "race start", "lights out", "go time", "let s go",
        ]
        for trigger in launch_triggers:
            if trigger in text:
                return Command(
                    intent="launch",
                    parameters={},
                    confidence=0.9
                )

        # Sprint race (no pit stop)
        sprint_triggers = [
            "sprint race", "sprint", "no pit stop", "no pitting",
            "no pits", "don't pit", "won't pit",
        ]
        for trigger in sprint_triggers:
            if trigger in text:
                return Command(
                    intent="no_pit_stop",
                    parameters={},
                    confidence=0.9
                )

        # Find grid slot
        grid_triggers = [
            "find grid slot", "grid slot", "find your spot", "stay right",
        ]
        for trigger in grid_triggers:
            if trigger in text:
                return Command(
                    intent="find_grid_slot",
                    parameters={},
                    confidence=0.9
                )

        return None

    # ---------------------------------------------------------
    # OBJECTIVE COMMANDS
    # ---------------------------------------------------------

    def _parse_objective(self, text: str) -> Command:
        # Objective start commands
        if text.startswith("objective") or text.startswith("obj"):
            return self._parse_objective_start(text)

        # Pass/fail/cancel
        if text in ("pass", "passed", "complete", "done", "success"):
            return Command(intent="objective_pass", parameters={}, confidence=1.0)

        if text in ("fail", "failed", "missed", "miss"):
            return Command(intent="objective_fail", parameters={}, confidence=1.0)

        if text in ("cancel", "cancelled", "abort", "stop"):
            return Command(intent="objective_cancel", parameters={}, confidence=1.0)

        return Command(
            intent="unknown",
            parameters={"text": text},
            confidence=0.0
        )

    def _parse_objective_start(self, text: str) -> Command:
        # Remove "objective" or "obj" prefix
        if text.startswith("objective "):
            text = text[10:]
        elif text.startswith("obj "):
            text = text[4:]

        # Try to match known objective types
        objective_types = {
            "lap time": "LAP_TIME",
            "sector": "SECTOR_IMPROVEMENT",
            "delta": "DELTA_TARGET",
            "tyre": "TYRE_MANAGEMENT",
            "fuel": "FUEL_SAVING",
            "ers": "ERS_MANAGEMENT",
            "racecraft": "RACECRAFT",
            "strategy": "STRATEGY",
            "weather": "WEATHER",
            "formation": "FORMATION",
            "safety car": "SAFETY_CAR",
        }

        for key, obj_type in objective_types.items():
            if text.startswith(key):
                return Command(
                    intent="objective_start",
                    parameters={
                        "obj_type": obj_type,
                        "description": text,
                        "target": None,
                    },
                    confidence=0.8
                )

        # Generic objective
        return Command(
            intent="objective_start",
            parameters={
                "obj_type": "UNKNOWN",
                "description": text,
                "target": None,
            },
            confidence=0.5
        )
