# core/f1_mode.py

from .base_mode import BaseMode
from .assets import AssetMap

class F1Mode(BaseMode):
    """
    Garage / pre-session Saul.
    """

    def on_enter(self):
        print("[F1Mode] Entered (garage)")

    def update(self, input_manager, speech_manager, response_brain, av_manager, tts_engine):
        av_manager.set_visible(True)

        if input_manager.is_pressed():
            av_manager.set_state("listening")
            av_manager.play_animation("f1mode_listen", loop=True)

        if input_manager.is_released():
            av_manager.set_state("thinking")
            av_manager.play_animation("f1mode_think", loop=False)

            user_text = speech_manager.listen_ptt()
            response = response_brain.generate(user_text, "F1Mode", self.context)

            av_manager.set_state("talking")
            av_manager.play_animation("f1mode_talk", loop=False)

            tts_engine.speak(
                response,
                radio=False,
                voice_profile="saul_garage"
            )

            av_manager.set_state("idle")
            av_manager.play_animation("f1mode_idle", loop=True)
