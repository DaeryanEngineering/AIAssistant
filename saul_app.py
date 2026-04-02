# saul_app.py

from core.ai_root import AIRoot
from core.ai_mode import AIMode
from core.f1_mode import F1Mode
from core.f1_engineer_mode import F1EngineerMode

def simulate_ptt_cycle(saul: AIRoot, mode_name: str):
    print(f"\n--- Simulating PTT cycle in {mode_name} ---")
    # Press PTT
    saul.input_manager.set_ptt_state(True)
    saul.update()
    # Release PTT
    saul.input_manager.set_ptt_state(False)
    saul.update()

def main():
    print("Saul is starting...")

    saul = AIRoot()

    # AIMode: assistant away from F1
    saul.set_mode(AIMode)
    simulate_ptt_cycle(saul, "AIMode")

    # F1Mode: garage engineer
    saul.set_mode(F1Mode)
    simulate_ptt_cycle(saul, "F1Mode")

    # F1EngineerMode: on-track radio engineer
    saul.set_mode(F1EngineerMode)
    simulate_ptt_cycle(saul, "F1EngineerMode")

if __name__ == "__main__":
    main()
