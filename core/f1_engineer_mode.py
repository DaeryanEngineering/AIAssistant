# core/f1_engineer_mode.py

from .f1_mode import F1Mode


class F1EngineerMode(F1Mode):
    """
    Saul's race engineer mode.
    Hidden visually, radio-only.
    Reacts to telemetry events and processes objectives from text input.
    """

    def __init__(self, context):
        super().__init__(context)
        self.waiting_for_user = False

    def on_enter(self):
        self.waiting_for_user = False

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine, 
               objective_manager=None, ers_drs_manager=None, career=None, telemetry_state=None):
        # Engineer mode is radio-only, hidden
        av_manager.set_visible(False)

        # ERS/DRS automation now runs from main loop - don't call here

        # --- OBJECTIVE / CHAMPIONSHIP HANDLING (from pause text box) ---
        if input_manager.has_text():
            text = input_manager.consume_text()
            intent = intent_parser.parse(text, "F1EngineerMode")

            if objective_manager:
                # Championship commands
                if intent.intent == "f2_championship":
                    objective_manager.record_f2_championship()
                    return

                if intent.intent == "f1_championship":
                    objective_manager.record_f1_championship()
                    return

                if intent.intent == "reset_streak":
                    objective_manager.reset_consecutive_titles()
                    return

                if intent.intent == "set_year":
                    if objective_manager.career:
                        objective_manager.career.set_career_year(intent.parameters.get("year", 1))
                    return

                if intent.intent == "set_series":
                    if objective_manager.career:
                        objective_manager.career.set_series(intent.parameters.get("series", "F1"))
                    return

                # Race commands
                if intent.intent == "formation_lap":
                    from core.events import EventType
                    telemetry_state._emit(EventType.FORMATION_LAP_START)
                    return

                if intent.intent == "launch":
                    from core.events import EventType
                    telemetry_state._emit(EventType.RACE_START_GRID)
                    return

                if intent.intent == "no_pit_stop":
                    # Disable pit calls for this session
                    telemetry_state._no_pit_stop = True
                    av_manager.set_state("talking")
                    tts_engine.speak("No pit stop, understood.", radio=True, play_beep=True)
                    av_manager.set_state("idle")
                    return

                if intent.intent == "find_grid_slot":
                    from core.events import EventType
                    telemetry_state._emit(EventType.FORMATION_LAP_SECTOR3)
                    return

                # Objective commands
                if intent.intent == "objective_start":
                    objective_manager.start_objective(
                        intent.parameters.get("obj_type"),
                        intent.parameters.get("description"),
                        intent.parameters.get("target")
                    )
                    return

                if intent.intent == "objective_pass":
                    objective_manager.manual_pass()
                    return

                if intent.intent == "objective_fail":
                    objective_manager.manual_fail()
                    return

                if intent.intent == "objective_cancel":
                    objective_manager.manual_cancel()
                    return


        # --- CONFIRMATION HANDLING ---
        if self.context.awaiting_confirmation:
            if input_manager.has_text():
                text = input_manager.consume_text()
                if text.strip().lower() == "confirm":
                    av_manager.set_state("talking")
                    self._speak_chunked(
                        self.context.confirmation_response,
                        tts_engine
                    )
                    av_manager.set_state("idle")
                    self.context.awaiting_confirmation = False
                    if self.context.pending_action:
                        self.context.pending_action()
                    return
            return

        # --- PIT CONFIRMATION via "confirm" text command ---
        if ers_drs_manager:
            if input_manager.has_text():
                text = input_manager.consume_text()
                if text.strip().lower() == "confirm":
                    confirmation = ers_drs_manager.confirm_pit()
                    if confirmation:
                        av_manager.set_state("talking")
                        tts_engine.speak(confirmation, radio=True, play_beep=True)
                        av_manager.set_state("idle")
                    return

        # --- PROACTIVE ENGINEER LINES ---
        engineer_line = self.context.get_engineer_line()
        if not engineer_line:
            return

        # Speak the engineer line (chunked)
        av_manager.set_state("talking")
        self._speak_chunked(engineer_line.text, tts_engine)
        av_manager.set_state("idle")

        # If this line requires confirmation:
        if engineer_line.requires_confirmation:
            self.context.awaiting_confirmation = True
            self.context.confirmation_response = engineer_line.on_confirm

    # ---------------------------------------------------------
    # INTERNAL: Chunked radio speech (Option B)
    # ---------------------------------------------------------
    def _speak_chunked(self, full_text, tts_engine):
        """
        Splits long engineer lines into chunks (paragraphs)
        and speaks them sequentially over the radio.
        """
        chunks = [c.strip() for c in full_text.split("\n\n") if c.strip()]

        for i, chunk in enumerate(chunks):
            # Talk this chunk
            tts_engine.speak(
                chunk,
                radio=True,
                play_beep=True,
            )

            # Idle between chunks (Option A)
            if i < len(chunks) - 1:
                # Radio engineer "thinking" is silent but stateful
                # No animations, but we set state for consistency
                pass
