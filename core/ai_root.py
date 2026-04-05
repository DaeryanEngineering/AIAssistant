# core/ai_root.py

from .context import Context
from .input_manager import InputManager
from .audio_video_manager import AudioVideoManager
from .tts_engine import TTSEngine
from .tone_engine import ToneEngine
from .mood_engine import MoodEngine
from .response_brain import ResponseBrain
from .intent_parser import IntentParser
from core.pause_manager import PauseManager
from ui.text_box_ui import TextBoxUI
from core.objective_manager import ObjectiveManager


class AIRoot:
    """
    Central AI controller for Saul.
    Manages modes, context, and update loop.
    """

    def __init__(self):
        self.context = Context()
        self.current_mode = None

        # Shared managers / engines
        self.input_manager = InputManager()
        self.av_manager = AudioVideoManager()
        self.tts_engine = TTSEngine(self.av_manager)
        self.tone_engine = ToneEngine()
        self.mood_engine = MoodEngine()
        self.response_brain = ResponseBrain(self.tone_engine, self.mood_engine)
        self.intent_parser = IntentParser()

        # Text input UI
        self.text_box = TextBoxUI(
            on_submit_callback=self.input_manager.submit_text
        )
        self.text_box.start()

        # Pause Manager (deferred, set in saul_app.py)
        self.pause_manager = None

        # Telemetry state and event router (deferred, set in saul_app.py)
        self.telemetry_state = None
        self.event_router = None

        # Objective system (deferred, set in saul_app.py)
        self.objective_manager = None


    def set_mode(self, mode_class):
        if self.current_mode:
            self.current_mode.on_exit()

        self.current_mode = mode_class(self.context)
        self.current_mode.on_enter()

        # Visual Hint Per Mode
        name = mode_class.__name__
        if name == "AIMode":
            self.av_manager.set_visible(True)
            self.av_manager.play_animation("aimode_idle", loop=True)
        elif name == "F1Mode":
            self.av_manager.set_visible(True)
            self.av_manager.play_animation("f1mode_idle", loop=True)
        elif name == "F1EngineerMode":
            self.av_manager.set_visible(False)
            self.av_manager.stop_animation()


    def update(self):
        self.context.update()

        # ---------------------------------------------------------
        # Pause Manager update BEFORE mode update
        # ---------------------------------------------------------
        if self.pause_manager:
            self.pause_manager.update(
                current_mode=self.current_mode.__class__.__name__
            )

        if self.current_mode and self.current_mode.__class__.__name__ == "F1EngineerMode":
            if self.objective_manager:
                self.objective_manager.update()


        # ---------------------------------------------------------
        # Mode update
        # ---------------------------------------------------------
        if self.current_mode:
            self.current_mode.update(
                self.input_manager,
                self.intent_parser,
                self.response_brain,
                self.av_manager,
                self.tts_engine,
                self.objective_manager,
            )
