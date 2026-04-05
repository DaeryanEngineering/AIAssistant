# core/f1_mode.py

from .base_mode import BaseMode
from .assets import AssetMap

class F1Mode(BaseMode):
    """
    Garage / pre-session Saul.
    Text-driven. No PTT behavior.
    Animation flow: idle → listen → think → talk → idle
    """

    def __init__(self, context):
        super().__init__(context)
        self.waiting_for_user = False

    def on_enter(self):
        print("[F1Mode] Entered (garage)")
        self.waiting_for_user = True

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine, objective_manager=None, ers_drs_manager=None):
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

        av_manager.set_state("thinking")
        av_manager.play_animation("f1mode_think", loop=False)

        full_response = response_brain.generate(
            user_text,
            self.__class__.__name__,
            self.context
        )

        chunks = [c.strip() for c in full_response.split("\n\n") if c.strip()]

        for i, chunk in enumerate(chunks):
            av_manager.set_state("talking")
            av_manager.play_animation("f1mode_talk", loop=True)

            tts_engine.speak(
                chunk,
                radio=False,
                play_beep=False,
                voice_profile="saul_main"
            )

            if i < len(chunks) - 1:
                av_manager.set_state("thinking")
                av_manager.play_animation("f1mode_think", loop=False)

        self.waiting_for_user = True
        av_manager.set_state("listening")
        av_manager.play_animation("f1mode_listen", loop=True)
