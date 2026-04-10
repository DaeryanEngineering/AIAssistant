# core/pause_manager.py

from core.mode_manager import ModeManager, SaulMode


class PauseManager:
    """
    Handles text box visibility and freeze/unfreeze behavior for Engineer Mode.
    Pause state is driven by ModeManager (single source of truth).
    """

    def __init__(self, telemetry_state, input_manager, text_box_ui, objective_manager=None, mode_manager=None):
        self.telemetry = telemetry_state
        self.input_manager = input_manager
        self.text_box = text_box_ui
        self.objective_manager = objective_manager
        self.mode_manager = mode_manager

        self.is_paused = False

    # ---------------------------------------------------------
    # UPDATE LOOP
    # ---------------------------------------------------------
    def update(self, current_mode):
        """
        Called every frame by AIRoot.
        Controls text box visibility and pause state.
        """
        # Get pause state from ModeManager (single source of truth)
        paused_now = (self.mode_manager.current_mode == SaulMode.PAUSED) if self.mode_manager else False

        if self.objective_manager:
            if paused_now and not self.is_paused:
                self.objective_manager.freeze()
            elif not paused_now and self.is_paused:
                self.objective_manager.resume()

        # -------------------------
        # ENTERING PAUSE
        # -------------------------
        if paused_now and not self.is_paused:
            self.is_paused = True

            # Show text box in Engineer Mode only
            if current_mode == "F1EngineerMode":
                self.text_box.show_centered()

        # -------------------------
        # EXITING PAUSE
        # -------------------------
        elif not paused_now and self.is_paused:
            self.is_paused = False

            # Hide text box when unpausing Engineer Mode
            if current_mode == "F1EngineerMode":
                self.text_box.hide()

        # -------------------------
        # AI Mode / F1 Mode
        # Text box always visible
        # -------------------------
        if current_mode in ["AIMode", "F1Mode"]:
            self.text_box.show_centered()

        # -------------------------
        # Engineer Mode (not paused)
        # Text box visible (video stays off to save compute)
        # -------------------------
        if current_mode == "F1EngineerMode" and not self.is_paused:
            self.text_box.show_centered()
