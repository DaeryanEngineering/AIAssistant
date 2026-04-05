# core/tts_engine.py

import wave
import queue
import threading
import numpy as np
from TTS.api import TTS
from .assets import AssetMap


class TTSEngine:
    """
    Real XTTS-powered TTS Engine.
    Non-blocking: speak_async() queues text, daemon thread synthesizes.
    Priority calls clear the queue first (safety, race start, etc.).
    """

    def __init__(self, av_manager):
        self._av = av_manager
        self._queue = queue.Queue()
        self._stop_flag = threading.Event()

        # Load XTTS v2 model once (blocking init — happens at startup)
        self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

        # Start synthesis thread
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def speak_async(
        self,
        text: str,
        *,
        priority: bool = False,
        radio: bool = False,
        play_beep: bool = False,
        voice_profile: str | None = None,
    ) -> None:
        """
        Non-blocking: queues text for synthesis.
        If priority=True, clears pending queue first.
        """
        if not text:
            return

        if priority:
            # Clear pending audio queue
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
            # Clear AV manager audio queue
            self._av.clear_queue()

        self._queue.put((text, radio, play_beep, voice_profile))

    def _worker(self):
        """
        Daemon thread: pops text from queue, synthesizes, queues to AV.
        """
        while not self._stop_flag.is_set():
            try:
                text, radio, play_beep, voice_profile = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if not text:
                self._queue.task_done()
                continue

            # Radio beep
            if play_beep:
                self._av.play_audio("radio_beep")

            # Resolve voice profile
            profile_key = voice_profile or "default"
            speaker_wav = AssetMap.get_voice(profile_key)

            # Debug log
            if radio:
                print(f"[TTS][RADIO][{profile_key}] {text}")
            else:
                print(f"[TTS][{profile_key}] {text}")
            print(f"       -> voice profile path: {speaker_wav}")

            try:
                # XTTS synthesis
                audio = self._model.tts(
                    text=text,
                    speaker_wav=speaker_wav,
                    language="en"
                )

                # Convert to float32 NumPy
                audio = np.array(audio, dtype=np.float32)
                sample_rate = 24000

                # Save to saul_output.wav (archival)
                output_path = AssetMap.get_voice("saul_output")
                self._save_wav(output_path, audio, sample_rate)
                print(f"       -> saved to: {output_path}")

                # Send to AV Manager (play from memory)
                self._av.play_tts_audio(audio, sample_rate)
            except Exception as e:
                print(f"[TTS] Synthesis error: {e}")

            self._queue.task_done()

    def _save_wav(self, path: str, audio: np.ndarray, sample_rate: int):
        """
        Save numpy audio array to WAV file.
        """
        audio_int16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

    def shutdown(self):
        self._stop_flag.set()
        self._queue.put(("", False, False, None))  # Sentinel
        self._thread.join(timeout=5)
