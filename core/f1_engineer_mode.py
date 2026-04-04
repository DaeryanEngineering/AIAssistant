# core/f1_engineer_mode.py

from .f1_mode import F1Mode

class F1EngineerMode(F1Mode):
    """
    Saul's race engineer mode.
    Hidden visually, radio-only.
    PTT = confirm button.
    Supports chunked long-form radio speech.
    """

    def __init__(self, context):
        super().__init__(context)
        self.waiting_for_user = False  # Not used for text, but for radio pacing

    def on_enter(self):
        print("[F1EngineerMode] Entered (on-track, radio-only)")
        self.waiting_for_user = False

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine):
        # Engineer mode is radio-only
        av_manager.set_visible(False)

        # --- CONFIRMATION HANDLING ---
        if self.context.awaiting_confirmation:
            # Waiting for PTT press
            if input_manager.is_pressed():
                av_manager.set_state("talking")

                # Speak confirmation response (chunked)
                self._speak_chunked(
                    self.context.confirmation_response,
                    tts_engine
                )

                av_manager.set_state("idle")
                self.context.awaiting_confirmation = False
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
                voice_profile="saul_main"
            )

            # Idle between chunks (Option A)
            if i < len(chunks) - 1:
                # Radio engineer "thinking" is silent but stateful
                # No animations, but we set state for consistency
                pass
