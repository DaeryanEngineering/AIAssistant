# core/tts_engine.py

import wave
import numpy as np
from TTS.api import TTS
from .assets import AssetMap


class TTSEngine:
    """
    Real XTTS-powered TTS Engine.
    Saves synthesized audio to saul_output.wav, then plays from memory.
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

        # XTTS returns a Python list -> convert to float32 NumPy
        audio = np.array(audio, dtype=np.float32)
        sample_rate = 24000  # XTTS default

        # -------------------------
        # Save to saul_output.wav (archival)
        # -------------------------
        output_path = AssetMap.get_voice("saul_output")
        self._save_wav(output_path, audio, sample_rate)
        print(f"       -> saved to: {output_path}")

        # -------------------------
        # Send to AV Manager (play from memory)
        # -------------------------
        self._av.play_tts_audio(audio, sample_rate)

    def _save_wav(self, path: str, audio: np.ndarray, sample_rate: int):
        """
        Save numpy audio array to WAV file.
        """
        # Convert float32 [-1, 1] to int16
        audio_int16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)          # Mono
            wf.setsampwidth(2)          # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())
