# saul_app.py

from core.ai_root import AIRoot
from core.ai_mode import AIMode
from core.f1_engineer_mode import F1EngineerMode

def main():
    print("Saul is starting...")

    saul = AIRoot()

    # Test conversational mode
    saul.set_mode(AIMode)
    for _ in range(3):
        saul.update()

    # Test F1 engineer mode
    saul.set_mode(F1EngineerMode)
    for _ in range(3):
        saul.update()

if __name__ == "__main__":
    main()
