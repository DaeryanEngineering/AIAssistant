# core/tts_engine.py

from .audio_video_manager import AudioVideoManager
from .assets import AssetMap

class TTSEngine:
    """
    TTS Engine
    """

    def __init__(self, av_manager: AudioVideoManager):
        self._av = av_manager

    def speak(
        self,
        text: str,
        *,
        radio: bool = False,
        play_beep: bool = False,
        voice_profile: str | None = None,
    ) -> None:
        """
        Asset Wiring 
        """

        # -------------------------
        # Radio beep
        # -------------------------
        if play_beep:
            # Use asset key, not filename
            self._av.play_audio("radio_beep")

        # -------------------------
        # Resolve voice profile
        # -------------------------
        profile_key = voice_profile or "default"
        profile_path = AssetMap.get_voice(profile_key)

        # -------------------------
        # Log output
        # -------------------------
        if radio:
            print(f"[TTS][RADIO][{profile_key}] {text}")
            print(f"       -> voice profile path: {profile_path}")
        else:
            print(f"[TTS][{profile_key}] {text}")
            print(f"       -> voice profile path: {profile_path}")