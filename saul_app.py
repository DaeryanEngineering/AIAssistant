# saul_app.py
from udp.telemetry_state import TelemetryState
from core.event_router import EventRouter
from f1.engineer_brain import EngineerBrain
from core.ai_root import AIRoot
from core.ai_mode import AIMode
from core.f1_mode import F1Mode
from core.f1_engineer_mode import F1EngineerMode
from core.mode_manager import ModeManager
from core.pause_manager import PauseManager

def main():
    print("Saul is starting...")

    saul = AIRoot()

    saul.pause_manager = PauseManager(
        telemetry_state=telemetry_state,
        input_manager=saul.input_manager,
        text_box_ui=saul.text_box
    )

    # --- Event System ---
    telemetry_state = TelemetryState()
    engineer_brain = EngineerBrain(
        response_brain=saul.response_brain,
        tts_engine=saul.tts_engine
    )
    event_router = EventRouter(engineer_brain)

    telemetry_state.register_listener(event_router)

    saul.telemetry_state = telemetry_state
    saul.event_router = event_router

    # --- Mode Manager (NEW) ---
    def on_mode_change(new_mode):
        # Saul switches modes automatically
        if new_mode == new_mode.AI:
            saul.set_mode(AIMode)
        elif new_mode == new_mode.F1:
            saul.set_mode(F1Mode)
        elif new_mode == new_mode.ENGINEER:
            saul.set_mode(F1EngineerMode)
        elif new_mode == new_mode.PAUSED:
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
