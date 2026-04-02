# core/audio_video_manager.py

from .assets import AssetMap

class AudioVideoManager:
    """
    AV Manager
    """

    def __init__(self):
        self._state = "idle"
        self._visible = True
        self._current_animation = None

    # -------------------------
    # Visibility
    # -------------------------

    def set_visible(self, visible: bool) -> None:
        self._visible = visible
        print(f"[AV] Visible -> {visible}")

    def is_visible(self) -> bool:
        return self._visible

    # -------------------------
    # Animation Control
    # -------------------------

    def play_animation(self, name: str, *, loop: bool = True) -> None:
        """
        Video Player
        """
        path = AssetMap.get_animation(name)
        self._current_animation = name

        loop_str = " (loop)" if loop else ""
        if self._visible:
            print(f"[AV] Play animation: {name}{loop_str} -> {path}")
        else:
            print(f"[AV] (hidden) animation requested: {name}{loop_str} -> {path}")

    def stop_animation(self) -> None:
        if self._current_animation:
            resolved = AssetMap.get_animation(self._current_animation)
            print(f"[AV] Stop animation: {self._current_animation} -> {resolved}")
        self._current_animation = None

    # -------------------------
    # State Helper
    # -------------------------

    def set_state(self, state: str) -> None:
        self._state = state
        print(f"[AV] State -> {state}")

    # -------------------------
    # Audio Playback
    # -------------------------

    def play_audio(self, name: str) -> None:
        """
        Audio Player
        """
        path = AssetMap.get_audio(name)
        print(f"[AV] Play audio: {name} -> {path}")
