# telemetry/ui_state.py

class GarageUIState:
    """
    Tracks garage UI state (setup screen, strategy screen, push-out, etc.)
    that is NOT broadcast via F1 25 UDP.

    Defaults to False for all fields. The app can update these externally
    if there are hooks to detect UI screen changes (e.g., from game state).
    """

    def __init__(self):
        self.in_garage: bool = False
        self.setup_open: bool = False
        self.strategy_open: bool = False
        self.pushout_animation: bool = False
        self.service_state: int = 0  # 0=idle, 1=working, 2=finishing
