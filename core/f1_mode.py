# core/f1_mode.py
# F1 Mode — deterministic responses for R&D and practice program.
# No LLM. All lines pre-cached in TTS.

import random
import re
from .base_mode import BaseMode


class F1Mode(BaseMode):
    """
    F1 Garage/Menu mode.
    Handles R&D recommendations and practice program selection.
    All responses are deterministic, pre-cached, warmth-wrapped.
    """

    RND_CATEGORIES = ["Aero", "Powertrain", "Chassis", "Durability"]

    PRACTICE_PROGRAMS = {
        "track acclimatisation",
        "tyre management",
        "fuel management",
        "ers management",
        "qualifying simulation",
        "race strategy",
    }

    _WARMTH_TIERS = {
        (0, 2): "sharp",
        (3, 5): "professional",
        (6, 8): "supportive",
        (9, 10): "partnership",
    }

    def __init__(self, context):
        super().__init__(context)
        self.practice_goal = None
        self.waiting_for_user = True

    def on_enter(self):
        print("[F1Mode] Entered")
        self.waiting_for_user = True

    def _warmth_tier(self, warmth: int) -> str:
        for (lo, hi), tier in self._WARMTH_TIERS.items():
            if lo <= warmth <= hi:
                return tier
        return "professional"

    def _parse_category(self, text: str):
        """Extract which R&D category the teammate is working on."""
        text_lower = text.lower()
        for cat in self.RND_CATEGORIES:
            if cat.lower() in text_lower:
                return cat
        return None

    def _parse_practice_program(self, text: str):
        """Extract practice program name from text."""
        text_lower = text.lower()
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        words = text_clean.split()

        for program in self.PRACTICE_PROGRAMS:
            program_words = program.split()
            if all(w in words for w in program_words):
                return program.title()

        return None

    def _rnd_response(self, teammate_category: str, warmth: int) -> str:
        """Build R&D response text from template."""
        tier = self._warmth_tier(warmth)
        remaining = [c for c in self.RND_CATEGORIES if c != teammate_category]
        chosen = random.choice(remaining)

        from core.radio_lines import RadioLines
        return RadioLines.get_f1_rnd(teammate_category, chosen, tier)

    def _practice_acknowledge(self, program: str, warmth: int) -> str:
        tier = self._warmth_tier(warmth)
        from core.radio_lines import RadioLines
        return RadioLines.get_f1_practice(program, tier)

    def _ers_management_response(self, warmth: int) -> str:
        tier = self._warmth_tier(warmth)
        from core.radio_lines import RadioLines
        return RadioLines.get_f1_practice("ERS Management", tier)

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine,
                objective_manager=None, ers_drs_manager=None, career=None):
        av_manager.set_visible(True)

        if self.waiting_for_user:
            user_text = input_manager.get_text()
            if not user_text:
                av_manager.set_state("listening")
                av_manager.play_animation("f1mode_listen", loop=True)
                return
        else:
            user_text = input_manager.get_text()
            if not user_text:
                return

        self.waiting_for_user = False

        user_lower = user_text.lower().strip()
        warmth = career.warmth if career else 0

        # "ERS management done" → resume ERS automation
        if "ers management done" in user_lower or "ers off done" in user_lower:
            if ers_drs_manager:
                ers_drs_manager.resume_ers_automation()
            self.waiting_for_user = True
            av_manager.set_state("listening")
            av_manager.play_animation("f1mode_listen", loop=True)
            return

        # Check if teammate category mentioned → R&D response
        teammate_cat = self._parse_category(user_text)
        if teammate_cat:
            line = self._rnd_response(teammate_cat, warmth)
            if line:
                tts_engine.speak(line, radio=False, play_beep=False, animation="f1mode_talk")
                self.waiting_for_user = True
                av_manager.play_animation("f1mode_listen", loop=True)
                return

        # Check for practice program in text
        program = self._parse_practice_program(user_text)
        if program:
            self.practice_goal = program

            if program.lower() == "ers management":
                line = self._ers_management_response(warmth)
                tts_engine.speak(line, radio=False, play_beep=False, animation="f1mode_talk")

                if ers_drs_manager:
                    ers_drs_manager.stop_ers_automation()
                    if hasattr(ers_drs_manager, 'keyboard') and ers_drs_manager.keyboard:
                        ers_drs_manager.keyboard.stop_ers()

                self.waiting_for_user = True
                av_manager.play_animation("f1mode_listen", loop=True)
                return

            line = self._practice_acknowledge(program, warmth)
            tts_engine.speak(line, radio=False, play_beep=False, animation="f1mode_talk")
            self.waiting_for_user = True
            av_manager.play_animation("f1mode_listen", loop=True)
            return

        # Invalid input → ask which program
        invalid = self._warmth_tier(warmth)
        from core.radio_lines import RadioLines
        line = RadioLines.get_f1_practice_invalid(invalid)
        tts_engine.speak(line, radio=False, play_beep=False, animation="f1mode_talk")
        self.waiting_for_user = True
        av_manager.play_animation("f1mode_listen", loop=True)
