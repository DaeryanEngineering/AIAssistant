# core/f1_mode.py
# F1 Mode — deterministic responses for R&D and practice program.
# Handles teammate name tracking, maxed category tracking, and smart garage entry.
# No LLM. All lines pre-cached in TTS.

import random
import re
from .base_mode import BaseMode


class F1Mode(BaseMode):
    """
    F1 Garage/Menu mode.
    Handles R&D recommendations and practice program selection.
    Tracks teammate name and maxed R&D categories across sessions.
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
        
        # State machine states
        self._state = "normal"  # normal, awaiting_teammate, awaiting_rnd
        self.waiting_for_user = True

    def on_enter(self):
        self.practice_goal = None
        # Don't reset _state - preserve across garage visits

    def _determine_entry_state(self):
        """Determine initial state based on career data. Call with career object."""
        pass  # Will be handled in update() when career is available

    def _warmth_tier(self, warmth: int) -> str:
        for (lo, hi), tier in self._WARMTH_TIERS.items():
            if lo <= warmth <= hi:
                return tier
        return "professional"

    def _parse_category(self, text: str):
        """Extract which R&D category from text."""
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

    def _extract_name(self, text: str):
        """Extract what looks like a person's name from text."""
        text_clean = text.strip()
        words = text_clean.split()
        
        if not words:
            return None
        
        first_word = words[0].capitalize()
        
        if len(first_word) >= 2 and first_word.lower() not in ['aero', 'chassis', 'powertrain', 'durability', "it's", 'thats', 'no', 'yes']:
            return first_word
        
        return None

    def _speak(self, line: str, av_manager, tts_engine):
        """Speak a line and return to listening state."""
        if line:
            tts_engine.speak(line, radio=False, play_beep=False, animation="f1mode_talk")
        av_manager.play_animation("f1mode_listen", loop=True)

    def _ask_teammate(self, warmth: int, av_manager, tts_engine):
        """Ask who they're working with."""
        tier = self._warmth_tier(warmth)
        from core.radio_lines import RadioLines
        line = RadioLines.get_f1_garage("ask_teammate", tier)
        self._speak(line, av_manager, tts_engine)

    def _ask_rnd(self, teammate_name: str, warmth: int, av_manager, tts_engine):
        """Ask what teammate is working on."""
        tier = self._warmth_tier(warmth)
        from core.radio_lines import RadioLines
        line = RadioLines.get_f1_garage("ask_rnd", tier, teammate=teammate_name)
        self._speak(line, av_manager, tts_engine)

    def _rnd_response(self, teammate_category: str, warmth: int, maxed_categories: list) -> str:
        """Build R&D response text from template."""
        tier = self._warmth_tier(warmth)
        
        # Filter out maxed categories and teammate's category
        remaining = [c for c in self.RND_CATEGORIES 
                    if c != teammate_category and c not in maxed_categories]
        
        # If all non-teammate categories are maxed, fall back to all non-teammate
        if not remaining:
            remaining = [c for c in self.RND_CATEGORIES if c != teammate_category]
        
        if not remaining:
            return None
            
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
                objective_manager=None, ers_drs_manager=None, career=None, telemetry_state=None):
        av_manager.set_visible(True)

        user_text = input_manager.get_text()
        if not user_text:
            # First time entering, show listening animation
            if self.waiting_for_user:
                if self._state == "normal" and career:
                    # Skip teammate/R&D in F2 (no upgrades)
                    if career.series == "F2":
                        self._speak("Focus on the racing in F2, ", av_manager, tts_engine)
                        self.waiting_for_user = True
                        return
                    if not career.teammate_name:
                        self._state = "awaiting_teammate"
                        self._ask_teammate(career.warmth, av_manager, tts_engine)
                    else:
                        self._state = "awaiting_rnd"
                        self._ask_rnd(career.teammate_name, career.warmth, av_manager, tts_engine)
                    self.waiting_for_user = False
                    return
                elif self._state == "awaiting_teammate":
                    self._ask_teammate(career.warmth if career else 0, av_manager, tts_engine)
                    self.waiting_for_user = False
                    return
                elif self._state == "awaiting_rnd":
                    self._ask_rnd(career.teammate_name if career else "your teammate", 
                                  career.warmth if career else 0, av_manager, tts_engine)
                    self.waiting_for_user = False
                    return
            av_manager.set_state("listening")
            av_manager.play_animation("f1mode_listen", loop=True)
            return

        user_lower = user_text.lower().strip()
        warmth = career.warmth if career else 0
        maxed_categories = career.maxed_rnd_categories if career else []
        teammate_name = career.teammate_name if career else None

        # "ERS management done" → resume ERS automation
        if "ers management done" in user_lower or "ers off done" in user_lower:
            if ers_drs_manager:
                ers_drs_manager.resume_ers_automation()
            self.waiting_for_user = True
            self._state = "normal"
            av_manager.play_animation("f1mode_listen", loop=True)
            return

        # Reset all → clear teammate name and maxed categories
        if "reset all" in user_lower or "reset everything" in user_lower:
            tier = self._warmth_tier(warmth)
            from core.radio_lines import RadioLines
            line = RadioLines.get_f1_rnd_meta("reset_all", tier)
            if career:
                career.teammate_name = None
                career.maxed_rnd_categories = []
            self._speak(line, av_manager, tts_engine)
            self._state = "awaiting_teammate"
            self.waiting_for_user = True
            return

        # State-specific handling
        if self._state == "awaiting_teammate":
            # Player is telling us their teammate's name
            name = self._extract_name(user_text)
            if name:
                if career:
                    career.teammate_name = name
                self._state = "awaiting_rnd"
                self._ask_rnd(name, warmth, av_manager, tts_engine)
                self.waiting_for_user = True
            else:
                # Ask again
                self._ask_teammate(warmth, av_manager, tts_engine)
                self.waiting_for_user = True
            return

        if self._state == "awaiting_rnd":
            # Player is telling us their teammate's R&D category
            teammate_cat = self._parse_category(user_text)
            if teammate_cat:
                self._state = "normal"
                line = self._rnd_response(teammate_cat, warmth, maxed_categories)
                if line:
                    self._speak(line, av_manager, tts_engine)
                else:
                    self._speak("Let's work on what we've got, ", av_manager, tts_engine)
                self.waiting_for_user = True
                return
            
            # Maybe they corrected the teammate name?
            if "it's" in user_lower:
                name = self._extract_name(user_text.replace("it's", "").replace("It's", ""))
                if name:
                    if career:
                        career.teammate_name = name
                    tier = self._warmth_tier(warmth)
                    from core.radio_lines import RadioLines
                    line = RadioLines.get_f1_garage("teammate_updated", tier, teammate=name)
                    self._speak(line, av_manager, tts_engine)
                    self.waiting_for_user = True
                    return
            
            # Ask again
            self._ask_rnd(teammate_name or "your teammate", warmth, av_manager, tts_engine)
            self.waiting_for_user = True
            return

        # Normal state - waiting for R&D category or practice program
        
        # Check if player says category is maxed
        maxed_match = None
        for phrase in ["is maxed", "is done", "is complete", "already done", "already maxed"]:
            if phrase in user_lower:
                cat = self._parse_category(user_text)
                if cat:
                    maxed_match = cat
                    break
        
        if maxed_match:
            if career and maxed_match not in career.maxed_rnd_categories:
                career.maxed_rnd_categories = career.maxed_rnd_categories + [maxed_match]
            tier = self._warmth_tier(warmth)
            from core.radio_lines import RadioLines
            line = RadioLines.get_f1_rnd_meta("category_maxed", tier, category=maxed_match)
            self._speak(line, av_manager, tts_engine)
            self.waiting_for_user = True
            return

        # Check if player says category has new upgrades
        available_match = None
        for phrase in ["has new upgrades", "has upgrades", "new upgrades", "is back", "is open"]:
            if phrase in user_lower:
                cat = self._parse_category(user_text)
                if cat:
                    available_match = cat
                    break
        
        if available_match:
            if career and available_match in career.maxed_rnd_categories:
                career.maxed_rnd_categories = [c for c in career.maxed_rnd_categories if c != available_match]
            tier = self._warmth_tier(warmth)
            from core.radio_lines import RadioLines
            line = RadioLines.get_f1_rnd_meta("category_available", tier, category=available_match)
            self._speak(line, av_manager, tts_engine)
            self.waiting_for_user = True
            return

        # Check if teammate category mentioned → R&D response
        teammate_cat = self._parse_category(user_text)
        if teammate_cat:
            # Check if this category is maxed
            if teammate_cat in maxed_categories:
                tier = self._warmth_tier(warmth)
                from core.radio_lines import RadioLines
                line = RadioLines.get_f1_rnd_meta("picking_maxed", tier, category=teammate_cat)
                self._speak(line, av_manager, tts_engine)
                self.waiting_for_user = True
                return
            
            # Normal R&D response
            line = self._rnd_response(teammate_cat, warmth, maxed_categories)
            if line:
                self._speak(line, av_manager, tts_engine)
            else:
                self._speak("Let's work on what we've got, ", av_manager, tts_engine)
            self.waiting_for_user = True
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
                self._state = "normal"
                av_manager.play_animation("f1mode_listen", loop=True)
                return

            line = self._practice_acknowledge(program, warmth)
            self._speak(line, av_manager, tts_engine)
            self.waiting_for_user = True
            self._state = "normal"
            return

        # Invalid input → ask which program
        invalid = self._warmth_tier(warmth)
        from core.radio_lines import RadioLines
        line = RadioLines.get_f1_practice_invalid(invalid)
        self._speak(line, av_manager, tts_engine)
        self.waiting_for_user = True
