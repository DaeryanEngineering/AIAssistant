# core/pause_manager.py

class PauseManager:
    """
    Handles pause/unpause detection, text box visibility,
    and freeze/unfreeze behavior for Engineer Mode.
    """

    def __init__(self, telemetry_state, input_manager, text_box_ui):
        self.telemetry = telemetry_state
        self.input_manager = input_manager
        self.text_box = text_box_ui

        self._last_session_time = None
        self.is_paused = False

    # ---------------------------------------------------------
    # PAUSE DETECTION
    # ---------------------------------------------------------
    def _detect_pause(self):
        """
        Detect pause by checking if sessionTimeLeft stops changing.
        """
        session_time = self.telemetry.session_time_left

        if self._last_session_time is None:
            self._last_session_time = session_time
            return False

        paused = (session_time == self._last_session_time)
        self._last_session_time = session_time

        return paused

    # ---------------------------------------------------------
    # UPDATE LOOP
    # ---------------------------------------------------------
    def update(self, current_mode):
        """
        Called every frame by AIRoot.
        Controls text box visibility and pause state.
        """

        paused_now = self._detect_pause()

        if paused_now:
            objective_manager.freeze()
        else:
            objective_manager.resume()


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
        # Text box hidden
        # -------------------------
        if current_mode == "F1EngineerMode" and not self.is_paused:
            self.text_box.hide()
