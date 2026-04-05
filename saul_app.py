# saul_app.py
from core.ai_root import AIRoot
from core.ai_mode import AIMode
from core.f1_mode import F1Mode
from core.f1_engineer_mode import F1EngineerMode
from core.mode_manager import ModeManager, SaulMode
from core.pause_manager import PauseManager
from core.career_tracker import CareerTracker
from core.keyboard_controller import KeyboardController
from core.keyboard_listener import KeyboardListener
from core.event_router import EventRouter
from f1.engineer_brain import EngineerBrain
from f1.ers_drs_manager import ERSDRSManager
from core.objective_manager import ObjectiveManager
from telemetry.telemetry_manager import TelemetryManager


def main():
    print("Saul is starting...")

    # --- Core AI ---
    saul = AIRoot()

    # Set initial mode before main loop
    saul.set_mode(AIMode)

    # --- Career Tracker ---
    career = CareerTracker()
    print(f"[Career] Year {career.career_year}, {career.series}, Warmth {career.warmth}")

    # --- Telemetry Manager (UDP polling + F1 state managers) ---
    telemetry_manager = TelemetryManager()
    saul.telemetry_state = telemetry_manager.state

    # Start telemetry thread (50ms loop) - must be after all listeners registered
    telemetry_manager.start_threads()

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
    print("[KeyboardController] Initialized")

    # --- ERSDRSManager ---
    ers_drs_manager = ERSDRSManager(
        telemetry_state=telemetry_manager.state,
        keyboard_controller=keyboard_controller,
        engineer_brain=engineer_brain
    )

    # --- Keyboard Listener (Insert key for pit confirmation) ---
    keyboard_listener = KeyboardListener(on_insert=ers_drs_manager.confirm_pit)
    keyboard_listener.start()

    # Start ERS/DRS thread (50ms loop)
    ers_drs_manager.start_thread()

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

    # --- Main Loop ---
    while True:
        mode_manager.update()
        saul.update()


if __name__ == "__main__":
    main()
