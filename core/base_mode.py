# core/base_mode.py

class BaseMode:
    """
    Base class for all AI modes.
    """

    def __init__(self, context):
        self.context = context

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self, input_manager, speech_manager, response_brain, av_manager, tts_engine):
        """
        Shared manager Stub
        """
        pass
