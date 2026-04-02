# core/ai_mode.py

from .base_mode import BaseMode
from .assets import AssetMap

class AIMode(BaseMode):
    """
    Saul's conversational, personality-driven mode.
    """

    def on_enter(self):
        print("[AIMode] Entered")

    def update(self, input_manager, speech_manager, intent_parser, response_brain, av_manager, tts_engine):
        av_manager.set_visible(True)

        if input_manager.is_pressed():
            av_manager.set_state("listening")
            av_manager.play_animation("aimode_listen", loop=True)

        if input_manager.is_released():
            av_manager.set_state("thinking")
            av_manager.play_animation("aimode_think", loop=False)

            user_text = speech_manager.listen_ptt()
            command = intent_parser.parse(user_text, self.__class__.__name__)
            response = response_brain.generate(user_text, self.__class__.__name__, self.context)

            av_manager.set_state("talking")
            av_manager.play_animation("aimode_talk", loop=False)

            tts_engine.speak(
                response,
                radio=False,
                voice_profile="saul_main"
            )

            av_manager.set_state("idle")
            av_manager.play_animation("aimode_idle", loop=True)
