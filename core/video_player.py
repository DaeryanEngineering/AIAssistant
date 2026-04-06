import vlc
import threading
import time
import os
import tkinter as tk


class VLCVideoPlayer:
    """
    VLC-based video player embedded in a borderless Tkinter window.
    - Pure black background is transparent (floating character effect)
    - Always-on-top, positioned bottom-right
    - Supports looping, stop/start
    """

    def __init__(self, width: int = 640, height: int = 720, x: int = 1260, y: int = 340):
        self._width = width
        self._height = height
        self._x = x
        self._y = y

        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()

        self._loop = False
        self._current_path = None
        self._stop_flag = threading.Event()

        # Tkinter window state
        self._tk_root = None
        self._toplevel = None
        self._canvas = None
        self._hwnd_ready = threading.Event()

        # Spawn Tkinter thread
        self._thread = threading.Thread(target=self._spawn_tk, daemon=True, name="VLCWindow")
        self._thread.start()

        # Wait for the Tkinter window to be ready (up to 5 seconds)
        self._hwnd_ready.wait(timeout=5)

        # Background thread to monitor looping
        self._loop_thread = threading.Thread(target=self._loop_worker, daemon=True)
        self._loop_thread.start()

    # ---------------------------------------------------------
    # TKINTER WINDOW SPAWN
    # ---------------------------------------------------------
    def _spawn_tk(self):
        try:
            # Hidden root (required for Toplevel)
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()

            # Floating toplevel
            self._toplevel = tk.Toplevel(self._tk_root)
            self._toplevel.overrideredirect(True)
            self._toplevel.attributes('-topmost', True)
            self._toplevel.attributes('-transparentcolor', 'black')
            self._toplevel.configure(bg='black')
            self._toplevel.resizable(False, False)
            self._toplevel.geometry(f"{self._width}x{self._height}+{self._x}+{self._y}")

            # Start hidden
            self._toplevel.withdraw()

            # Canvas for VLC embedding
            self._canvas = tk.Canvas(self._toplevel, width=self._width, height=self._height, bg='black', highlightthickness=0)
            self._canvas.pack(fill='both', expand=True)

            # Embed VLC player into canvas
            self._player.set_hwnd(self._canvas.winfo_id())

            # Signal ready
            self._hwnd_ready.set()

            # Run event loop
            self._toplevel.mainloop()
        except Exception as e:
            print(f"[VLC] Failed to create Tkinter window: {e}")
            self._hwnd_ready.set()

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

        # Re-embed VLC into canvas (needed after each new media)
        if self._canvas:
            self._player.set_hwnd(self._canvas.winfo_id())

        self._player.play()

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------
    def stop(self):
        self._loop = False
        self._player.stop()

    # ---------------------------------------------------------
    # VISIBILITY
    # ---------------------------------------------------------
    def set_visible(self, visible: bool):
        if not self._toplevel:
            return

        try:
            if visible:
                self._toplevel.deiconify()
            else:
                self._toplevel.withdraw()
        except Exception as e:
            print(f"[VLC] Could not change visibility: {e}")

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

                    # Re-embed after new media
                    if self._canvas:
                        self._player.set_hwnd(self._canvas.winfo_id())

                    self._player.play()

    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    def shutdown(self):
        self._stop_flag.set()
        self.stop()

        if self._toplevel:
            try:
                self._toplevel.quit()
            except Exception:
                pass

        print("[VLC] Shutdown complete")
