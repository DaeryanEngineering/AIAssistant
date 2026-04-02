# core/tts_engine.py

import numpy as np
from TTS.api import TTS
from .assets import AssetMap


class TTSEngine:
    """
    Real XTTS-powered TTS Engine
    """

    def __init__(self, av_manager):
        self._av = av_manager

        # Load XTTS v2 model once
        self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    def speak(
        self,
        text: str,
        *,
        radio: bool = False,
        play_beep: bool = False,
        voice_profile: str | None = None,
    ) -> None:

        if not text:
            return

        # -------------------------
        # Radio beep
        # -------------------------
        if play_beep:
            self._av.play_audio("radio_beep")

        # -------------------------
        # Resolve voice profile
        # -------------------------
        profile_key = voice_profile or "default"
        speaker_wav = AssetMap.get_voice(profile_key)

        # -------------------------
        # Debug log
        # -------------------------
        if radio:
            print(f"[TTS][RADIO][{profile_key}] {text}")
        else:
            print(f"[TTS][{profile_key}] {text}")

        print(f"       -> voice profile path: {speaker_wav}")

        # -------------------------
        # XTTS synthesis
        # -------------------------
        audio = self._model.tts(
            text=text,
            speaker_wav=speaker_wav,
            language="en"
        )

        # XTTS returns a Python list → convert to float32 NumPy
        audio = np.array(audio, dtype=np.float32)
        sample_rate = 24000  # XTTS default

        # -------------------------
        # Send to AV Manager
        # -------------------------
        self._av.play_tts_audio(audio, sample_rate)