# saul_app.py
import os
import time
import threading
from core.ai_root import AIRoot
from core.ai_mode import AIMode
from core.f1_mode import F1Mode
from core.f1_engineer_mode import F1EngineerMode
from core.mode_manager import ModeManager, SaulMode
from core.pause_manager import PauseManager
from core.career_tracker import CareerTracker
from core.keyboard_controller import KeyboardController
from core.event_router import EventRouter
from core.radio_lines import RadioLines
from core.tts_cache import _numbers_to_words
from f1.engineer_brain import EngineerBrain
from f1.ers_drs_manager import ERSDRSManager
from core.objective_manager import ObjectiveManager
from telemetry.telemetry_manager import TelemetryManager


def main():
    # --- Core AI ---
    saul = AIRoot()

    # Set initial mode before main loop
    saul.set_mode(AIMode)

    # --- Career Tracker ---
    career = CareerTracker()
    saul.career = career

    # --- TTS cache: all static lines pre-cached on disk, instant load each startup ---
    static_lines = RadioLines.get_all_static()
    f1_mode_lines = RadioLines.get_all_f1_mode()
    all_lines = static_lines + f1_mode_lines
    saul.tts_engine.preload(all_lines)

    # Signal ready so Shawn knows she's online
    saul.tts_engine.speak("I'm ready, Shawn", radio=False, play_beep=False, animation="f1mode_talk")

    # --- Telemetry Manager (no thread - called from main loop) ---
    telemetry_manager = TelemetryManager()
    saul.telemetry_state = telemetry_manager.state

    # Remove thread - now called from main loop
    # telemetry_manager.start_threads()

    # --- Event Router ---
    engineer_brain = EngineerBrain(
        response_brain=saul.response_brain,
        tts_engine=saul.tts_engine,
        career_tracker=career
    )
    event_router = EventRouter(engineer_brain)
    telemetry_manager.state.register_listener(event_router)
    saul.event_router = event_router

    # --- Objective Manager ---
    objective_manager = ObjectiveManager(
        telemetry_state=telemetry_manager.state,
        engineer_brain=engineer_brain,
        career_tracker=career
    )
    saul.objective_manager = objective_manager

    # --- Keyboard Controller (DRS/ERS/MFD) ---
    keyboard_controller = KeyboardController()

    # --- ERSDRSManager ---
    ers_drs_manager = ERSDRSManager(
        telemetry_state=telemetry_manager.state,
        keyboard_controller=keyboard_controller,
        engineer_brain=engineer_brain
    )

    # --- Gap Worker (non-blocking gap calculation) ---
    gap_worker = GapWorker(telemetry_manager.state)

    # --- Keyboard Listener (Insert key for pit confirmation) ---
    # NOTE: keyboard package doesn't catch Steam Input keys.
    # Use "confirm" text command instead when in Engineer Mode pause menu.

    # Remove thread - now called from main loop
    # ers_drs_manager.start_thread()

    # --- Mode Manager ---
    def on_mode_change(new_mode):
        if new_mode == SaulMode.AI:
            saul.set_mode(AIMode)
        elif new_mode == SaulMode.F1:
            saul.set_mode(F1Mode)
        elif new_mode == SaulMode.ENGINEER:
            saul.set_mode(F1EngineerMode)
        elif new_mode == SaulMode.PAUSED:
            pass
        
        # Enable/disable animation based on mode
        animation_enabled = (new_mode == SaulMode.F1 or new_mode == SaulMode.ENGINEER)
        saul.tts_engine.set_animation_enabled(animation_enabled)

    mode_manager = ModeManager(
        telemetry_state=telemetry_manager.state,
        on_mode_change=on_mode_change
    )

    # Wire ERSDRSManager into Saul's context
    saul.ers_drs_manager = ers_drs_manager

    # Pass mode_manager to PauseManager so it uses ModeManager's pause detection
    saul.pause_manager = PauseManager(
        telemetry_state=telemetry_manager.state,
        input_manager=saul.input_manager,
        text_box_ui=saul.text_box,
        objective_manager=objective_manager,
        mode_manager=mode_manager
    )

    # --- Main Loop (20Hz = 50ms per frame) ---
    LOOP_HZ = 20
    LOOP_PERIOD = 1.0 / LOOP_HZ

    _session_debug_printed = False

    while True:
        loop_start = time.perf_counter()

        # 1. Mode management
        mode_manager.update()

        # 2. Telemetry read + all managers (was in separate thread)
        telemetry_manager.update()

        # 3. ERS/DRS automation (was in separate thread)
        # Only run if in Engineer mode
        mode_name = type(saul.current_mode).__name__ if saul.current_mode else "None"
        if saul.current_mode and isinstance(saul.current_mode, F1EngineerMode):
            ers_drs_manager.update(career=career)

        # 4. Saul AI update (intent handling for AI/chat modes)
        saul.update()

        # 5. Gap worker - compute and speak gap call if ready
        gap_line = gap_worker.get_gap_call_if_ready()
        if gap_line:
            saul.tts_engine.speak(gap_line, radio=True, play_beep=True)

        # Frame timing - enforce 20Hz
        elapsed = time.perf_counter() - loop_start
        sleep_time = LOOP_PERIOD - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)


