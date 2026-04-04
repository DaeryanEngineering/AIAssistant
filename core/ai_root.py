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

        # ---------------------------------------------------------
        # Text Box UI (Tkinter)
        # ---------------------------------------------------------
        self.text_box = TextBoxUI(
            on_submit_callback=self.input_manager.submit_text
        )
        self.text_box.start()

        # ---------------------------------------------------------
        # Pause Manager
        # ---------------------------------------------------------
        self.pause_manager = None


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
            )
