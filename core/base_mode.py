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

    def update(self, input_manager, intent_parser, response_brain, av_manager, tts_engine, objective_manager=None):
        """
        Called every frame by AIRoot.
        Subclasses override this with mode-specific behavior.
        """
        pass
