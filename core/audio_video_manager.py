# core/audio_video_manager.py

import threading
import queue
import time
import sounddevice as sd
import numpy as np
from .video_player import VLCVideoPlayer

from .assets import AssetMap


class AudioVideoManager:
    """
    Real Audio + Video Manager
    - Plays radio beeps
    - Plays XTTS audio (from memory, saves WAV to disk)
    - Manages talking/idle animations
    - Threaded audio queue
    """

    def __init__(self):
        self._state = "idle"
        self._visible = True
        self._current_animation = None
        self._pending_tts_animation = None
        self._tts_playing = threading.Event()
        self._video = VLCVideoPlayer()

        # -------------------------
        # Audio queue + thread
        # -------------------------
        self._audio_queue = queue.Queue()
        self._stop_flag = threading.Event()

        self._audio_thread = threading.Thread(
            target=self._audio_worker,
            daemon=True
        )
        self._audio_thread.start()

    # =========================================================
    # VISIBILITY
    # =========================================================

    def set_visible(self, visible: bool) -> None:
        self._visible = visible
        self._video.set_visible(visible)

    def is_visible(self) -> bool:
        return self._visible

    # =========================================================
    # ANIMATION CONTROL
    # =========================================================

    def play_animation(self, name: str, *, loop: bool = True) -> None:
        # Block animation changes while TTS is playing — prevents "idle" from overriding "talk"
        if self._tts_playing.is_set():
            return

        if self._current_animation == name:
            return

        path = AssetMap.get_animation(name)
        self._current_animation = name

        loop_str = " (loop)" if loop else ""
        if self._visible:
            self._video.play(path, loop=loop)

    def stop_animation(self) -> None:
        self._current_animation = None
        self._video.stop()

    # =========================================================
    # STATE HELPER
    # =========================================================

    def set_state(self, state: str) -> None:
        self._state = state

    # =========================================================
    # AUDIO PLAYBACK (RADIO BEEP / WAV FILE)
    # =========================================================

    def play_audio(self, name: str) -> None:
        """
        Plays a short audio asset (radio beep, etc.) by name.
        """
        path = AssetMap.get_audio(name)

        # Load WAV file
        import soundfile as sf
        audio, sr = sf.read(path, dtype="float32")

        # Queue for playback (False = no animation change, None = no animation)
        self._audio_queue.put((audio, sr, False, None))

    def play_wav_file(self, path: str, return_to_idle: bool = False) -> None:
        """
        Plays a WAV file from disk.
        """
        import soundfile as sf
        audio, sr = sf.read(path, dtype="float32")

        self._audio_queue.put((audio, sr, return_to_idle, None))

    # =========================================================
    # TTS AUDIO PLAYBACK
    # =========================================================

    def play_tts_audio(self, audio: np.ndarray, sr: int, animation: str | None = None):
        """
        Called by TTSCache after XTTS synthesis.
        Plays audio from memory (already has the numpy array).
        Animation is triggered in the audio worker right before playback starts.
        """
        self._audio_queue.put((audio, sr, True, animation))

    def clear_queue(self):
        """
        Clear pending audio items from the queue.
        Called by TTSCache for priority events.
        """
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
                self._audio_queue.task_done()
            except queue.Empty:
                break

    # =========================================================
    # AUDIO THREAD WORKER
    # =========================================================

    def _audio_worker(self):
        while not self._stop_flag.is_set():
            item = self._audio_queue.get()
            if item is None:
                break

            if len(item) == 3:
                audio, sr, return_to_idle = item
                animation = None
            else:
                audio, sr, return_to_idle, animation = item

            # Mark TTS as playing — blocks animation changes until done
            if animation:
                self._tts_playing.set()

            # Trigger animation right BEFORE audio plays (guaranteed sync)
            if animation:
                self._play_animation_internal(animation)

            # Play audio and wait for it to finish (prevents cutting off)
            sd.play(audio, sr)
            stream = sd.get_stream()
            while stream.active:
                time.sleep(0.01)

            # Return to idle after audio finishes
            if return_to_idle:
                self._play_animation_internal("idle")

            # Release flag — animations can now change
            self._tts_playing.clear()
            self._audio_queue.task_done()

    def _play_animation_internal(self, name: str):
        """Internal animation player (no state tracking)."""
        if name == "idle":
            self._current_animation = None
            self._video.stop()
            return

        if self._current_animation == name:
            return

        path = AssetMap.get_animation(name)
        self._current_animation = name
        if self._visible:
            self._video.play(path, loop=False)

    # =========================================================
    # TALKING / IDLE ANIMATION HOOKS
    # =========================================================

    def on_talk_start(self):
        # Modes handle their own animation transitions.
        # This hook is kept for future extensibility but does not
        # override the mode's animation choice.
        pass

    def on_talk_end(self):
        # Modes handle their own animation transitions.
        # This hook is kept for future extensibility but does not
        # override the mode's animation choice.
        pass

    # =========================================================
    # SHUTDOWN
    # =========================================================

    def shutdown(self):
        self._stop_flag.set()
        self._audio_queue.put(None)
        self._audio_thread.join()
        self._video.shutdown()
