# saul_app.py
from core.ai_root import AIRoot
from core.ai_mode import AIMode
from core.f1_mode import F1Mode
from core.f1_engineer_mode import F1EngineerMode
from core.mode_manager import ModeManager, SaulMode
from core.pause_manager import PauseManager
from core.career_tracker import CareerTracker
from udp.telemetry_state import TelemetryState
from core.event_router import EventRouter
from f1.engineer_brain import EngineerBrain
from core.objective_manager import ObjectiveManager


def main():
    print("Saul is starting...")

    # --- Core AI ---
    saul = AIRoot()

    # --- Career Tracker ---
    career = CareerTracker()
    print(f"[Career] Year {career.career_year}, {career.series}, Warmth {career.warmth}")

    # --- Telemetry + Events ---
    telemetry_state = TelemetryState()
    saul.telemetry_state = telemetry_state

    engineer_brain = EngineerBrain(
        response_brain=saul.response_brain,
        tts_engine=saul.tts_engine
    )
    event_router = EventRouter(engineer_brain)
    telemetry_state.register_listener(event_router)
    saul.event_router = event_router

    # --- Objective Manager ---
    objective_manager = ObjectiveManager(
        telemetry_state=telemetry_state,
        engineer_brain=engineer_brain,
        career_tracker=career
    )
    saul.objective_manager = objective_manager

    # --- Pause Manager ---
    saul.pause_manager = PauseManager(
        telemetry_state=telemetry_state,
        input_manager=saul.input_manager,
        text_box_ui=saul.text_box,
        objective_manager=objective_manager
    )

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
        telemetry_state=telemetry_state,
        on_mode_change=on_mode_change
    )

    # --- Main Loop ---
    while True:
        # Update telemetry
        packet = telemetry_state.get_latest_packet()
        if packet:
            telemetry_state.update_from_packet(packet)

        # Update mode manager (auto-switching)
        mode_manager.update()

        # Update Saul
        saul.update()


if __name__ == "__main__":
    main()
