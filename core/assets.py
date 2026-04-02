# core/assets.py

class AssetMap:
    """
    Asset Map
    """

    # -------------------------
    # ANIMATIONS
    # -------------------------
    animations = {
        # AIMode animations
        "aimode_idle":      "assets/animations/aimode/idle.mp4",
        "aimode_listen":    "assets/animations/aimode/listen.mp4",
        "aimode_think":     "assets/animations/aimode/think.mp4",
        "aimode_talk":      "assets/animations/aimode/talk.mp4",

        # F1Mode animations (garage)
        "f1mode_idle":      "assets/animations/f1mode/idle.mp4",
        "f1mode_listen":    "assets/animations/f1mode/listen.mp4",
        "f1mode_think":     "assets/animations/f1mode/think.mp4",
        "f1mode_talk":      "assets/animations/f1mode/talk.mp4",
    }

    # -------------------------
    # AUDIO
    # -------------------------
    audio = {
        # Radio beep
        "radio_beep":       "assets/audio/radio/radio_beep.wav",

        # Future: UI sounds, ambient, etc.
        "ui_click":         "assets/audio/ui/click.wav",
        "garage_ambience":  "assets/audio/ambient/garage.wav",
    }

    # -------------------------
    # VOICE PROFILES
    # -------------------------
    voices = {
        # Main conversational voice
        "saul_main":        "assets/voices/saul_main.pt",

        # Garage technical voice (optional)
        "saul_garage":      "assets/voices/saul_garage.pt",

        # Radio voice (clean EQ applied later)
        "saul_radio":       "assets/voices/saul_radio.pt",
    }

    @classmethod
    def get_animation(cls, name: str) -> str:
        return cls.animations.get(name, f"[Missing animation: {name}]")

    @classmethod
    def get_audio(cls, name: str) -> str:
        return cls.audio.get(name, f"[Missing audio: {name}]")

    @classmethod
    def get_voice(cls, name: str) -> str:
        return cls.voices.get(name, f"[Missing voice profile: {name}]")
