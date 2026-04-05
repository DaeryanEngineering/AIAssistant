# core/audio_video_manager.py

import threading
import queue
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
        print(f"[AV] Visible -> {visible}")
        self._video.set_visible(visible)

    def is_visible(self) -> bool:
        return self._visible

    # =========================================================
    # ANIMATION CONTROL
    # =========================================================

    def play_animation(self, name: str, *, loop: bool = True) -> None:
        if self._current_animation == name:
            return

        path = AssetMap.get_animation(name)
        self._current_animation = name

        loop_str = " (loop)" if loop else ""
        if self._visible:
            print(f"[AV] Play animation: {name}{loop_str} -> {path}")
            self._video.play(path, loop=loop)
        else:
            print(f"[AV] (hidden) animation requested: {name}{loop_str} -> {path}")

    def stop_animation(self) -> None:
        if self._current_animation:
            resolved = AssetMap.get_animation(self._current_animation)
            print(f"[AV] Stop animation: {self._current_animation} -> {resolved}")

        self._current_animation = None
        self._video.stop()

    # =========================================================
    # STATE HELPER
    # =========================================================

    def set_state(self, state: str) -> None:
        self._state = state
        print(f"[AV] State -> {state}")

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

        # Queue for playback
        self._audio_queue.put((audio, sr, False))  # False = no animation change

    def play_wav_file(self, path: str, return_to_idle: bool = False) -> None:
        """
        Plays a WAV file from disk.
        """
        import soundfile as sf
        audio, sr = sf.read(path, dtype="float32")

        self._audio_queue.put((audio, sr, return_to_idle))

    # =========================================================
    # TTS AUDIO PLAYBACK
    # =========================================================

    def play_tts_audio(self, audio: np.ndarray, sr: int):
        """
        Called by TTSEngine after XTTS synthesis.
        Plays audio from memory (already has the numpy array).
        """
        # Trigger talking animation
        self.on_talk_start()

        # Queue audio for playback (from memory, not from file)
        self._audio_queue.put((audio, sr, True))  # True = return to idle after

    def clear_queue(self):
        """
        Clear pending audio items from the queue.
        Called by TTSEngine for priority events.
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

            audio, sr, return_to_idle = item

            sd.play(audio, sr)
            sd.wait()

            if return_to_idle:
                self.on_talk_end()

            self._audio_queue.task_done()

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