class GapWorker:
    """
    Gap calculation worker thread.
    Computes gap calls and returns cached radio line when ready.
    """

    def __init__(self, telemetry_state):
        self.telemetry = telemetry_state

        self.driver_last_names = {}
        self.gap_phrase_cache = {}
        self.last_gap = {}
        self.last_trend = {}
        self.last_called_bucket = {}

        self._last_gap_lap = -1
        self._pending_gap = None
        self._lock = threading.Lock()
        self._running = True
        
        self._thread = threading.Thread(target=self._run, daemon=True, name="GapWorker")
        self._thread.start()

    def get_gap_call_if_ready(self) -> str | None:
        """Check if a gap call is ready to speak."""
        with self._lock:
            result = self._pending_gap
            self._pending_gap = None
            return result

    def _run(self):
        while self._running:
            # Wait until participants are ready
            if not getattr(self.telemetry, '_participants_ready', False):
                time.sleep(0.1)
                continue
            
            self._compute_and_cache()
            time.sleep(0.1)  # Check every 100ms

    def _compute_and_cache(self):
        from core.radio_lines import RadioLines

        session = self.telemetry.session
        player = self.telemetry.get_player()

        if not session or not player:
            return

        if getattr(session, 'm_safetyCarStatus', 0) != 0:
            return

        current_lap = player.m_currentLapNum

        if current_lap <= 1:
            return

        if current_lap == self._last_gap_lap:
            return

        self._last_gap_lap = current_lap

        # Use position-based approach (race position, not participant index)
        player = self.telemetry.get_player()
        ahead_lap = self.telemetry.get_car_ahead()
        behind_lap = self.telemetry.get_car_behind()

        ahead_id  = ahead_lap.m_driverId  if ahead_lap else None
        behind_id = behind_lap.m_driverId if behind_lap else None

        print(f"[GAP] Checking: lap={current_lap}, ahead_id={ahead_id}, behind_id={behind_id}")

        gap_ahead = self._compute_gap_to_driver(ahead_id)
        gap_behind = self._compute_gap_to_driver(behind_id)

        print(f"[GAP] Gaps: ahead={gap_ahead}, behind={gap_behind}")

        gap_line = None
        if gap_ahead is not None:
            gap_line = self._build_gap_line(ahead_id, gap_ahead, ahead=True)

        if gap_line is None and gap_behind is not None:
            gap_line = self._build_gap_line(behind_id, gap_behind, ahead=False)

        if gap_line:
            print(f"[GAP] Computed: {gap_line}")
            with self._lock:
                self._pending_gap = gap_line

    def _compute_gap_to_driver(self, driver_id):
        if driver_id is None:
            return None

        player = self.telemetry.get_player()
        other = self.telemetry.get_lap_data_by_driver_id(driver_id)

        if not other:
            return None

        track_length = self.telemetry.track_length
        speed = self.telemetry.speed or 0

        return self._compute_gap(
            player.m_totalDistance,
            other.m_totalDistance,
            track_length,
            speed
        )

    def _compute_gap(self, player_dist, other_dist, track_length, speed):
        if track_length <= 0 or speed <= 0:
            return None

        delta = abs(player_dist - other_dist)

        if delta >= track_length:
            return None

        speed_ms = speed / 3.6
        gap = delta / speed_ms

        if gap < 0.1:
            return None

        return round(gap, 1)

    def _build_gap_line(self, driver_id, gap, ahead=True):
        from core.radio_lines import RadioLines

        if driver_id not in self.driver_last_names:
            last_name = self.telemetry.get_last_name_by_driver_id(driver_id)
            self.driver_last_names[driver_id] = last_name

        last_name = self.driver_last_names[driver_id]

        key = (driver_id, gap)
        if key not in self.gap_phrase_cache:
            self.gap_phrase_cache[key] = RadioLines.format_gap(gap)

        gap_phrase = self.gap_phrase_cache[key]

        if self.last_called_bucket.get(driver_id) == gap:
            return None

        self.last_called_bucket[driver_id] = gap

        if ahead:
            return f"{last_name} ahead, {gap_phrase}"
        else:
            return f"{last_name} behind, {gap_phrase}"


if __name__ == "__main__":
    main()