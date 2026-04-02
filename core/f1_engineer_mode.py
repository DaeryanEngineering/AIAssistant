# core/f1_engineer_mode.py

from .f1_mode import F1Mode
from .assets import AssetMap

class F1EngineerMode(F1Mode):
    """
    Saul's race engineer mode.
    Hidden visually, radio-only.
    """

    def on_enter(self):
        print("[F1EngineerMode] Entered (on-track, radio-only)")

    def update(self, input_manager, speech_manager, intent_parser, response_brain, av_manager, tts_engine):
        av_manager.set_visible(False)

        if input_manager.is_pressed():
            av_manager.set_state("listening")

        if input_manager.is_released():
            av_manager.set_state("thinking")

            user_text = speech_manager.listen_ptt()
            command = intent_parser.parse(user_text, self.__class__.__name__)
            response = response_brain.generate(user_text, self.__class__.__name__, self.context)

            av_manager.set_state("talking")

            tts_engine.speak(
                response,
                radio=True,
                play_beep=True,
                voice_profile="saul_radio"
            )

            av_manager.set_state("idle")
