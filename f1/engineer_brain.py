# f1/engineer_brain.py

from core.events import EventType
from core.radio_lines import RadioLines


class EngineerBrain:
    """
    Saul's race engineer brain.
    Receives high-level events from EventRouter and turns them into
    radio lines via tts_engine, with warmth-aware line selection.
    """

    def __init__(self, response_brain, tts_engine, career_tracker):
        self.response_brain = response_brain
        self.tts_engine = tts_engine
        self.career = career_tracker

    # ---------------------------------------------------------
    # Internal helper — routes through RadioLines
    # ---------------------------------------------------------
    def _say(self, event_name: str, priority: bool = False, **kwargs):
        line = RadioLines.get(event_name, self.career, **kwargs)
        if line:
            self.tts_engine.speak(
                line,
                priority=priority,
                radio=True,
                play_beep=True,
            )

    # ---------------------------------------------------------
    # Flag / safety events
    # ---------------------------------------------------------
    def handle_red_flag(self, **_):
        self._say("red_flag", priority=True)

    def handle_red_flag_restart(self, **_):
        self._say("restart_grid_ready", priority=True)

    def handle_sc_start(self, **_):
        self._say("safety_car_deployed", priority=True)

    def handle_sc_restart(self, **_):
        self._say("safety_car_in_this_lap", priority=True)

    def handle_sc_end(self, **_):
        self._say("safety_car_end")

    def handle_vsc_start(self, **_):
        self._say("vsc_deployed", priority=True)

    def handle_vsc_end(self, **_):
        self._say("vsc_end")

    def handle_sc_vsc_pit_recommendation(self, **_):
        self._say("safety_override")

    def handle_delta_freeze_start(self, **_):
        self._say("delta_freeze_start")

    def handle_delta_freeze_end(self, **_):
        self._say("delta_freeze_end")

    # ---------------------------------------------------------
    # Race start
    # ---------------------------------------------------------
    def handle_race_start(self, **_):
        self._say("race_start", priority=True)

    # ---------------------------------------------------------
    # Pit window / strategy
    # ---------------------------------------------------------
    def handle_pit_window(self, **_):
        self._say("pit_window_open")

    def handle_pit_reminder(self, **_):
        self._say("pit_window_sector3")

    def handle_pit_limiter_reminder(self, **_):
        self._say("pit_limiter_reminder", priority=True)

    def handle_pit_stop_quality(self, quality: str | None = None, **_):
        if quality == "good":
            self._say("pit_stop_quality_good", priority=True)
        elif quality == "acceptable":
            self._say("pit_stop_quality_acceptable", priority=True)
        else:
            self._say("pit_stop_quality_slow", priority=True)

    def handle_extend_stint(self, **_):
        self._say("extend_stint")

    def handle_safety_override(self, reason: str | None = None, **_):
        self._say("safety_override")

    def handle_strategy_update(self, component: str | None = None, value: int | None = None, **_):
        if component:
            line = f"We're adjusting your strategy because of {component} damage."
        else:
            line = "We're changing your strategy because of the damage."
        self.tts_engine.speak(line, radio=True, play_beep=True)

    def handle_out_lap(self, **_):
        line = "Out lap, Build the temperature and check the balance,"
        self.tts_engine.speak(line, radio=True, play_beep=True)

    def handle_in_lap(self, **_):
        line = "In lap, Box this lap, Mind the delta on entry,"
        self.tts_engine.speak(line, radio=True, play_beep=True)

    # ---------------------------------------------------------
    # Teammate / traffic
    # ---------------------------------------------------------
    def handle_teammate_pit(self, first_name: str | None = None, **_):
        if first_name:
            self._say("teammate_pitting", first=first_name)
        else:
            self._say("teammate_pitting", first="Your teammate")

    def handle_teammate_dnf(self, first_name: str | None = None, **_):
        if first_name:
            self._say("teammate_dnf", first=first_name)
        else:
            self._say("teammate_dnf", first="Your teammate")

    # ---------------------------------------------------------
    # Qualifying
    # ---------------------------------------------------------
    def handle_quali_goal(self, **_):
        self._say("quali_goal")

    def handle_quali_lap_complete(self, position: int | None = None, **_):
        if position is not None:
            self._say("quali_lap_complete", position=position)
        else:
            self._say("quali_lap_complete", position=0)

    def handle_quali_lap_invalid(self, **_):
        self._say("quali_lap_invalid")

    def handle_quali_provisional_pole(self, **_):
        self._say("quali_provisional_pole")

    def handle_quali_final_pole(self, **_):
        self._say("quali_final_pole")

    def handle_quali_position_loss(self, position: int | None = None, **_):
        if position is not None:
            self._say("quali_position_lost", position=position)
        else:
            self._say("quali_position_lost", position=0)

    def handle_quali_position_update(self, position: int | None = None, **_):
        self._say("quali_position_update", position=position or 0)

    def handle_quali_lap_complete_valid(self, lap: int | None = None, position: int | None = None, **_):
        self._say("quali_lap_complete_valid", position=position or 0)

    def handle_quali_lap_complete_invalid(self, lap: int | None = None, **_):
        self._say("quali_lap_invalid")

    def handle_quali_go_back_out(self, **_):
        self._say("quali_go_back_out")

    def handle_quali_target(self, target_position: int | None = None, **_):
        if target_position is not None:
            line = f"We need at least P{target_position} to make the cutoff."
            self.tts_engine.speak(line, radio=True, play_beep=True)
        else:
            line = "We need a better lap to make the cutoff."
            self.tts_engine.speak(line, radio=True, play_beep=True)

    # ---------------------------------------------------------
    # Weather
    # ---------------------------------------------------------
    def handle_weather_update(self, minutes: int | None = None,
                              intensity: str | None = None,
                              trend: str | None = None,
                              **_):
        if minutes is not None and intensity:
            line = f"{intensity.capitalize()} rain expected in about {minutes} minutes."
            self.tts_engine.speak(line, radio=True, play_beep=True)
        elif minutes is not None:
            line = f"Weather change expected in about {minutes} minutes."
            self.tts_engine.speak(line, radio=True, play_beep=True)
        else:
            line = "Track conditions are changing, Keep me updated on the grip."
            self.tts_engine.speak(line, radio=True, play_beep=True)

    def handle_weather_changed(self, **_):
        self._say("weather_changed")

    def handle_rain_soon(self, minutes: int | None = None, **_):
        if minutes is not None:
            self._say("rain_soon", n=minutes)
        else:
            self._say("rain_soon", n=0)

    def handle_track_drying(self, **_):
        self._say("track_drying")

    def handle_track_worsening(self, **_):
        self._say("track_worsening")

    def handle_crossover_to_full_wets(self, **_):
        self._say("crossover_wets")

    def handle_crossover_to_inters(self, **_):
        self._say("crossover_inters")

    def handle_crossover_to_slicks(self, **_):
        self._say("crossover_slicks")

    # ---------------------------------------------------------
    # Gap reports — every racing lap
    # ---------------------------------------------------------
    def handle_gap_report(self, lap: int | None = None,
                          ahead_name: str | None = None,
                          ahead_gap: float | None = None,
                          ahead_lapped: bool = False,
                          behind_name: str | None = None,
                          behind_gap: float | None = None,
                          behind_lapped: bool = False,
                          position: int | None = None,
                          **_):
        gap_parts = []
        if position is not None:
            gap_parts.append(f"P{position}")

        if ahead_gap is not None:
            ahead_text = RadioLines.format_gap_text(ahead_gap, ahead_lapped)
            if ahead_text:
                gap_parts.append(f"{ahead_text} ahead")

        if behind_gap is not None:
            behind_text = RadioLines.format_gap_text(behind_gap, behind_lapped)
            if behind_text:
                gap_parts.append(f"{behind_text} behind")

        if not gap_parts:
            return

        line = " ".join(gap_parts)
        self.tts_engine.speak(line, radio=True, play_beep=True)

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
        if win_on_the_line:
            line = "Five laps to go, This is for the win."
            self.tts_engine.speak(line, radio=True, play_beep=True)
            return
        if podium_on_the_line:
            line = "Five laps to go, This is for the podium."
            self.tts_engine.speak(line, radio=True, play_beep=True)
            return

        self._say("last_five_laps",
                  position=position or 0,
                  ahead=ahead_name or "",
                  gap=RadioLines.format_gap(ahead_gap) if ahead_gap else "",
                  behind=behind_name or "",
                  behind_gap=RadioLines.format_gap(behind_gap) if behind_gap else "")

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
        if win_on_the_line:
            line = "Last lap, This is for the win, Bring it home."
            self.tts_engine.speak(line, radio=True, play_beep=True)
            return
        if podium_on_the_line:
            line = "Last lap, This is for the podium, Keep it clean."
            self.tts_engine.speak(line, radio=True, play_beep=True)
            return
        if under_threat and behind_gap and behind_name:
            line = f"Last lap, {RadioLines.format_gap(behind_gap)} to {behind_name} behind, Defend the position."
            self.tts_engine.speak(line, radio=True, play_beep=True)
            return
        if attacking and ahead_gap and ahead_name:
            line = f"Last lap, {RadioLines.format_gap(ahead_gap)} to {ahead_name} ahead, Push to the line."
            self.tts_engine.speak(line, radio=True, play_beep=True)
            return

        self._say("last_lap",
                  position=position or 0,
                  ahead=ahead_name or "",
                  gap=RadioLines.format_gap(ahead_gap) if ahead_gap else "",
                  behind=behind_name or "",
                  behind_gap=RadioLines.format_gap(behind_gap) if behind_gap else "")

    # ---------------------------------------------------------
    # Race finish
    # ---------------------------------------------------------
    def handle_race_finish(self, position: int | None = None, points: int | None = None, **_):
        if position is None:
            return
        if position == 1:
            self._say("race_finish_p1", priority=True, position=1)
        elif position <= 6:
            self._say("race_finish_p2_p6", position=position)
        elif position <= 11:
            self._say("race_finish_p7_p11", position=position)
        elif position <= 16:
            self._say("race_finish_p12_p16", position=position)
        else:
            self._say("race_finish_p17_p22", position=position)

    # ---------------------------------------------------------
    # End of race / titles
    # ---------------------------------------------------------
    def handle_race_win(self, **_):
        self._say("race_win", priority=True)

    def handle_position_gain(self, positions: int | None = None, position: int | None = None, **_):
        self._say("position_gain", positions=positions or 0, position=position or 0)

    def handle_position_lost(self, positions: int | None = None, position: int | None = None, **_):
        self._say("position_lost", positions=positions or 0, position=position or 0)

    def handle_constructors_title(self, position: int | None = None, team: str | None = None, **_):
        self._say("constructors_title", priority=True,
                  position=position or 0, team=team or "your team")

    def handle_drivers_title(self, is_first: bool = False, **_):
        if is_first:
            self._say("drivers_title_first", priority=True)
        else:
            self._say("drivers_title_consecutive", priority=True)

    # ---------------------------------------------------------
    # Session events
    # ---------------------------------------------------------
    def handle_session_start(self, **_):
        self._say("session_start")

    def handle_session_ready(self, **_):
        self._say("session_ready")

    def handle_sprint_announcement(self, **_):
        self._say("sprint_race_no_pit")

    def handle_session_end(self, **_):
        self._say("session_end")

    def handle_session_type_changed(self, **_):
        self._say("session_type_changed")

    # ---------------------------------------------------------
    # Garage events
    # ---------------------------------------------------------
    def handle_garage_entered(self, **_):
        self._say("garage_entered")

    def handle_garage_exited(self, **_):
        self._say("garage_exited")

    # ---------------------------------------------------------
    # Lap start
    # ---------------------------------------------------------
    def handle_lap_start(self, lap: int | None = None, **_):
        self._say("lap_start", lap=lap or 0)

    # ---------------------------------------------------------
    # Lap invalidated
    # ---------------------------------------------------------
    def handle_lap_invalidated(self, **_):
        self._say("lap_invalidated")

    # ---------------------------------------------------------
    # Pit entry / exit
    # ---------------------------------------------------------
    def handle_pit_entry(self, **_):
        self._say("pit_entry")

    def handle_pit_exit(self, **_):
        self._say("pit_exit")

    # ---------------------------------------------------------
    # Pit limiter (voice-only events)
    # ---------------------------------------------------------
    def handle_pit_limiter_on(self, **_):
        self._say("pit_limiter_on")

    def handle_pit_limiter_off(self, **_):
        self._say("pit_limiter_off")

    # ---------------------------------------------------------
    # Track flags
    # ---------------------------------------------------------
    def handle_track_green(self, **_):
        self._say("track_green")

    def handle_track_yellow(self, **_):
        self._say("track_yellow")

    def handle_track_double_yellow(self, **_):
        self._say("track_double_yellow")

    # ---------------------------------------------------------
    # On track entered / exited
    # ---------------------------------------------------------
    def handle_on_track_entered(self, **_):
        pass

    def handle_on_track_exited(self, **_):
        pass

    # ---------------------------------------------------------
    # Quali lap start
    # ---------------------------------------------------------
    def handle_quali_lap_start(self, lap: int | None = None, **_):
        self._say("lap_start", lap=lap or 0)

    # ---------------------------------------------------------
    # Pit lane / service events (informational only)
    # ---------------------------------------------------------
    def handle_pit_lane_entered(self, **_):
        pass

    def handle_pit_lane_exited(self, **_):
        pass

    def handle_pit_service_start(self, **_):
        pass

    def handle_pit_service_end(self, **_):
        pass

    def handle_pit_release(self, **_):
        pass

    def handle_pit_entry_line(self, **_):
        self._say("pit_entry_line")

    def handle_pit_exit_line(self, **_):
        self._say("pit_exit_line")

    # ---------------------------------------------------------
    # Forecast changes (handled by weather_changed)
    # ---------------------------------------------------------
    def handle_forecast_rain_change(self, **_):
        pass

    def handle_forecast_weather_change(self, **_):
        self._say("forecast_weather_change")
