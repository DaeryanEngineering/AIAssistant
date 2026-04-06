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
        "aimode_idle":      "assets/video/SaulIdle.mp4",
        "aimode_listen":    "assets/video/SaulListen.mp4",
        "aimode_think":     "assets/video/SaulThink.mp4",
        "aimode_talk":      "assets/video/SaulTalk.mp4",

        # F1Mode animations (garage)
        "f1mode_idle":      "assets/video/SaulIdle.mp4",
        "f1mode_listen":    "assets/video/SaulListen.mp4",
        "f1mode_think":     "assets/video/SaulThink.mp4",
        "f1mode_talk":      "assets/video/SaulTalk.mp4",
    }

    # -------------------------
    # AUDIO
    # -------------------------
    audio = {
        # Radio beep
        "radio_beep":       "assets/audio/radio_beep.wav",
    }

    # -------------------------
    # VOICE PROFILES
    # -------------------------
    voices = {
        # Profile Reference
        "default":     "assets/voices/saul.wav",
        "saul_main":   "assets/voices/saul.wav",
        "saul_radio":  "assets/voices/saul.wav",

        # Output file for XTTS synthesis (saved every utterance)
        "saul_output": "assets/voices/saul_output.wav",
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
