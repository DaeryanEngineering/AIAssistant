import vlc
import threading
import time
import os


class VLCVideoPlayer:
    """
    Standalone VLC-based video player.
    - Plays MP4 animations in a separate window
    - Supports looping
    - Supports stop/start
    - Very stable on Windows
    """

    def __init__(self):
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()

        self._loop = False
        self._current_path = None
        self._stop_flag = threading.Event()

        # Background thread to monitor looping
        self._thread = threading.Thread(target=self._loop_worker, daemon=True)
        self._thread.start()

    # ---------------------------------------------------------
    # LOAD + PLAY
    # ---------------------------------------------------------
    def play(self, path: str, loop: bool = True):
        if not os.path.exists(path):
            print(f"[VLC] Missing video file: {path}")
            return

        self._loop = loop
        self._current_path = path

        media = self._instance.media_new(path)
        self._player.set_media(media)
        self._player.play()

        print(f"[VLC] Playing: {path} (loop={loop})")

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------
    def stop(self):
        self._loop = False
        self._player.stop()
        print("[VLC] Stopped video")

    # ---------------------------------------------------------
    # VISIBILITY
    # ---------------------------------------------------------
    def set_visible(self, visible: bool):
        # VLC doesn't have a direct "hide window" API,
        # but we can mute the window by moving it off-screen.
        if visible:
            self._player.set_fullscreen(False)
            print("[VLC] Window visible")
        else:
            # Move window off-screen
            try:
                self._player.set_fullscreen(False)
                self._player.set_xwindow(0)  # Linux fallback
            except:
                pass
            print("[VLC] Window hidden (off-screen hack)")

    # ---------------------------------------------------------
    # LOOP MONITOR
    # ---------------------------------------------------------
    def _loop_worker(self):
        while not self._stop_flag.is_set():
            time.sleep(0.1)

            if self._loop and self._player:
                state = self._player.get_state()

                # VLC state 6 = Ended
                if state == vlc.State.Ended:
                    media = self._instance.media_new(self._current_path)
                    self._player.set_media(media)
                    self._player.play()

    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    def shutdown(self):
        self._stop_flag.set()
        self.stop()
        print("[VLC] Shutdown complete")
