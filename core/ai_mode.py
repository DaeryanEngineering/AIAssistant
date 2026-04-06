# core/ai_mode.py

import sys
from .base_mode import BaseMode
from .response_brain import NoLLMError


class AIMode(BaseMode):
    """
    Saul's conversational, personality-driven mode.
    Text-driven. LLM-powered with streaming output.
    Animation flow: idle → listen → think → talk → idle
    """

    def __init__(self, context):
        super().__init__(context)
        self.waiting_for_user = True

    def on_enter(self):
        print("[AIMode] Entered")
        self.waiting_for_user = True

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine,
                objective_manager=None, ers_drs_manager=None, career=None):
        av_manager.set_visible(True)

        if self.waiting_for_user:
            user_text = input_manager.get_text()
            if not user_text:
                av_manager.set_state("listening")
                av_manager.play_animation("aimode_listen", loop=True)
                return
        else:
            user_text = input_manager.get_text()
            if not user_text:
                return

        self.waiting_for_user = False

        av_manager.set_state("thinking")
        av_manager.play_animation("aimode_think", loop=False)

        try:
            stream_iter, _ = response_brain.generate_stream(
                user_text,
                self.__class__.__name__,
                self.context,
                career,
            )
        except NoLLMError:
            self.waiting_for_user = True
            return

        # Stream tokens to console in real-time
        full = []
        print("[AIMode] ", end="", flush=True)
        for token in stream_iter:
            print(token, end="", flush=True)
            sys.stdout.flush()
            full.append(token)
        print()

        full_response = "".join(full)

        if full_response.strip():
            animation = "aimode_talk"
            tts_engine.speak(full_response, radio=False, play_beep=False, animation=animation)

        self.waiting_for_user = True
        av_manager.play_animation("aimode_listen", loop=True)
