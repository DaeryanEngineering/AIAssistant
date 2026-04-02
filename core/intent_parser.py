# core/intent_parser.py

from dataclasses import dataclass

@dataclass
class Command:
    """
    Command Handling
    """
    intent: str
    parameters: dict
    confidence: float


class IntentParser:
    """
    Intent Parser
    """

    def parse(self, text: str, mode: str) -> Command:
        # Placeholder logic for Phase 3 Step 1
        print(f"[IntentParser] Received text='{text}' in mode='{mode}'")

        # Return a default "unknown" command
        return Command(
            intent="unknown",
            parameters={},
            confidence=0.0
        )
