# core/ai_mode.py

from .base_mode import BaseMode

class AIMode(BaseMode):
    """
    Saul's conversational, personality-driven mode.
    Text-driven. No PTT behavior.
    Supports long-form, chunked speech and looping thinking animations.
    """

    def __init__(self, context):
        super().__init__(context)
        self.waiting_for_user = False  # NEW: controls looping thinking animation

    def on_enter(self):
        print("[AIMode] Entered")
        self.waiting_for_user = True  # When entering AIMode, she waits for input

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine):
        # AIMode is text-driven. PTT does nothing here.
        av_manager.set_visible(True)

        # If she's waiting for user input and no text is submitted, loop thinking animation
        if self.waiting_for_user:
            user_text = input_manager.get_text()
            if not user_text:
                av_manager.set_state("thinking")
                av_manager.play_animation("aimode_think", loop=True)
                return
        else:
            # Not waiting for user, but check for text anyway
            user_text = input_manager.get_text()
            if not user_text:
                return

        # At this point, we have user text
        self.waiting_for_user = False  # She is now processing input

        # Quick-thinking animation (non-looping)
        av_manager.set_state("thinking")
        av_manager.play_animation("aimode_think", loop=False)

        # Generate response (may be long)
        command = intent_parser.parse(user_text, self.__class__.__name__)
        full_response = response_brain.generate(
            user_text,
            self.__class__.__name__,
            self.context
        )

        # Split into chunks (paragraphs)
        chunks = [c.strip() for c in full_response.split("\n\n") if c.strip()]

        # Speak each chunk sequentially
        for i, chunk in enumerate(chunks):
            av_manager.set_state("talking")
            av_manager.play_animation("aimode_talk", loop=True)

            tts_engine.speak(
                chunk,
                radio=False,
                play_beep=False,
                voice_profile="saul_main"
            )

            # After each chunk, return to idle (Option A)
            av_manager.set_state("idle")
            av_manager.play_animation("aimode_idle", loop=True)

            # If there are more chunks coming, loop thinking while preparing next chunk
            if i < len(chunks) - 1:
                av_manager.set_state("thinking")
                av_manager.play_animation("aimode_think", loop=True)

        # After all chunks, she waits for your next input
        self.waiting_for_user = True
        av_manager.set_state("thinking")
        av_manager.play_animation("aimode_think", loop=True)
