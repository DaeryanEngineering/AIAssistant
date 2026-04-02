# core/ai_root.py

from .context import Context

class AIRoot:
    """
    Central AI controller for Saul.
    Manages modes, context, and update loop.
    """

    def __init__(self):
        self.context = Context()
        self.current_mode = None

    def set_mode(self, mode_class):
        if self.current_mode:
            self.current_mode.on_exit()

        self.current_mode = mode_class(self.context)
        self.current_mode.on_enter()

    def update(self):
        self.context.update()

        if self.current_mode:
            self.current_mode.update()

